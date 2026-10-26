# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Security

- ...

### Fixed

- Evaluate personalisation segments once per request, avoiding duplicate database work and preserving editor segment overrides
- Keep signed-in page responses private even when no personalised CTA is displayed

### Added

- ...

### Changed

- Upgrade wagtail-personalisation from the Torchbox fork to upstream 1.0.0, retaining RCA's custom segmentation rules
- Load personalised CTAs through a private endpoint so anonymous page HTML can be shared without creating a visitor session

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
