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

addEventListener('fetch', (event) => {
    event.respondWith(handleRouting(event));
});

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

/**
 * Return a request with specified querystring keys stripped out
 */
function stripIgnoredQuerystring(request) {
    const url = new URL(request.url);
    const stripKeys = STRIP_QUERYSTRING_KEYS.filter((v) =>
        url.searchParams.has(v),
    );

    if (stripKeys.length) {
        stripKeys.forEach((v) => url.searchParams.delete(v));

        return new Request(url, {
            body: request.body,
            headers: request.headers,
            redirect: request.redirect,
        });
    }
    return request;
}

async function handleRouting(event) {
    let cache = caches.default;
    let response;
    let request = stripIgnoredQuerystring(event.request);
    let url = new URL(request.url);
    let skipCache = hasPrivateCookie(request);

    if (!skipCache) {
        response = await cache.match(request);
    }

    if (!response) {
        response = await routeTo(NEW_HOST, request, url);
        if (response.status === 404) {
            // If we get a 404 from the new host, route to the legacy host
            response = await routeTo(LEGACY_HOST, request, url);
        }
        if (CANONICAL_DOMAIN && url.hostname !== CANONICAL_DOMAIN) {
            response = new Response(response.body, response);
            response.headers.set('X-Robots-Tag', 'noindex');
        }

        if (!skipCache) {
            event.waitUntil(cache.put(request, response.clone()));
        }
    }
    return response;
}
