# Personalised CTAs

## Overview

The RCA website features a personalisation system that displays targeted call to action components to users based on their segments/rules. This system allows content editors to create dynamic, personalized experiences for different user groups without requiring code changes.

## Architecture

### Components

The personalisation system consists of three main components:

1. Segments - User groups defined by rules (using the `wagtail-personalisation` package)
2. CTA Models - Four types of personalised content blocks
3. Display Logic - Automatic rendering based on page type and/or specific page and segment matching

### How It Works

```
Anonymous visitor → Shared page HTML → Private CTA request → Segments evaluated → Matching CTAs displayed
```

1. An anonymous visitor receives shared page HTML containing placeholders for the four CTA types. This response does not create or modify a personalisation session.
2. JavaScript requests the page's private CTA endpoint, which records the page visit and evaluates the visitor's segments once.
3. The system queries for CTAs configured for:
   - The current page type (e.g., "Programme Page", "Event Detail Page") and/or specific pages
   - Any of the user's active segments
   - Current date/time (respecting go-live and expiry dates)
4. The endpoint returns HTML fragments. The browser inserts them in the designated locations and initializes the existing triggers, countdowns, navigation controls and analytics.

Signed-in visitors, previews, form pages and pages with view restrictions retain server-rendered CTAs. These are excluded from the shared-page path. Personalised CTAs on shared pages require JavaScript; if the fragment request fails, the page's main content remains available without the CTAs.

### Creating a Personalised CTA

#### Step 1: Create Segments

1. Go to Wagtail Admin → Segments
2. Click 'Add segment'
3. Define your segment rules
4. Save the segment

#### Step 2: Create a CTA

1. Go to Wagtail Admin → Personalisation
2. Fill in the content fields
3. Select a user action (if available)
4. Add segments - the CTA will show to users in ANY selected segment
5. Add page types and/or specific pages - where the CTA should appear:
   - Page Types: CTA appears on all pages of the selected type(s)
   - Include specific pages: CTA appears on selected individual pages
   - Check Include children to show the CTA on all child pages of the selected page
   - The CTA will appear if it matches by page type and/or included specific pages
6. Optionally exclude specific pages - where the CTA should never appear, even if it would otherwise match:
   - Exclude specific pages: CTA will not appear on selected individual pages
   - Check Include children to also exclude all child pages of the selected page
   - Exclusions always take precedence over page type matches and included pages
7. Set scheduling - optional go-live and expiry dates
8. Save and preview

#### Step 3: Test

- Test with different segments by modifying browser settings (location, time, etc.)
- Check on actual page types to ensure correct display

## Scheduling

All CTAs support scheduling with two fields:

- Go live date/time: When the CTA should start appearing
- Expiry date/time: When the CTA should stop appearing

Important: At least one of these dates must be set for the CTA to be active. If both are blank, the CTA is considered disabled and will not appear.

The system checks both segment rules AND scheduling. A CTA will only display if:

1. At least one scheduling date is set (go-live or expiry)
2. User matches at least one segment
3. Current page matches a configured page type and/or is an included specific page (or child page if enabled)
4. Current page is not an excluded specific page (or child page of one if enabled) - exclusions always win, even over a page type or included page match
5. Current time is after go-live (if set)
6. Current time is before expiry (if set)

## Caching Behavior

Shared page HTML and visitor-specific CTA fragments have separate cache policies.

### How It Works

- **Anonymous public pages**: Return the standard public cache headers and a named URL for the fragment request. Personalisation neither starts a session nor evaluates rules on this response, even if the visitor already has a session cookie.
- **CTA fragments**: `/personalisation/ctas/<page_id>/` is GET-only and always returns `private, no-store` headers, including when no CTA matches. It owns the page-visit tracking and session writes, so returning-visitor targeting continues to work when the main page comes from a CDN.
- **Signed-in visitors and inline personalisation**: Keep private responses and server-rendered CTAs. Superuser segment overrides and previews continue to work.
- **Access restrictions**: The fragment endpoint only accepts live pages within the current site's page tree and rejects password-protected pages, other restricted pages and their descendants. Private pages use inline rendering instead.

The early `before_serve_page` hook marks eligible requests before the package constructs its session adapter. `RequestSegmentsAdapter` leaves those requests untouched; it retains normal session-backed behaviour for fragments and inline rendering. `BasePage.get_personalised_cta_context()` shares CTA selection between the two rendering paths.

### Cloudflare configuration

Application headers alone do not make Cloudflare cache HTML. A matching HTML cache rule is still required, and authenticated traffic, previews, admin routes, form submissions and the fragment endpoint must be excluded from shared caching. Keep the origin's private/no-store policy and Set-Cookie protections; do not force-cache fragment responses.

Confirm that publishing, unpublishing and page restriction changes purge cached HTML before enabling the rule. RCA's optional Wagtail Cloudflare purge integration is configured with the `FRONTEND_CACHE_CLOUDFLARE_TOKEN`, `FRONTEND_CACHE_CLOUDFLARE_EMAIL` and `FRONTEND_CACHE_CLOUDFLARE_ZONEID` environment variables.

The application cannot tell Cloudflare whether an opaque `sessionid` belongs to an anonymous or authenticated visitor. Bypassing all session cookies is conservative but also excludes returning anonymous visitors from edge caching. Review the existing authentication and cookie rules before enabling broader HTML caching. The application change has been verified locally; Cloudflare configuration and actual edge cache hits require separate verification.
