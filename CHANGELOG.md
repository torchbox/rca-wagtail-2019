# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Security

- [R1-391](https://torchbox.atlassian.net/browse/R1-391) Stop `PublicCacheVaryCookieMiddleware` from dropping the `Vary: Cookie` header when a CSRF cookie is set, which would otherwise let the CDN cache one visitor's CSRF token and serve it to everyone else on cached form pages
- [R1-391](https://torchbox.atlassian.net/browse/R1-391) Stop `PublicCacheVaryCookieMiddleware` from caching authenticated requests, so a staff member's `{% wagtailuserbar %}` edit toolbar can no longer end up in the shared public cache and get served to anonymous visitors

### Fixed

- [R1-391](https://torchbox.atlassian.net/browse/R1-391) Strip the session cookie and `Vary: Cookie` header from publicly cacheable responses, so personalisation no longer defeats CDN caching for anonymous traffic
- [R1-391](https://torchbox.atlassian.net/browse/R1-391) Fix wagtail-personalisation's `AppConfig` not loading on Django 5.2, which had silently disconnected the signal that sets `Segment.enable_date`/`disable_date`

### Added

- ...

### Changed

- ...

### Removed

- ...

## 2026-10-26

### Security

- [R1-394](https://torchbox.atlassian.net/browse/R1-394) Security update: Wagtail 7.4.4, certifi 2026.10.19, Pillow 13.0.0 and Django REST framework 3.18.3 (GHSA-jm43-45cc-q9rr, GHSA-g6cr-c9h3-6j2m, GHSA-3xgh-xc8p-9h54, GHSA-4pg7-87vv-vrh7, GHSA-jrgm-fhgv-hmj9, GHSA-6q48-6c7w-9gw2, CVE-2026-112403, CVE-2026-112397, CVE-2026-112400, CVE-2026-112404, CVE-2026-112895, CVE-2026-112896, CVE-2026-112897, CVE-2026-112395, CVE-2026-112899, CVE-2026-114136, CVE-2026-114137, CVE-2026-114138)

## 2026-10-08

### Fixed

- [AHM-265](https://torchbox.atlassian.net/browse/AHM-265) Fix SSO login HTTP 405: the single sign-on button now POSTs, as social-auth-app-django 6 requires

## 2026-10-07

### Security

- [R1-382](https://torchbox.atlassian.net/browse/R1-382) Django 5.2.18 security update and dependency CVE fixes

## 2026-09-28

### Security

- [R1-367](https://torchbox.atlassian.net/browse/R1-367) Wagtail 7.4.3 security update and dependency CVE fixes

## 2026-07-27

- [R1-344](https://torchbox.atlassian.net/browse/R1-344) Wagtail 7.4 Quarterly Upgrade

## 2026 pre-changelog 26-03-2026

This changelog was started on 26-03-2026. Before that date, changes were not documented here.
