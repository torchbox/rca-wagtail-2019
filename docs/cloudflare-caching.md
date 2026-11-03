# RCA returning-visitor HTML cache

`infrastructure/cloudflare/caching-worker.mjs` is a standalone ES module replacement for the production
`caching-worker` source supplied on 2 November 2026. It is prepared for review;
adding this file to the application does not deploy it to Cloudflare. The original
policy remains in place for the other hostnames using this Worker. Only
`www.rca.ac.uk` uses the new policy.

## Request flow

1. A visitor without a session can receive cached public HTML.
2. The browser requests `/personalisation/ctas/<page_id>/` privately. Django saves
   the visitor's existing personalisation session and, if anonymous, issues a
   signed `__Host-rca-anonymous` marker.
3. Later public-page requests carry both cookies. The Worker verifies the marker
   against the current `sessionid`, hostname and expiry before checking its cache.
4. Existing anonymous sessions without a marker initially bypass the cache; their
   next successful CTA request supplies one without discarding visitor history.
5. Missing, invalid or expired markers with a session bypass the cache. Django
   login rotates the session ID and middleware deletes the old marker on normal
   and SSO login responses. A stale marker cannot validate against the new session.
   Logout and later anonymous CTA requests establish a fresh anonymous session.

The marker grants access only to shared public HTML, not to an account or private
content. The Worker still sends the original cookies to the origin on a miss and
on every private request. HTML and CTA requests are separate: every CTA fetch
still reaches Django for visit tracking and personalisation.

## Application/Worker contract

| Setting or field               | Value                                                                                   |
| ------------------------------ | --------------------------------------------------------------------------------------- |
| Dedicated secret on both sides | `PERSONALISATION_CACHE_SIGNING_KEY`, at least 32 bytes                                  |
| Enabled hostname               | `www.rca.ac.uk`                                                                         |
| Django session cookie          | `sessionid`                                                                             |
| Marker cookie                  | `__Host-rca-anonymous`; Secure, HttpOnly, SameSite=Lax, Path=/, no Domain               |
| Marker lifetime                | Up to one hour, bounded by session expiry; renewed on successful anonymous CTA requests |
| Marker format                  | `v1.<expiry Unix seconds>.<lowercase hex HMAC-SHA256>`                                  |
| Signed UTF-8 message           | `rca-anonymous-cache:v1\n<hostname>\n<sessionid>\n<expiry>`                             |
| Origin opt-in for shared HTML  | `X-RCA-Cacheable: public-v1`                                                            |
| Worker diagnostics             | `X-RCA-Cache-Status`                                                                    |

Use a new random secret, separate from Django's `SECRET_KEY` and Cloudflare API
credentials. Do not put it in this repository or in a browser-visible setting.
The example signature fixture contains a public test key only. The application
issues markers only on HTTPS requests for the enabled hostname, after
SessionMiddleware has saved the session; keep AnonymousCacheMiddleware before
SessionMiddleware in the settings list. Public HTML never renews the marker or
creates a personalisation session.

The application decides whether a page may opt in; the Worker independently
rejects unsafe response headers before sharing it.
`tests/test_django_contract.py` passes actual Django response headers and
Set-Cookie values to the production Worker module through
`tests/django-contract.mjs`. It checks public cache reuse, alternative cache
lifetimes and rejection of private responses without reimplementing the
cacheability checks in the test harness. These tests run as
a separate CI step from the repository checkout, alongside the fixed signature
compatibility fixture. Infrastructure files are excluded from the Docker image;
Worker deployment remains a manual copy through the Cloudflare release process.

With the secret absent or shorter than 32 bytes, the application issues no marker
or origin opt-in header and the new Worker bypasses its RCA cache path. A wrong
secret causes session requests to bypass. Rotation of the shared secret similarly
invalidates existing markers until a private CTA response renews them.

## Shared and private responses

The new Worker stores only status-200 HTML explicitly opted in by the anonymous
public-page rendering path, with public Cache-Control and no Set-Cookie or
private/no-store/no-cache directive. Unknown Vary dimensions are rejected. Existing
cache entries without the new opt-in are ignored. The cache key omits cookies;
the origin request retains them. This normalisation applies only to explicitly
shareable HTML, never to CTA fragments.

The Worker bypasses non-GET requests, Authorization, Origin, AJAX and Range
requests, client no-cache/no-store requests, and admin, authentication, API,
documents and CTA routes. Form and restricted-page responses do not receive the
origin opt-in and remain private. Cache read/write failures do not stop the page
being served.

Diagnostics distinguish `HIT`, `MISS`, `BYPASS-SESSION`, `BYPASS-ROUTE`,
`BYPASS-REQUEST`, `BYPASS-RESPONSE` and `BYPASS-CONFIG`. `MISS` means an origin
response was returned and a cache write attempted; it does not guarantee the cache
accepted the write. Cache contents are local to Cloudflare's serving data centre.

## Restriction changes

Adding, editing or deleting a `PageViewRestriction` schedules cache invalidation
after the database transaction commits. The RCA Cloudflare backend sends a global
prefix purge for the page's path on every Wagtail site that serves it. This covers
descendants and query-string variants; a restriction above a site's root purges
that entire site. Rolled-back changes do not trigger a purge. Normal publishing
and unpublishing retain Wagtail's existing file-purge behaviour.

This requires the `FRONTEND_CACHE_CLOUDFLARE_*` settings and the configured
`rca.utils.frontend_cache.CloudflareBackend`. Cloudflare prefix purging is
[available on all plans](https://developers.cloudflare.com/changelog/post/2025-04-01-purge-for-all).
Purge failures are logged under `wagtail.frontendcache`; monitor
these errors because failed invalidation can leave public HTML cached until its
TTL expires. Confirm that the API credentials permit prefix purging and that the
configured Wagtail site hostnames match the production Worker routes.

## Rollout and verification

1. Review the application and Worker together. Verify that publishing,
   unpublishing, restrictions on a page or ancestor, and relevant shared-content
   changes invalidate the affected cached HTML. The optional Wagtail Cloudflare
   purge settings must be checked in the target environment; manual dashboard
   purging does not establish automatic invalidation.
2. Configure the same new secret as an application environment variable and a
   secret binding on `caching-worker`. Deploy the application first. With the old
   Worker still running, session requests keep their existing bypass behaviour.
3. After verifying invalidation, deploy the reviewed standalone ES module Worker
   through the normal Cloudflare release process, preserving existing routes.
   Do not add a competing Cache Everything rule or strip origin Set-Cookie. The
   Worker serves other RCA hostnames, so retain the hostname guard and legacy path.
4. In a fresh browser, verify public HTML MISS then HIT in the same data centre,
   a private CTA response carrying session and marker cookies, and HIT on later
   public pages and returning visits. Check the real CTA targeting and visit
   counts. Requests with sessions but no valid marker must show BYPASS-SESSION.
5. Test normal login, SSO, logout, marker expiry, forms, previews and restricted
   pages. Logged-in and private responses must remain uncached, and expired
   markers should be renewed only through private CTA responses.
6. Verify publish/unpublish/restriction purging against the actual Worker cache,
   then compare origin request rates and resource use. Cached HTML still triggers
   a private CTA request; a reduction in production memory use is not guaranteed.

Rollback: restore the previous Worker source first, returning every session to the
old bypass policy. Remove the dedicated secret afterwards if disabling markers.
No database migration is required.

## Local checks

The cross-runtime contract tests run separately from the application test suite.
Run them from a repository checkout with the Poetry environment, Node from
`.nvmrc` on PATH and a test database available. The application container does not
need the Worker files or the contract-test runner.

```sh
node --test infrastructure/cloudflare/tests/cache-checks.mjs
docker compose exec web python manage.py test rca.personalisation.tests.test_cache_marker --settings=rca.settings.test
docker compose exec web python manage.py test rca.personalisation.tests.test_restriction_cache --settings=rca.settings.test
poetry run python manage.py test infrastructure.cloudflare.tests.test_django_contract --settings=rca.settings.test
```

The Node tests exercise first/returning visits, cross-session cache reuse, invalid
markers, login rotation, private requests, response protections and the legacy
hostname policy using a local cache/origin harness. Django tests exercise real
session saving, CTA tracking, normal login, SSO's Django login operation, logout
and public/private responses. The contract tests also execute the actual Worker
against Django's responses with default and alternative cache lifetimes.
The fixed signature fixture remains
a compatibility check. Restriction tests exercise commit/rollback behaviour
and the Cloudflare prefix-purge requests for edits, deletion, descendants and
multiple site roots. These checks do not establish live Cloudflare hits or
successful production purging.
