# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Security

- [R1-403](https://torchbox.atlassian.net/browse/R1-403) Fix four medium Trivy findings in the glob and minimatch Node dev dependencies

### Fixed

- [R1-403](https://torchbox.atlassian.net/browse/R1-403) The programme finder's filter bar no longer shows through the open mobile menu
- [R1-403](https://torchbox.atlassian.net/browse/R1-403) Fix the scroll icon's transition, which a missing comma had stopped from working

### Added

- ...

### Changed

- [R1-403](https://torchbox.atlassian.net/browse/R1-403) Wagtail 8.1 Quarterly Upgrade
- [R1-403](https://torchbox.atlassian.net/browse/R1-403) Python 3.13 → 3.15 and Node 24 → 26
- [R1-403](https://torchbox.atlassian.net/browse/R1-403) wagtail-personalisation now uses the upstream 1.0.0 release instead of the Torchbox fork
- [R1-403](https://torchbox.atlassian.net/browse/R1-403) Python packages are now managed with uv instead of Poetry
- [R1-403](https://torchbox.atlassian.net/browse/R1-403) Python linting and formatting now use ruff instead of black, flake8 and isort
- [R1-403](https://torchbox.atlassian.net/browse/R1-403) Node packages are now managed with pnpm instead of npm
- [R1-403](https://torchbox.atlassian.net/browse/R1-403) JavaScript linting and formatting now use Biome instead of ESLint

### Removed

- ...

## 2026-11-24

### Fixed

- [AHM-291](https://torchbox.atlassian.net/browse/AHM-291) Pages that can show a personalised CTA are cached again: the page fetches its CTAs once it has loaded, and page views no longer set a session cookie
- [AHM-291](https://torchbox.atlassian.net/browse/AHM-291) Log ignored Redis errors as one line rather than a traceback

## 2026-11-17

### Security

- [R1-399](https://torchbox.atlassian.net/browse/R1-399) Security update: Django 5.2.19 (CVE-2026-108147, CVE-2026-111211, CVE-2026-111362, CVE-2026-113593, CVE-2026-113733, CVE-2026-114582)

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
