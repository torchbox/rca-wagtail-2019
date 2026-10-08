# Personalised CTAs

## Overview

The RCA website features a personalisation system that displays targeted call to action components to users based on their segments/rules. This system allows content editors to create dynamic, personalized experiences for different user groups without requiring code changes.

## Architecture

### Components

The personalisation system consists of three main components:

1. Segments - User groups defined by rules (using the `wagtail-personalisation` package)
2. CTA Models - Four types of personalised content blocks
3. Display Logic - Automatic rendering based on page type, non-page view, and/or specific page and segment matching

### How It Works

```
User visits page or view → Segments evaluated → Matching CTAs queried → CTAs displayed
```

1. When a user visits a page or non-page view, the system evaluates which segments they belong to
2. The system queries for CTAs configured for:
   - The current page type (e.g., "Programme Page", "Event Detail Page"), non-page view (e.g., "Register Your Interest (Form)"), and/or specific pages
   - Any of the user's active segments
   - Current date/time (respecting go-live and expiry dates)
3. Matching CTAs are displayed in their designated locations

### Non-page views

Some views on the site are not Wagtail pages but still support personalised CTAs. These are listed alongside page types in the "Page Types" inline panel and are identified by their view identifier rather than a content type:

| View | Identifier |
|---|---|
| Register Your Interest (Form) | `enquire_to_study.form` |
| Register Your Interest (Thank You) | `enquire_to_study.thanks` |

Unlike Wagtail page types, non-page views do not support the "Specific Pages" targeting option — only page type matching applies.

To add CTA support to a new non-page view, a developer must:

1. Add an entry to `PAGE_TYPE_CHOICES` in `rca/personalisation/models.py`
2. Apply `PersonalisedCTAMixin` (from `rca/personalisation/mixins.py`) to the view class and set `personalised_cta_view_type` to the new identifier

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
   - Page Types: CTA appears on all pages/views of the selected type(s), including non-page views
   - Specific Page: CTA appears on selected individual pages (not available for non-page views)
   - Check Include children to show the CTA on all child pages of the selected page
   - The CTA will appear if it matches by page type and/or specific pages
6. Set scheduling - optional go-live and expiry dates
7. Save and preview

#### Step 3: Test

- Test with different segments by modifying browser settings (location, time, etc.)
- Check on actual page types and views to ensure correct display

## Scheduling

All CTAs support scheduling with two fields:

- Go live date/time: When the CTA should start appearing
- Expiry date/time: When the CTA should stop appearing

Important: At least one of these dates must be set for the CTA to be active. If both are blank, the CTA is considered disabled and will not appear.

The system checks both segment rules AND scheduling. A CTA will only display if:

1. At least one scheduling date is set (go-live or expiry)
2. User matches at least one segment
3. Current page or view matches a configured page type and/or is a selected specific page (or child page if enabled)
4. Current time is after go-live (if set)
5. Current time is before expiry (if set)

## Caching Behavior

Pages displaying personalised CTAs require special cache handling to ensure users see content appropriate to their segment.

### How It Works

- **Pages without personalised CTAs**: Use standard cache control headers
- **Pages with personalised CTAs**: Automatically receive no-cache headers
