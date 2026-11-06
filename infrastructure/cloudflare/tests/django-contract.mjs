import worker from '../caching-worker.mjs';

let input = '';
for await (const chunk of process.stdin) input += chunk;
const { secret, cases } = JSON.parse(input);
const entries = new Map();
const pending = [];
let originRequests = 0;
const keyFor = (request) =>
    `${request.url}|${request.headers.get('Accept-Encoding')}`;

globalThis.caches = {
    default: {
        async match(request) {
            return entries.get(keyFor(request))?.clone();
        },
        async put(request, response) {
            entries.set(keyFor(request), response.clone());
        },
    },
};

const results = [];
for (const item of cases) {
    globalThis.fetch = async () => {
        originRequests += 1;
        return new Response(item.response.body, {
            status: item.response.status,
            headers: item.response.headers,
        });
    };
    const response = await worker.fetch(
        new Request(item.url, {
            headers: item.cookie ? { Cookie: item.cookie } : {},
        }),
        { PERSONALISATION_CACHE_SIGNING_KEY: item.secret ?? secret },
        { waitUntil: (promise) => pending.push(promise) },
    );
    await Promise.all(pending.splice(0));
    results.push({
        decision: response.headers.get('X-RCA-Cache-Status'),
        body: await response.text(),
        originRequests,
        cacheEntries: entries.size,
    });
}

process.stdout.write(JSON.stringify(results));
