# Upgrading guidelines

This document describes aspects of the system which should be given particular attention when upgrading Wagtail or its dependencies.

## Wagtail package dependencies

We are maintaining our own forks of Wagtail packages at: <https://github.com/torchbox-forks>.

The enables any team member to propose a change to a package, we can all work directly on the work branch and submit it to the original author for consideration.

- [How we work on forked packages (intranet article).](https://intranet.torchbox.com/torchbox-teams/tech-team/working-with-3rd-party-packages/#forking-repositories)
- [Where we manage forked packages (Monday board).](https://torchbox.monday.com/boards/1124794299)

As much as possible, we want to use the official releases available on PyPI for the Wagtail package dependencies. A temporary solution is to fork the package dependency, tag the working branch, and use the tag in the pyproject file.

### Check these packages for updates

**Last tested for wagtail 6.0 upgrade** Comments in the pyproject.toml file may have more detailed information.

It is important to replace the usage of the git tags in the pyproject.toml file with the official release version from PyPI as soon as they become available.

## Critical paths

The following areas of functionality are critical paths for the site which don't have full automated tests and should be checked manually.

### 1. Account Management

App https://github.com/torchbox/rca-wagtail-2019/tree/master/rca/account_management

The account management app provides the functionality for administrators to create student accounts.
Most of this IS covered by unit tests, however it's still worth doing a test over the UI.

- First go to admin > settings > collections, you will need to create a new collection for a test user.
- Then go to `admin/student/create`, fill in the details and assign the collection, make sure 'create student page' is true.

Expected behaviour after submitting the form:

- A student account is created
- A student page is created and linked to the new user account
- An email is sent to the student inviting them to reset their password.

### 1.2 Student Accounts

App https://github.com/torchbox/rca-wagtail-2019/tree/master/rca/people

Most of the custom logic for students is covered by tests, but again it's worth testing the UI for any changes between wagtail versions.

Given in 1 (above) a student account is created, the student is able to sign in and edit their own page. There are a number of fields that we don't want the student to be able to edit. E.G title, collection, page link. There are also fields that we don't want anyone to be able to edit.

How to test:

- Sign in as admin and searh for 'students', this will show you a student page.
- Editing the student page as admin, you shouldn't be able to edit the ' Student user account' or ' Student user image collection' fields.
- Next, sign in as a student to edit your own student page.
- Students shouldn't see the Wagtail search in the sidebar, or any page, images etc menu links. It's all removed aside from 'help'
- you should see a reduced amount of fields compared to signing in as admin.
- The fields shown to superuser vs student roles can be seen [here](https://github.com/torchbox/rca-wagtail-2019/blob/master/rca/people/models.py#L765) in rca.people.models.StudentPage.content_panels

### 2. Enquire to study form

URL: https://www.rca.ac.uk/register-your-interest/
App: https://github.com/torchbox/rca-wagtail-2019/tree/master/rca/enquire_to_study

Whilst there are unit tests for this form, it has 2 integrations so important to test this form.
When submitted the form will geneate a submission object at `admin/enquire_to_study/enquiryformsubmission/`.

How to test:

- Fill out and submit the form as a user from the UK (integrates to Mailchimp)
- Fill out and submit the form as a user from outside the UK (integrates to QS)
- Confirm that the submission object is created in the admin view
- Confirm you can delete the submission(s) invidually and by bulk

### 3. Scholarship

URL: https://www.rca.ac.uk/study/application-process/funding-your-studies/rca-scholarships-and-awards/express-interest/
App: https://github.com/torchbox/rca-wagtail-2019/tree/master/rca/scholarships

Scholarships are added as snippets `admin/snippets/scholarships/scholarship/` and are rendered as choices on the form. After submitting the form, a submission object should be created in the admin at `admin/scholarships/scholarshipenquiryformsubmission/`

How to test:

- Fill out the form
- Confirm a submission is created at `admin/scholarships/scholarshipenquiryformsubmission/`
- Confirm you can delete the submission object individually and by bulk.

### 4. Import to intranet

The RCA intranet supports importing certain page types to the intranet from the main site. This is done by reading the pages API endpoint. Testing this can be a little trick, but rca-inforca-staging can be used to test it, as that staging site has the env var `RCA_CONTENT_API_URL` to read from the rca-develompoent site.

How to test:

- Pick/edit/create an Event Or Editorial page on the rca-development site (rca-development.herokuapp.com)
- Head to the intranet staging site importer at https://rca-inforca-staging.herokuapp.com/admin/content_importer/
- Click to import content, you should be offered a search showing you pages from the rca-development site.
- Import the content and make sure it's all gone smooth and fields are populated.

## Other considerations

As well as testing the critical paths, these areas of functionality should be checked:

### Student account vs Admin account editor viewing permissions.

1. The site has custom code to show/hide fields and panels depending on if a StudentPage is viewed by an admin (superuser) or a Student (none superuser).
2. The site has custom code to show/hide sidebar elements depending on if a Student is viewing the editor vs an admin (superuser).

---

#### Wagtail v3 Upgrade notes

When the site was upgraded to Wagtail v3 the original issue at v2.15 & v2.16 noted above was fixed.

Wagtail 3 introduced a lot of Javascript generated editor template "furniture" such as the admin side bar. To accommodate hiding the search input for Student accounts the following has been implemented.

- New wagtail_hooks [global_admin_css](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/people/wagtail_hooks.py#L21) and [global_admin_js](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/people/wagtail_hooks.py#L13)
- Wagtail [Base.html](https://github.com/torchbox/rca-wagtail-2019/blob/support/wagtail-3.0-upgrade/rca/account_management/templates/wagtailadmin/base.html) override. Specifically [here](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/account_management/templates/wagtailadmin/base.html#L12) Which adds a new data-attribute for the hooks above to operate on.

Wagtail 3 introduced a new [FieldPanel `permission` parameter](https://docs.wagtail.org/en/stable/reference/pages/panels.html#wagtail.admin.panels.FieldPanel.permission) which has been use on many fields of the [StudentPage](https://github.com/torchbox/rca-wagtail-2019/blob/support/wagtail-3.0-upgrade/rca/people/models.py#L777) content_panels.

Additionally there are some Custom Panels which help to add the `permission` parameter to child FieldPanels and control panel visibility in general.

- [StudentPageInlinePanel](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/people/utils.py#L72), including the custom templates at the following locations:
  - `rca/people/templates/admin/panels/student_page_inline_panel.html`
  - `rca/people/templates/admin/panels/student_page_inline_panel_child.html`
- [StudentPagePromoteTab](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/people/utils.py#L86)
- [StudentPageSettingsTab](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/people/utils.py#L107)

`use_json_field` argument added to `StreamField` (creates new migration files)

---

#### Wagtail v4 Upgrade notes

- Removed `wagtail_redirect_importer` as it's now part of Wagtail since version `2.10`

---

#### Wagtail v5 Upgrade notes

- Added `index.AutocompleteField` entries for the relevant fields on the model’s `search_fields` definition, as the old `SearchField("some_field", partial_match=True)` format is no longer supported.
- Changes to header CSS classes in `ModelAdmin` templates
- `wagtailsearch.Query` has been moved to `wagtail.contrib.search_promotions`
- `status` classes are now `w-status`

---

#### Wagtail v6 Upgrade notes

- `StreamField` no longer requires `use_json_field=True`

---

## Overridden core Wagtail templates

The following templates are overridden and should be checked for changes when upgrading Wagtail:

Last checked against Wagtail version: 6.1

- `rca/account_management/templates/wagtailadmin/base.html`
- ~~`rca/users/templates/wagtailusers/users/list.html`~~ This template was deleted in 2645c204425b8fa3409a110f46b2822a1953fe49 because as of Wagtail 6.1, [it's no longer used](https://github.com/wagtail/wagtail/commit/7b1644eb37b6b6cf7800276acf9abef5254fc096). Please note that the `user_listing_buttons` template tag was used in this template, and it has since been [deprecated](https://docs.wagtail.org/en/latest/releases/6.1.html#deprecation-of-user-listing-buttons-template-tag).

!!! warning "Technical Debt - to be addressed in Wagtail 6.2"

    The deleted `rca/users/templates/wagtailusers/users/list.html` template did two things:

    1.  altered the "Admin" (now called "Access level") column to show "Yes" if `user.is_superuser`.
        The default behaviour is to show "Admin" if `user.is_superuser`.
    2.  added a "Groups" column after the preceding column, whose contents are `{{user.group_links|join:", "}}`

    Retaining the above functionality in Wagtail 6.1 is not a trivial task.
    There's currently an [open PR](https://github.com/wagtail/wagtail/pull/11952) which
    seeks to solve this problem, and it may be ready in the 6.2 release.

    **Action**: When upgrading to Wagtail 6.2, look out for the above change, and restore
    the feature to the way it was before the 6.1 upgrade.

---

## Frontend authentication

This is the path to the Django template which is used to display the “password required” form when a user accesses a private page. For more details, see Wagtail's [Private pages](https://docs.wagtail.org/en/stable/advanced_topics/privacy.html#private-pages) documentation.

```python
WAGTAIL_PASSWORD_REQUIRED_TEMPLATE = "patterns/pages/wagtail/password_required.html"
```
