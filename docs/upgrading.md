# Upgrading guidelines

This document describes aspects of the system which should be given particular attention when upgrading Wagtail or its dependencies.

## Wagtail package dependencies

We are maintaining our own forks of Wagtail packages at: <https://github.com/torchbox-forks>.

The enables any team member to propose a change to a package, we can all work directly on the work branch and submit it to the original author for consideration.

- [How we work on forked packages (intranet article).](https://intranet.torchbox.com/torchbox-teams/tech-team/working-with-3rd-party-packages/#forking-repositories)
- [Where we manage forked packages (Monday board).](https://torchbox.monday.com/boards/1124794299)

As much as possible, we want to use the official releases available on PyPI for the Wagtail package dependencies. A temporary solution is to fork the package dependency, tag the working branch, and use the tag in the pyproject file.

### Check these packages for updates

**Last tested for wagtail 7.0 upgrade** Comments in the pyproject.toml file may have more detailed information.

wagtail-accessibility
wagtail-django-recaptcha
wagtail-factories
wagtail-modeladmin
wagtail-orderable (uses a forked tag)
wagtail-rangefilter
wagtail-storages

It is important to replace the usage of the git tags in the pyproject.toml file with the official release version from PyPI as soon as they become available.

## PostgreSQL extensions

### pg_trgm extension

The `pg_trgm` extension is enabled via Django migration (`rca/search/migrations/0001_initial.py`) to support trigram similarity search. The similarity threshold is defined as a constant in `rca/search/views.py`.

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

The RCA intranet supports importing certain page types to the intranet from the main site. This is done by reading the pages API endpoint. Testing this can be a little tricky, but rca-inforca-staging can be used to test it, as that staging site has the env var `RCA_CONTENT_API_URL` to read from the rca-develompoent site.

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

### Users who logged in via SSO automatically gets 'Editor' permissions.

1. When users log in via SSO, they are automatically made editors. This is done via `rca.utils.pipeline.make_sso_users_editors` and added to the `SOCIAL_AUTH_PIPELINE`. RCA will manually elevate permissiosn if necessary.

### Users who logged in via SSO is redirected to a logout confirmation when they logout.

1. The site overrides the `/admin/logout/` endpoint to redirect users who logged in to `/logout/`. This is a confirmation screen that users will still need to manually log out of their SSO accounts. This is done with `rca.account_management.views.CustomLogoutView` and `rca.account_management.views.SSOLogoutConfirmationView`.
2. Users who did not log in via SSO should be able to log out without seeing any confirmation screen.

---

## Overridden core Wagtail templates

The following templates are overridden and should be checked for changes when upgrading Wagtail:

Last checked against Wagtail version: 7.0

- `rca/account_management/templates/wagtailadmin/base.html`
- `rca/project_styleguide/templates/patterns/pages/auth/login.html` - This was overridden to add the "Sign in with single sign-on" button to the login template.
- `rca/images/forms.py` - default wagtail image upload form extended to provide copyright acknowledgement checkbox.

## Overridden wagtail-modeladmin templates

These have been overridden to add the Delete button to the list view.

- `rca/scholarships/templates/scholarships/index.html`
- `rca/enquire_to_study/templates/enquire_to_study/index.html`

---

## Frontend authentication

This is the path to the Django template which is used to display the “password required” form when a user accesses a private page. For more details, see Wagtail's [Private pages](https://docs.wagtail.org/en/stable/advanced_topics/privacy.html#private-pages) documentation.

```python
WAGTAIL_PASSWORD_REQUIRED_TEMPLATE = "patterns/pages/wagtail/password_required.html"
```

## Python version upgrade

We don't generally upgrade python versions until a new LTS/Major version is released and has been stable for a while. We prefer to be running a more stable version of python.

If you are upgrading python, you should check the following python version references are updated:

- The `python` key in the `tool.poetry.dependencies` section of the `pyproject.toml` file.
- The `python` key in the pre-commit configuration file `.pre-commit-config.yaml`.
- The `python` image tag in the `Dockerfile`/s.
- Any references to the python version in documentation.
- Any references to the python version in the CI configuration file `gitlab-ci.yaml`.

### Pyupgrade tool

If you are upgrading python. There is a development tool available to help with modernising the codebase. This is installed as part of the poetry development dependencies.

To run the tool, use the following command:

```bash
git ls-files -z -- '*.py' | xargs -0 pyupgrade [python-version-arg]
```

Where `[python-version-arg]` is the version of python you are upgrading to.

To view the available version arguments, use the following command:

```bash
pyupgrade --help
```

### Pre-commit + Pyupgrade

The pyupgrade tool is run as a step in the pre-commit configuration. This will help you to use the modern syntax as you work on the codebase.

You can manually run the pre-commit checks on `*.py` files using the following command:

```bash
git ls-files -z -- '*.py' | xargs -0 | pre-commit run --files
```

## Django upgrades

If you are upgrading Django. There is a development tool available to help with modernising the codebase. This is installed as part of the poetry development dependencies.

### Django upgrade tool

If you are upgrading django. There is a development tool available to help with modernising the codebase. This is installed as part of the poetry development dependencies.

To run the tool, use the following command:

```bash
git ls-files -z -- '*.py' | xargs -0 django-upgrade --target-version [django-version-arg]
```

Where `[django-version-arg]` is the version of Django you are upgrading to.

### Pre-commit + django-upgrade

The django-upgrade tool is run as a step in the pre-commit configuration. This will help you to use the modern syntax as you work on the codebase.

You can manually run the pre-commit checks on `*.py` files using the following command:

```bash
git ls-files -z -- '*.py' | xargs -0 | pre-commit run --files
```
