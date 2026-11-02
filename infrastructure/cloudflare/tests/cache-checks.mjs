import assert from 'node:assert/strict';
import { createHmac } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';

import worker from '../caching-worker.mjs';

const fixture = JSON.parse(
    await readFile(
        new URL(
            '../../../rca/personalisation/tests/fixtures/anonymous_cache.json',
            import.meta.url,
        ),
        'utf8',
    ),
);
const secret = fixture.secret;
const markerName = '__Host-rca-anonymous';

function token(
    session,
    expires = Math.floor(Date.now() / 1000) + 300,
    host = 'www.rca.ac.uk',
) {
    const signature = createHmac('sha256', secret)
        .update(`rca-anonymous-cache:v1\n${host}\n${session}\n${expires}`)
        .digest('hex');
    return `v1.${expires}.${signature}`;
}

function sharedPage(body = 'Shared public HTML', headers = {}) {
    return new Response(body, {
        headers: {
            'Content-Type': 'text/html; charset=utf-8',
            'Cache-Control': 'public, s-maxage=600',
            'X-RCA-Cacheable': 'public-v1',
            'Vary': 'Cookie, origin',
            ...headers,
        },
    });
}

function setup(origin = () => sharedPage()) {
    const entries = new Map();
    const requests = [];
    const writes = [];
    const cacheKey = (request) =>
        `${request.url}|${request.headers.get('Cookie')}|${request.headers.get('Accept-Encoding')}`;
    globalThis.caches = {
        default: {
            async match(request) {
                // Include Cookie to catch accidental visitor-specific cache keys.
                return entries.get(cacheKey(request))?.clone();
            },
            async put(request, response) {
                assert.equal(request.method, 'GET');
                assert.equal(response.headers.get('Set-Cookie'), null);
                assert.doesNotMatch(
                    response.headers.get('Cache-Control'),
                    /private|no-store/,
                );
                entries.set(cacheKey(request), response.clone());
            },
        },
    };
    globalThis.fetch = async (request) => {
        requests.push(request);
        return origin(request);
    };
    return {
        requests,
        entries,
        async visit(
            path = '/',
            headers = {},
            env = { PERSONALISATION_CACHE_SIGNING_KEY: secret },
        ) {
            const response = await worker.fetch(
                new Request(`https://www.rca.ac.uk${path}`, { headers }),
                env,
                { waitUntil: (promise) => writes.push(promise) },
            );
            await Promise.all(writes.splice(0));
            return response;
        },
    };
}

test('first visitor warms cache; CTA session then uses the same cached HTML', async () => {
    const app = setup();
    assert.equal((await app.visit()).headers.get('X-RCA-Cache-Status'), 'MISS');
    const returning = await app.visit('/', {
        Cookie: `sessionid=anonymous-a; ${markerName}=${token('anonymous-a')}`,
    });
    assert.equal(returning.headers.get('X-RCA-Cache-Status'), 'HIT');
    assert.equal(await returning.text(), 'Shared public HTML');
    assert.equal(app.requests.length, 1);
    const otherVisitor = await app.visit('/', {
        Cookie: `sessionid=anonymous-b; ${markerName}=${token('anonymous-b')}; analytics=other`,
    });
    assert.equal(otherVisitor.headers.get('X-RCA-Cache-Status'), 'HIT');
    assert.equal(app.requests.length, 1);
});

test('Python-generated signature is accepted by Worker', async () => {
    const app = setup();
    const response = await app.visit('/', {
        Cookie: `sessionid=${fixture.session}; ${markerName}=${fixture.token}`,
    });
    assert.equal(response.headers.get('X-RCA-Cache-Status'), 'MISS');
    assert.equal(app.entries.size, 1);
});

test('missing, expired, forged, wrong-host and mismatched-session markers bypass a warm cache', async () => {
    const app = setup();
    await app.visit();
    const badMarkers = [
        '',
        'v1.2000000000.' + '0'.repeat(64),
        token('anonymous', Math.floor(Date.now() / 1000) - 1),
        token('another-session'),
        token('anonymous', undefined, 'beta.rca.ac.uk'),
        token('anonymous') + '.extra',
    ];
    for (const marker of badMarkers) {
        const response = await app.visit('/', {
            Cookie: `sessionid=anonymous; ${markerName}=${marker}`,
        });
        assert.equal(
            response.headers.get('X-RCA-Cache-Status'),
            'BYPASS-SESSION',
        );
    }
    assert.equal(app.requests.length, badMarkers.length + 1);
});

test('login session rotation invalidates the old anonymous proof', async () => {
    const app = setup(() => sharedPage('Origin response'));
    await app.visit();
    const response = await app.visit('/', {
        Cookie: `sessionid=new-authenticated-session; ${markerName}=${token('old-anonymous-session')}`,
    });
    assert.equal(response.headers.get('X-RCA-Cache-Status'), 'BYPASS-SESSION');
    assert.equal(app.requests.length, 2);
});

test('duplicate session or marker cookies cannot bypass classification', async () => {
    const app = setup();
    await app.visit();
    for (const cookie of [
        `sessionid=anonymous; sessionid=authenticated; ${markerName}=${token('anonymous')}`,
        `sessionid=anonymous; ${markerName}=${token('anonymous')}; ${markerName}=other`,
        `sessionid=; ${markerName}=${token('anonymous')}`,
    ]) {
        const response = await app.visit('/', { Cookie: cookie });
        assert.equal(
            response.headers.get('X-RCA-Cache-Status'),
            'BYPASS-SESSION',
        );
    }
});

test('CTA, authentication, API and private routes bypass even with a valid proof', async () => {
    const app = setup();
    const headers = {
        Cookie: `sessionid=anonymous; ${markerName}=${token('anonymous')}`,
    };
    for (const path of [
        '/personalisation/ctas/123/',
        '/admin/',
        '/django-admin/',
        '/login/azuread-tenant-oauth2/',
        '/complete/azuread-tenant-oauth2/',
        '/logout/',
        '/disconnect/azuread-tenant-oauth2/',
        '/api/v3/pages/',
        '/register-your-interest/',
        '/documents2/123/',
    ]) {
        const response = await app.visit(path, headers);
        assert.equal(
            response.headers.get('X-RCA-Cache-Status'),
            'BYPASS-ROUTE',
            path,
        );
    }
    assert.equal(app.entries.size, 0);
});

test('non-GET, authorization, origin and AJAX requests bypass a warm cache', async () => {
    const app = setup();
    await app.visit();
    for (const method of ['POST', 'HEAD', 'PUT']) {
        const response = await worker.fetch(
            new Request('https://www.rca.ac.uk/', { method }),
            { PERSONALISATION_CACHE_SIGNING_KEY: secret },
            { waitUntil: () => assert.fail('No cache write expected') },
        );
        assert.equal(
            response.headers.get('X-RCA-Cache-Status'),
            'BYPASS-REQUEST',
        );
    }
    for (const headers of [
        { Authorization: 'Bearer example' },
        { Origin: 'https://example.com' },
        { 'X-Requested-With': 'XMLHttpRequest' },
        { Range: 'bytes=0-3' },
        { 'Cache-Control': 'no-cache' },
    ]) {
        const response = await app.visit('/', headers);
        assert.equal(
            response.headers.get('X-RCA-Cache-Status'),
            'BYPASS-REQUEST',
        );
    }
});

test('private, cookie-setting and unapproved responses are never stored', async () => {
    for (const headers of [
        { 'Cache-Control': 'private, no-store' },
        { 'Set-Cookie': 'sessionid=private; Secure; HttpOnly' },
        { 'X-RCA-Cacheable': 'no' },
        { 'Content-Type': 'application/json' },
        { Vary: '*' },
        { Vary: 'User-Agent' },
        { 'Cache-Control': 'public, no-cache' },
    ]) {
        const app = setup(() => sharedPage('Private response', headers));
        assert.equal(
            (await app.visit()).headers.get('X-RCA-Cache-Status'),
            'BYPASS-RESPONSE',
        );
        await app.visit();
        assert.equal(app.requests.length, 2);
        assert.equal(app.entries.size, 0);
    }
});

test('old cache entries without the application opt-in are not served', async () => {
    const app = setup();
    app.entries.set(
        'https://www.rca.ac.uk/|null|null',
        sharedPage('Old content', { 'X-RCA-Cacheable': '' }),
    );
    const response = await app.visit();
    assert.equal(response.headers.get('X-RCA-Cache-Status'), 'MISS');
    assert.equal(await response.text(), 'Shared public HTML');
});

test('missing signing secret disables the new cache path', async () => {
    const app = setup();
    await app.visit();
    const response = await app.visit('/', {}, {});
    assert.equal(response.headers.get('X-RCA-Cache-Status'), 'BYPASS-CONFIG');
    assert.equal(app.requests.length, 2);
});

test('RCA cache read/write failures fall back to serving the page', async () => {
    const app = setup();
    globalThis.caches.default.match = async () => {
        throw new Error('cache unavailable');
    };
    globalThis.caches.default.put = async () => {
        throw new Error('cache unavailable');
    };
    const response = await app.visit();
    assert.equal(response.status, 200);
    assert.equal(await response.text(), 'Shared public HTML');
    assert.equal(app.requests.length, 1);
});

test('other RCA hostnames retain the original session bypass', async () => {
    const app = setup();
    const response = await worker.fetch(
        new Request('https://beta.rca.ac.uk/', {
            headers: {
                Cookie: `sessionid=anonymous; ${markerName}=${token('anonymous')}`,
            },
        }),
        { PERSONALISATION_CACHE_SIGNING_KEY: secret },
        { waitUntil: () => assert.fail('No cache write expected') },
    );
    assert.equal(response.headers.get('X-RCA-Cache-Status'), null);
    assert.equal(app.requests.length, 1);
});

test('tracking parameters are stripped but content query parameters stay separate', async () => {
    const app = setup();
    await app.visit('/?utm_source=example&category=art');
    const response = await app.visit('/?category=art');
    assert.equal(response.headers.get('X-RCA-Cache-Status'), 'HIT');
    assert.equal(app.requests[0].url, 'https://www.rca.ac.uk/?category=art');
    const different = await app.visit('/?category=design');
    assert.equal(different.headers.get('X-RCA-Cache-Status'), 'MISS');
});

test('cache key preserves the negotiated encoding while sharing across cookies', async () => {
    const app = setup((request) =>
        sharedPage(request.headers.get('Accept-Encoding')),
    );
    await app.visit('/', { 'Accept-Encoding': 'br' });
    const gzip = await app.visit('/', { 'Accept-Encoding': 'gzip' });
    assert.equal(gzip.headers.get('X-RCA-Cache-Status'), 'MISS');
    assert.equal(await gzip.text(), 'gzip');
    const brotli = await app.visit('/', {
        'Accept-Encoding': 'br',
        'Cookie': `sessionid=anonymous; ${markerName}=${token('anonymous')}`,
    });
    assert.equal(brotli.headers.get('X-RCA-Cache-Status'), 'HIT');
    assert.equal(await brotli.text(), 'br');
});

test('legacy hostnames still cache no-session requests with their original policy', async () => {
    const app = setup();
    const writes = [];
    for (let i = 0; i < 2; i += 1) {
        const response = await worker.fetch(
            new Request('https://beta.rca.ac.uk/'),
            {},
            { waitUntil: (promise) => writes.push(promise) },
        );
        await Promise.all(writes.splice(0));
        assert.equal(response.status, 200);
        assert.equal(response.headers.get('X-RCA-Cache-Status'), null);
    }
    assert.equal(app.requests.length, 1);
});
