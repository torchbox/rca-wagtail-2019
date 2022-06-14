# Wagtail 3.0 upgrade issues

## Admin sidebar

### Current Implementation

It is customised to hide the search bar by user group/permissions (Students)

### Problem

The side bar is now a javascript constructed element so the current implementation doesn't work.

### File:

`rca/account_management/templates/wagtailadmin/base.html`


## Content Panels

### Current Implementation

`StudentPage` which uses a `PerUserPageMixin` to hide/show content panels based on group/user permissions

### Problem

I'm unsure about the changes needed here. I'm not entirely sure how this is intended or currently works.

### Files:

`rca/people/models.py` & `rca/people/utils.py`
