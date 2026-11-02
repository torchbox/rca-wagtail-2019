// NOTE: A 'Cache Level' page rule set to 'Cache Everything' will
// prevent private cookie cache skipping from working, as it is
// applied after this worker runs.

// When any cookie in this list is present in the request, cache will be skipped
const PRIVATE_COOKIES = ['sessionid'];

// These querystring keys are stripped from the request as they are generally not
// needed by the origin.
const STRIP_QUERYSTRING_KEYS = [
    'utm_source',
    'utm_campaign',
    'utm_medium',
    'utm_term',
    'utm_content',
    'gclid',
    'fbclid',
    'dm_i', // DotDigital
    'msclkid',
    'al_applink_data', // Meta outbound app links

    // https://docs.flying-press.com/cache/ignore-query-strings
    'age-verified',
    'ao_noptimize',
    'usqp',
    'cn-reloaded',
    'sscid',
    'ef_id',
    '_bta_tid',
    '_bta_c',
    'fb_action_ids',
    'fb_action_types',
    'fb_source',
    '_ga',
    'adid',
    '_gl',
    'gclsrc',
    'gdfms',
    'gdftrk',
    'gdffi',
    '_ke',
    'trk_contact',
    'trk_msg',
    'trk_module',
    'trk_sid',
    'mc_cid',
    'mc_eid',
    'mkwid',
    'pcrid',
    'mtm_source',
    'mtm_medium',
    'mtm_campaign',
    'mtm_keyword',
    'mtm_cid',
    'mtm_content',
    'epik',
    'pp',
    'pk_source',
    'pk_medium',
    'pk_campaign',
    'pk_keyword',
    'pk_cid',
    'pk_content',
    'redirect_log_mongo_id',
    'redirect_mongo_id',
    'sb_referer_host',
];

// If this is true, the querystring keys stripped from the request will be
// addeed to any Location header served by a redirect.
const REPLACE_STRIPPED_QUERYSTRING_ON_REDIRECT_LOCATION = false;

// If this is true, querystring key are stripped if they have no value eg. ?foo
// Disabled by default, but highly recommended
const STRIP_VALUELESS_QUERYSTRING_KEYS = false;

// Only these status codes should be considered cacheable
// (from https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.4)
const CACHABLE_HTTP_STATUS_CODES = [200, 203, 206, 300, 301, 410];

const RCA_HOSTNAME = 'www.rca.ac.uk';
const MARKER_COOKIE = '__Host-rca-anonymous';
const PRIVATE_PATHS = [
    '/admin',
    '/django-admin',
    '/personalisation',
    '/login',
    '/complete',
    '/disconnect',
    '/logout',
    '/api',
    '/documents2',
    '/register-your-interest',
];
const SHARED_VARY_HEADERS = new Set([
    'cookie',
    'origin',
    'accept-encoding',
    'x-requested-with',
    'x-forwarded-proto',
]);

function withStatus(response, status) {
    const result = new Response(response.body, response);
    result.headers.set('X-RCA-Cache-Status', status);
    return result;
}

function isSharedPage(response) {
    const control = response.headers.get('Cache-Control') || '';
    const vary = response.headers.get('Vary') || '';
    return (
        response.status === 200 &&
        response.headers.get('X-RCA-Cacheable') === 'public-v1' &&
        (response.headers.get('Content-Type') || '')
            .toLowerCase()
            .startsWith('text/html') &&
        !response.headers.has('Set-Cookie') &&
        /(?:^|,)\s*public\s*(?:,|$)/i.test(control) &&
        !/(?:^|,)\s*(?:private|no-store|no-cache)\s*(?:=|,|$)/i.test(control) &&
        vary
            .split(',')
            .every(
                (name) =>
                    !name.trim() ||
                    SHARED_VARY_HEADERS.has(name.trim().toLowerCase()),
            )
    );
}

async function hasAnonymousSession(request, secret) {
    const cookies = (request.headers.get('Cookie') || '').split(';');
    const sessions = [];
    const markers = [];
    for (const cookie of cookies) {
        const equals = cookie.indexOf('=');
        const name = (equals < 0 ? cookie : cookie.slice(0, equals)).trim();
        const value = equals < 0 ? '' : cookie.slice(equals + 1).trim();
        if (name === 'sessionid') sessions.push(value);
        if (name === MARKER_COOKIE) markers.push(value);
    }
    if (!sessions.length) return true;
    if (sessions.length !== 1 || markers.length !== 1 || !sessions[0])
        return false;

    const match = /^v1\.(\d{10})\.([a-f0-9]{64})$/.exec(markers[0]);
    if (!match || Number(match[1]) <= Math.floor(Date.now() / 1000))
        return false;

    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
        'raw',
        encoder.encode(secret),
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['verify'],
    );
    const signature = Uint8Array.from(match[2].match(/../g), (pair) =>
        parseInt(pair, 16),
    );
    return crypto.subtle.verify(
        'HMAC',
        key,
        signature,
        encoder.encode(
            `rca-anonymous-cache:v1\n${RCA_HOSTNAME}\n${sessions[0]}\n${match[1]}`,
        ),
    );
}

async function serveRCAPage(request, env, ctx) {
    const bypass = async (reason) => withStatus(await fetch(request), reason);
    const url = new URL(request.url);
    if (
        url.protocol !== 'https:' ||
        request.method !== 'GET' ||
        ['Authorization', 'Origin', 'X-Requested-With', 'Range'].some((name) =>
            request.headers.has(name),
        ) ||
        /(?:no-cache|no-store)/i.test(
            request.headers.get('Cache-Control') || '',
        ) ||
        /no-cache/i.test(request.headers.get('Pragma') || '')
    )
        return bypass('BYPASS-REQUEST');

    // Decode before checking: Wagtail/Django route on the decoded URL path.
    let path;
    try {
        path = decodeURIComponent(url.pathname).toLowerCase();
    } catch {
        return bypass('BYPASS-REQUEST');
    }
    if (
        PRIVATE_PATHS.some(
            (prefix) => path === prefix || path.startsWith(`${prefix}/`),
        )
    ) {
        return bypass('BYPASS-ROUTE');
    }

    const secret = env.PERSONALISATION_CACHE_SIGNING_KEY;
    if (
        typeof secret !== 'string' ||
        new TextEncoder().encode(secret).length < 32
    ) {
        return bypass('BYPASS-CONFIG');
    }
    let anonymous;
    try {
        anonymous = await hasAnonymousSession(request, secret);
    } catch {
        return bypass('BYPASS-SESSION');
    }
    if (!anonymous) return bypass('BYPASS-SESSION');

    // Normalise only the cache key; keep visitor cookies on the origin request.
    // Only explicit public-v1 HTML is stored under this visitor-independent key.
    const headers = new Headers();
    if (request.headers.has('Accept-Encoding')) {
        headers.set('Accept-Encoding', request.headers.get('Accept-Encoding'));
    }
    const key = new Request(url, { method: 'GET', headers });
    const cache = caches.default;
    try {
        const cached = await cache.match(key);
        if (cached && isSharedPage(cached)) return withStatus(cached, 'HIT');
    } catch {
        // Cache availability must not prevent the origin serving a page.
    }
    const response = await fetch(request);
    if (!isSharedPage(response)) return withStatus(response, 'BYPASS-RESPONSE');
    ctx.waitUntil(cache.put(key, response.clone()).catch(() => {}));
    return withStatus(response, 'MISS');
}

export default {
    async fetch(request, env, ctx) {
        if (new URL(request.url).hostname === RCA_HOSTNAME) {
            const [normalised] = stripQuerystring(request);
            return serveRCAPage(normalised, env, ctx);
        }
        return main({
            request,
            waitUntil: (promise) => ctx.waitUntil(promise),
        });
    },
};

async function main(event) {
    const cache = caches.default;
    let request = event.request;
    let strippedParams;
    [request, strippedParams] = stripQuerystring(request);

    if (!requestIsCachable(request)) {
        // If the request isn't cacheable, return a Response directly from the origin.
        return fetch(request);
    }

    const cachingRequest = getCachingRequest(request);
    let response = await cache.match(cachingRequest);

    if (!response) {
        // If we didn't get a response from the cache, fetch one from the origin
        // and put it in the cache.
        response = await fetch(request);
        if (responseIsCachable(response)) {
            event.waitUntil(cache.put(cachingRequest, response.clone()));
        }
    }

    if (REPLACE_STRIPPED_QUERYSTRING_ON_REDIRECT_LOCATION) {
        response = replaceStrippedQsOnRedirectResponse(
            response,
            strippedParams,
        );
    }

    return response;
}

/*
 * Cacheability Utilities
 */
function requestIsCachable(request) {
    /*
     * Given a Request, determine if it should be cached.
     * Currently the only factor here is whether a private cookie is present.
     */
    return !hasPrivateCookie(request);
}

function responseIsCachable(response) {
    /*
     * Given a Response, determine if it should be cached.
     * Currently the only factor here is whether the status code is cachable.
     */
    return CACHABLE_HTTP_STATUS_CODES.includes(response.status);
}

function getCachingRequest(request) {
    /**
     * When needed, modify a request for use as the cache key.
     *
     * Note: Modifications to this request are not sent upstream.
     */
    return new Request(new URL(request.url), request);
}

/*
 * Request Utilities
 */
function stripQuerystring(request) {
    /**
     * Given a Request, return a new Request with the ignored or blank querystring keys stripped out,
     * along with an object representing the stripped values.
     */
    const url = new URL(request.url);

    const stripKeys = STRIP_QUERYSTRING_KEYS.filter((v) =>
        url.searchParams.has(v),
    );

    let strippedParams = {};

    if (stripKeys.length) {
        stripKeys.reduce((acc, key) => {
            acc[key] = url.searchParams.getAll(key);
            url.searchParams.delete(key);
            return acc;
        }, strippedParams);
    }

    if (STRIP_VALUELESS_QUERYSTRING_KEYS) {
        // Strip query params without values to avoid unnecessary cache misses
        for (const [key, value] of url.searchParams.entries()) {
            if (!value) {
                url.searchParams.delete(key);
                strippedParams[key] = '';
            }
        }
    }

    return [new Request(url, request), strippedParams];
}

function hasPrivateCookie(request) {
    /*
     * Given a Request, determine if one of the 'private' cookies are present.
     */
    const cookieHeader = request.headers.get('Cookie');
    if (!cookieHeader) {
        return false;
    }

    const requestCookieNames = cookieHeader
        .split(';')
        .map((cookie) => cookie.split('=')[0].trim());

    return PRIVATE_COOKIES.some((privateCookieName) =>
        requestCookieNames.includes(privateCookieName),
    );
}

/**
 * Response Utilities
 */

function replaceStrippedQsOnRedirectResponse(response, strippedParams) {
    /**
     * Given an existing Response, and an object of stripped querystring keys,
     * determine if the response is a redirect.
     * If it is, add the stripped querystrings to the location header.
     * This allows us to persist tracking querystrings (like UTM) over redirects.
     */
    response = new Response(response.body, response);

    if ([301, 302].includes(response.status)) {
        const locationHeaderValue = response.headers.get('location');
        let locationUrl;

        if (!locationHeaderValue) {
            return response;
        }

        const isAbsolute = isUrlAbsolute(locationHeaderValue);

        if (!isAbsolute) {
            // If the Location URL isn't absolute, we need to provide a Host so we can use
            // a URL object.
            locationUrl = new URL(
                locationHeaderValue,
                'http://www.example.com',
            );
        } else {
            locationUrl = new URL(locationHeaderValue);
        }

        for (const [key, value] of Object.entries(strippedParams)) {
            locationUrl.searchParams.append(key, value);
        }

        let newLocation;

        if (isAbsolute) {
            newLocation = locationUrl.toString();
        } else {
            newLocation = `${locationUrl.pathname}${locationUrl.search}`;
        }

        response.headers.set('location', newLocation);
    }

    return response;
}

/**
 * URL Utilities
 */
function isUrlAbsolute(url) {
    return url.indexOf('://') > 0 || url.indexOf('//') === 0;
}
