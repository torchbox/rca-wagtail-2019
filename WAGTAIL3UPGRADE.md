# Wagtail 3.0 upgrade issues

## Admin sidebar

### Current Implementation

It is customised to hide the search bar by user group/permissions (Students)

### Problem

The side bar is now a javascript constructed element so the current implementation doesn't work.

### File:

`rca/account_management/templates/wagtailadmin/base.html`

## Comments from Kevin

Looks like we are going to have to find a new way to hide the sidebar for students, so this might be quite an overhaul.

---

## Content Panels

### Current Implementation

`StudentPage` which uses a `PerUserPageMixin` to hide/show content panels based on group/user permissions

### Problem

The content panels are not showing when choosing to edit the page as an admin or student, I've not been able to test if the permissions work but I think they will, it's more to do with how these panels need to be implemented in Wagtail v3.

I think this will require more changes than we have seen on other panel updates.

The upgrade [docs] have an example but it's not quite what we need due to the student/staff permissions used.

### Files:

`rca/people/models.py` & `rca/people/utils.py`

## Comments from Kevin

The gist of it is that if you are a superuser, then the super user panels will be rendered. Anyone else (like a student) would only see what's defined in the 'basic' content panels. It's a way of making sure students can edit their profiles but not edit anything that admin should only be able to control.

The is a loose test for some specific edit handlers being shown to different accounts here https://github.com/torchbox/rca-wagtail-2019/blob/master/rca/people/tests/test_utils.py#L41

But, it's definitely worth a manual test which would be:

sign in as admin and confirm super user panels
sign in as student and confirm you can't see any superuser defined panels.
