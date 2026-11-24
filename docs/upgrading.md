# Upgrading guidelines

This document describes aspects of the system which should be given particular attention when upgrading Wagtail or its dependencies.

## Node dependency holds

- `stylelint` (`^17.16.0`): held because `stylelint-config-torchbox@5.0.0`, its latest release, only supports `stylelint@^17`; its 18.x major has no compatible `stylelint-config-torchbox` release yet. Lift when `stylelint-config-torchbox` supports stylelint v18.
  Evidence: `PNPM_CONFIG_STRICT_PEER_DEPENDENCIES=true pnpm install --lockfile-only` with `stylelint` bumped to `^18.0.0` fails with `unmet peer stylelint, Installed: 18.1.0, Wanted ^17.0.0: stylelint-config-torchbox@5.0.0`
  Release notes: https://github.com/stylelint/stylelint/releases/tag/18.0.0
- `video.js` (`^8.24.2`): held because v10 replaced the classic `Tech` plugin API with `createPlayer`/extension packages, dropping `videojs.registerTech`/`getTech`, which `amazon-ivs-player`'s `registerIVSTech` calls to register the IVS playback tech. Lift when `amazon-ivs-player` ships a v10-compatible release.
  Evidence: `node -e "const videojs = require('video.js'); require('amazon-ivs-player').registerIVSTech(videojs, {})"` on `video.js@10.5.0` fails with `videojs not available, AmazonIVS tech not registered`
  Release notes: https://github.com/videojs/video.js/blob/main/CHANGELOG.md (no tagged v9/v10 release page; see the "Release Video.js 10.0.0 as stable" entry)

## Python dependencies

### pillow-heif wheel availability

`pillow-heif` (pulled in by Wagtail's `Willow[heif]` extra) only ships wheels for actively-supported CPython minors, so a Python bump can land on a locked version with no wheel for the new interpreter — the build then fails compiling it from source, since the production image has no `libheif` headers. Re-lock just that package (`uv lock --upgrade-package pillow-heif`) rather than widening the dependency bump.

### lxml wheel availability

Same pattern as `pillow-heif` above: `lxml` only ships wheels for actively-supported CPython minors, so a Python bump can land on a locked patch version with no wheel for the new interpreter, and the build fails compiling it from source (missing `libxml2`/`libxslt` headers in the production image). Re-lock just that package (`uv lock --upgrade-package lxml`) to the newest patch within the existing specifier rather than widening the dependency bump.

## Wagtail package dependencies

We are maintaining our own forks of Wagtail packages at: <https://github.com/torchbox-forks>.

The enables any team member to propose a change to a package, we can all work directly on the work branch and submit it to the original author for consideration.

- [How we work on forked packages (intranet article).](https://intranet.torchbox.com/torchbox-teams/tech-team/working-with-3rd-party-packages/#forking-repositories)
- [Where we manage forked packages (Monday board).](https://torchbox.monday.com/boards/1124794299)

As much as possible, we want to use the official releases available on PyPI for the Wagtail package dependencies. A temporary solution is to fork the package dependency, tag the working branch, and use the tag in the pyproject file.

### Check these packages for updates

**Last tested for wagtail 8.1 upgrade** Comments in the pyproject.toml file may have more detailed information.

wagtail-accessibility
wagtail-django-recaptcha
wagtail-factories
wagtail-modeladmin
wagtail-orderable (uses a forked tag)
wagtail-rangefilter
wagtail-storages
wagtail-personalisation — see also the userbar hook noted under [Other considerations](#other-considerations)

It is important to replace the usage of the git tags in the pyproject.toml file with the official release version from PyPI as soon as they become available.

### wagtail-personalisation: fork retired for upstream 1.0.0

This project pinned the Torchbox fork (`torchbox-forks/wagtail-personalisation` at `0.16.0+tbx`) until this upgrade, which replaced it with the upstream `1.0.0` PyPI release. Diffed the fork against upstream 1.0.0 directly: every change the fork carried over its base (the Wagtail 5.2+ button-hook signatures, the `<li>`-based userbar markup, the custom icon registration, and the `request.headers` modernisation) is already in `1.0.0`. The only gap is one migration, `0027_update_help_text` (a cosmetic `django-countries` choice reorder plus a `Meta.verbose_name` rename), which upstream's chain doesn't carry under that name; nothing in this project depends on it, so it's a harmless gap, not a blocker.

The Wagtail 8.1 `construct_wagtail_userbar` three-argument break noted under [Other considerations](#other-considerations) isn't related to this swap: the fork never patched that hook either, so the runtime patch in `PersonalisationConfig` applies regardless of which package variant is installed.

## PostgreSQL extensions

### pg_trgm extension

The `pg_trgm` extension is enabled via Django migration (`rca/search/migrations/0001_initial.py`) to support trigram similarity search. The similarity threshold is defined as a constant in `rca/search/views.py`.

## Critical paths

The following areas of functionality are critical paths for the site which don't have full automated tests and should be checked manually.

### 1. Account Management

App <https://github.com/torchbox/rca-wagtail-2019/tree/master/rca/account_management>

The account management app provides the functionality for administrators to create student accounts.
Most of this IS covered by unit tests, however it's still worth doing a test over the UI.

- First go to admin > settings > collections, you will need to create a new collection for a test user.
- Then go to `admin/student/create`, fill in the details and assign the collection, make sure 'create student page' is true.

Expected behaviour after submitting the form:

- A student account is created
- A student page is created and linked to the new user account
- An email is sent to the student inviting them to reset their password.

### 1.2 Student Accounts

App <https://github.com/torchbox/rca-wagtail-2019/tree/master/rca/people>

Most of the custom logic for students is covered by tests, but again it's worth testing the UI for any changes between wagtail versions.

Given in 1 (above) a student account is created, the student is able to sign in and edit their own page. There are a number of fields that we don't want the student to be able to edit. E.G title, collection, page link. There are also fields that we don't want anyone to be able to edit.

How to test:

- Sign in as admin and search for 'students', this will show you a student page.
- Editing the student page as admin, you shouldn't be able to edit the ' Student user account' or ' Student user image collection' fields.
- Next, sign in as a student to edit your own student page.
- Students shouldn't see the Wagtail search in the sidebar, or any page, images etc menu links. It's all removed aside from 'help'
- you should see a reduced amount of fields compared to signing in as admin.
- The fields shown to superuser vs student roles can be seen [here](https://github.com/torchbox/rca-wagtail-2019/blob/master/rca/people/models.py#L765) in rca.people.models.StudentPage.content_panels

### 2. Enquire to study form

URL: <https://www.rca.ac.uk/register-your-interest/>
App: <https://github.com/torchbox/rca-wagtail-2019/tree/master/rca/enquire_to_study>

Whilst there are unit tests for this form, it has 2 integrations so important to test this form.
When submitted the form will generate a submission object at `admin/enquire_to_study/enquiryformsubmission/`.

How to test:

- Fill out and submit the form as a user from the UK (integrates to Mailchimp)
- Fill out and submit the form as a user from outside the UK (integrates to QS)
- Confirm that the submission object is created in the admin view
- Confirm you can delete the submission(s) invidually and by bulk

### 3. Import to intranet

The RCA intranet supports importing certain page types to the intranet from the main site. This is done by reading the pages API endpoint. Testing this can be a little tricky, but rca-inforca-staging can be used to test it, as that staging site has the env var `RCA_CONTENT_API_URL` to read from the rca-staging site.

How to test:

- Pick/edit/create an Event Or Editorial page on the rca-staging site (<https://rca-staging.torchbox.dev>)
- Head to the intranet staging site importer at <https://rca-inforca-staging.herokuapp.com/admin/content_importer/>
- Click to import content, you should be offered a search showing you pages from the rca-staging site.
- Import the content and make sure it's all gone smooth and fields are populated.

## Other considerations

As well as testing the critical paths, these areas of functionality should be checked:

### Student account vs Admin account editor viewing permissions

1. The site has custom code to show/hide fields and panels depending on if a StudentPage is viewed by an admin (superuser) or a Student (none superuser).
2. The site has custom code to show/hide sidebar elements depending on if a Student is viewing the editor vs an admin (superuser).

### Users who logged in via SSO automatically gets 'Editor' permissions

1. When users log in via SSO, they are automatically made editors. This is done via `rca.utils.pipeline.make_sso_users_editors` and added to the `SOCIAL_AUTH_PIPELINE`. RCA will manually elevate permissions if necessary.

### Users who logged in via SSO is redirected to a logout confirmation when they logout

1. The site overrides the `/admin/logout/` endpoint to redirect users who logged in to `/logout/`. This is a confirmation screen that users will still need to manually log out of their SSO accounts. This is done with `rca.account_management.views.CustomLogoutView` and `rca.account_management.views.SSOLogoutConfirmationView`.
2. Users who did not log in via SSO should be able to log out without seeing any confirmation screen.

### Personalisation segments hidden from the userbar

1. `rca.personalisation.wagtail_hooks.remove_personalisation_segments` strips segment items from the userbar via `construct_wagtail_userbar` (Wagtail 8.0's `request, items, page` form). A renamed or removed `segment` attribute would silently stop the filtering.
2. `wagtail-personalisation`'s own `add_segment_link_items` hook is still two-argument at its latest release (1.0.0): Wagtail 8.1 calls every userbar hook as `(request, items, page)` unconditionally, so this would raise `TypeError`. `rca.personalisation.apps.PersonalisationConfig._patch_personalisation_userbar_hook` wraps it in place by reaching into Wagtail's private `hooks._hooks` registry, not a documented API, so it can also break if Wagtail changes how that registry is structured, not only once wagtail-personalisation adds the third argument. Drop the patch once a newer wagtail-personalisation release fixes it upstream (the patch checks the hook's signature and leaves it alone once it does).

### Wagtail v2 API in use (rca.wagtailapi)

Last checked on Wagtail 8.1

`rca/wagtailapi/` builds its page, image and navigation endpoints on `wagtail.api.v2` (router, filters, serializers), with several project-specific filter backends and serializers layered on top. Wagtail 8.1 keeps v2 working with no warning yet, but it raises deprecation warnings from 8.2 and is removed in 9.0. Migrate `rca/wagtailapi/` to `wagtail.api.v3` before that upgrade; the filters and serializers will need porting, not just an import swap.

### Frontend cache purge on page move or slug change (Cloudflare)

Last checked on Wagtail 8.1

Wagtail now purges the frontend cache on a page move or slug change, not only on publish. This project's Cloudflare backend (`wagtail.contrib.frontend_cache`) will see more purge requests for bulk page reorganisations; if that approaches Cloudflare's rate limits, set `PURGE_BATCH_SIZE` on the backend config.

### `tzdata` declared for base-image timezone drift

Debian Trixie drops the legacy tz aliases from its base image, so `zoneinfo` can no longer resolve a stored legacy timezone (e.g. `US/Eastern`) from the system database alone. `tzdata` is declared directly so the app carries its own IANA database, aliases included, independent of what the base image ships.

### Legacy `@babel/polyfill`

`main.entry.js` still imports `@babel/polyfill` for the Safari 11 / iOS Safari 11-12 browserslist floor. The package is frozen at `7.12.1` and bundles a deprecated `core-js@2`; no further `@babel/polyfill` release exists. Replacing it needs a `@babel/preset-env` `useBuiltIns` + `core-js@3` migration, scoped to what those browsers actually lack: out of scope for a routine dependency bump.

## Python dependency holds

- `django-import-export` (`~3.3`): 4.x breaks the resource/admin API `rca/people/admin/` overrides, and the untested import feature needs full re-test. Lift when it is re-tested end to end on 4.x and the tablib hold clears too.
  Evidence: `grep -nE 'resource_class =|def (before_|after_)?save_instance' rca/people/admin/__init__.py rca/people/admin/page_import.py` fails with unchanged 3.x signatures still present (`resource_class = StaffPageResource`, old `save_instance` signature)
  Release notes: https://django-import-export.readthedocs.io/en/stable/release_notes.html (the v4.0 section)

## Security

Last security review: 2026-11-24

### Accepted CVE-2026-9318 in tablib

- Package: tablib held at ==3.5.0
- Verified binding constraint: upstream hard-pin — every `django-import-export` 3.3.x release depends on `tablib[html,ods,xls,xlsx,yaml] (3.5.0)` exactly, so no later tablib is reachable while the project pins `django-import-export = "~3.3"`.
- How verified: promoting tablib to a direct `tablib~=3.10.0` dependency and running `uv lock` fails with "Because django-import-export>=3.3.0,<=3.3.9 depends on tablib[html]==3.5.0 ..., your project's requirements are unsatisfiable", confirming every `django-import-export` 3.3.x release up to 3.3.9, the last on that line, hard-pins `tablib==3.5.0`. The lock keeps nothing when the resolve fails. tablib 3.10.0 is months older than the cool-down window, so release age is not the blocker.
- Why unreachable: CVE-2026-9318 is stored XSS in tablib's HTML _export_. This project uses `django-import-export` for import only — `rca/people/admin/page_import.py` subclasses `ImportMixin` and `resources.ModelResource` with import-side hooks; no `ExportMixin`, export action, or HTML export format is registered anywhere under `rca/`.
- Cool-down: not bypassed — the fix is cool-down-allowed; the `django-import-export ~3.3` ceiling blocks it, not the cool-down.

Lifted by upgrading `django-import-export` to 4.x, which relaxes the tablib pin. That is itself held by the ceiling recorded in `pyproject.toml` ("v4+ has breaking changes"), and the import feature needs comprehensive testing before it moves.

---

## Overridden core Wagtail templates

The following templates are overridden and should be checked for changes when upgrading Wagtail:

Last checked against Wagtail version: 7.3

- `rca/account_management/templates/wagtailadmin/base.html`
- `rca/project_styleguide/templates/patterns/pages/auth/login.html` - Extends `wagtailadmin/login.html` and adds the "Sign in with single sign-on" form in the `below_login` block. Only check that the block still exists.
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

- The `requires-python` key in the `[project]` section of the `pyproject.toml` file.
- The `python` key in the pre-commit configuration file `.pre-commit-config.yaml`.
- The `python` image tag in the `Dockerfile`/s.
- Any references to the python version in documentation.
- Any references to the python version in the CI configuration file `gitlab-ci.yaml`.

### Pyupgrade tool

If you are upgrading python. There is a development tool available to help with modernising the codebase. This is installed as part of the uv dev dependency group.

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

If you are upgrading Django. There is a development tool available to help with modernising the codebase. This is installed as part of the uv dev dependency group.

### Django upgrade tool

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
