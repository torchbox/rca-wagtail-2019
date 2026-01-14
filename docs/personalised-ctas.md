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
User visits page → Segments evaluated → Matching CTAs queried → CTAs displayed
```

1. When a user visits a page, the system evaluates which segments they belong to
2. The system queries for CTAs configured for:
   - The current page type (e.g., "Programme Page", "Event Detail Page") and/or specific pages
   - Any of the user's active segments
   - Current date/time (respecting go-live and expiry dates)
3. Matching CTAs are displayed in their designated locations on the page

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
   - Specific Page: CTA appears on selected individual pages
   - Check Include children to show the CTA on all child pages of the selected page
   - The CTA will appear if it matches by page type and/or specific pages
6. Set scheduling - optional go-live and expiry dates
7. Save and preview

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
3. Current page matches a configured page type and/or is a selected specific page (or child page if enabled)
4. Current time is after go-live (if set)
5. Current time is before expiry (if set)
