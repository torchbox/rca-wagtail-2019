# Upgrading guidelines

This document describes aspects of the system which should be given particular attention when upgrading Wagtail or its dependencies.

## Critical paths

The following areas of functionality are critical paths for the site which don't have full automated tests and should be checked manually.

(If this information is managed in a separate document, a link here will suffice.)

### 1. [Summary of critical path, e.g. 'Donations']

[Description of the overall functionality covered]

- Step-by-step instructions for what to test and what the expected behaviour is
- Include details for edge cases as well as the general case
- Break this into separate subsections if there's a lot to cover
- Don't include anything which is already covered by automated testing, unless it's a prerequisite for a manual test

## Other considerations

As well as testing the critical paths, these areas of functionality should be checked:

- For unknown reasons, [the sidebar is not working properly](https://github.com/wagtail/wagtail.org/pull/144)
  after upgrading from Wagtail v2.15 to v2.16 . We decided to disable the sidebar. When the legacy sidebar removed in
  Wagtail 2.18, then that is the time to fix this issue If the problem still persists.
