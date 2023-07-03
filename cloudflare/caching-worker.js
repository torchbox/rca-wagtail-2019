/*
  A modified version of the caching worker to route requests to the legacy system application if they don't exist on the new.
*/

const CANONICAL_DOMAIN = 'www.rca.ac.uk';

const PRIVATE_COOKIES = [
    'ssession=',
    'sessionid=',
    'csrftoken=',
    'sessionid=',
    'SESS[0-9A-Za-z]*=',
    '_shibsession_[0-9A-Za-z]*=',
    'CraftSessionId=',
];

const STRIP_QUERYSTRING_KEYS = [
    'utm_source',
    'utm_campaign',
    'utm_medium',
    'utm_term',
    'utm_content',
];

// Replace with real values
const NEW_HOST = 'xxxxxx';
const LEGACY_HOST = 'xxxxxx';

const CACHABLE_HTTP_STATUS_CODES = [200, 203, 206, 300, 301, 410];

addEventListener('fetch', (event) => {
    event.respondWith(handleRouting(event));
});

async function handleRouting(event) {
    const cache = caches.default;
    let request = stripIgnoredQuerystring(event.request)[0];

    let response;

    if (requestIsCachable(request)) {
        // If the request is cacheable, check for it in the cache
        response = await cache.match(request);
    }

    if (!response) {
        const url = new URL(request.url);
        response = await routeTo(NEW_HOST, request, url);
        if (response.status === 404) {
            // If we get a 404 from the new host, route to the legacy host
            response = await routeTo(LEGACY_HOST, request, url);
        }
        if (CANONICAL_DOMAIN && url.hostname !== CANONICAL_DOMAIN) {
            response = new Response(response.body, response);
            response.headers.set('X-Robots-Tag', 'noindex');
        }

        if (responseIsCachable(response)) {
            event.waitUntil(cache.put(request, response.clone()));
        }
    }

    return response;
}

/**
 * Convenience function to route requests to a particular host
 */
function routeTo(host, request, url) {
    const origin = url.host;
    const newUrl = new URL(url);
    newUrl.hostname = host;

    // Build new request with updated headers
    const newRequest = new Request(newUrl, request.clone());
    newRequest.headers.set('CF-Origin', origin);
    return fetch(newRequest);
}

/**
 * Check if the request includes any of the specified private cookies
 */
function hasPrivateCookie(request) {
    const patterns = new RegExp(PRIVATE_COOKIES.join('|'));
    const cookieString = request.headers.get('Cookie');
    return patterns.test(cookieString);
}

function stripIgnoredQuerystring(request) {
    /**
     * Given a Request, return a new Request with the ignored querystring keys stripped out,
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

        return [new Request(url, request), strippedParams];
    }
    return [request, strippedParams];
}

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
