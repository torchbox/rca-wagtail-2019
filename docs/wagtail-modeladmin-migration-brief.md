# Wagtail ModelAdmin Migration Brief

_Strategy pass — produced before implementation. Do not implement until reviewed._
_Date: 2026-06-16 · Branch: `chore/R1-319-remove-modeladmin`_

## Summary

- **Project / versions:** rca-wagtail-2019 · Wagtail pinned `~7.3`
  (**`poetry.lock` = 7.3.2; local venv = 7.4.2 — drift to reconcile, see below**) ·
  Django `~5.2` · `wagtail-modeladmin ~2.2` ·
  `wagtail-orderable` (torchbox fork `1.3.1+tbx`) · `wagtail-rangefilter ~0.2`.
- **Evidence reviewed:** `pyproject.toml`, `rca/settings/base.py` (INSTALLED_APPS),
  `rca/utils/wagtail_hooks.py`, `rca/enquire_to_study/wagtail_hooks.py`,
  `rca/enquire_to_study/views.py`, `rca/enquire_to_study/templates/enquire_to_study/index.html`,
  all referenced models, existing snippet/viewset registrations
  (`rca/personalisation/wagtail_hooks.py`, `rca/utils/models.py`), and the existing
  `wagtail-contrib-audit.md`. The installed `wagtailorderable` source was inspected.
- **Overall recommendation:** Migrate the two remaining `wagtail-modeladmin`
  registrations to Wagtail core viewsets. Replace `TaxonomiesModelAdminGroup`
  with a **`ModelViewSetGroup` of `ModelViewSet`s** (preserves the grouped
  "Taxonomies" menu and current FK-dropdown editor behaviour). Replace
  `EnquiryFormSubmissionAdmin` with a **`ModelViewSet` plus custom view behaviour**
  whose listing **reuses Wagtail's core form-submissions listing**
  (`SpreadsheetExportMixin` + `BaseListingView` + `wagtailforms/submissions_index.html`)
  rather than porting the modeladmin template — it is a read-only submission log with
  export and bulk-delete, so the core forms listing fits directly. No page
  modeladmins exist, so page-specific migration targets are out of scope.

### Important corrections to the existing audit

- `wagtail-contrib-audit.md` (dated 2026-04-09) lists
  `rca/scholarships/wagtail_hooks.py` as a modeladmin usage. **That file is now
  empty.** The scholarship taxonomy models (`ScholarshipFeeStatus`,
  `ScholarshipFunding`, `ScholarshipLocation`) are still administered, but only as
  items inside `TaxonomiesModelAdminGroup` in `rca/utils/wagtail_hooks.py`. Treat
  the audit count of "7" as stale; the live surface is **2 registrations**.
- `rca/people/admin/__init__.py` defines `StaffPageModelAdmin` and `PageAdmin`
  using **Django's `django.contrib.admin.ModelAdmin`** (for `django-import-export`),
  **not** `wagtail_modeladmin`. It is unrelated to this migration and must not be
  touched.

## Inventory

| Admin                            | Model(s)                       | Page model? | Custom behavior                                                                                        | Recommended target                                                                                 | Confidence |
| -------------------------------- | ------------------------------ | ----------: | ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- | ---------- |
| `TaxonomiesModelAdminGroup`      | 22 taxonomy models (see below) |          No | Grouped menu; one orderable item; one near-singleton item                                              | `ModelViewSetGroup` of `ModelViewSet`s                                                             | High       |
| ↳ `ProgrammeTypeModelAdmin`      | `ProgrammeType`                |          No | `OrderableMixin` (drag reorder) + `ordering=["sort_order"]`                                            | `ModelViewSet` w/ native reorder; swap to `wagtail.models.Orderable`; **drop `wagtail-orderable`** | High       |
| ↳ `ProgrammeStudyModeModelAdmin` | `ProgrammeStudyMode`           |          No | Custom `IndexView` hides "Add" when `count() >= 2`                                                     | `ModelViewSet` + custom index/permission                                                           | Medium     |
| `EnquiryFormSubmissionAdmin`     | `EnquiryFormSubmission`        |          No | Read-only create, `list_export`, `DateTimeRangeFilter`, custom index template, custom bulk-delete view | `ModelViewSet` + custom behaviour                                                                  | Medium     |

**Taxonomy group members** (all plain `models.Model` / `SluggedTaxonomy` /
`EventTaxonomyBase` / `WagtailOrdable` — none are pages): `DegreeLevel`,
`ProgrammeType`, `ProgrammeStudyMode`, `ProgrammeLocation`, `Subject`,
`ResearchType`, `AreaOfExpertise`, `Sector`, `ResearchTheme`, `Directorate`,
`DegreeType`, `DegreeStatus`, `EventAvailability`, `EventEligibility`,
`EventLocation`, `EventSeries`, `EventType`, `Author`, `EditorialType`,
`ScholarshipFeeStatus`, `ScholarshipFunding`, `ScholarshipLocation`.

## Recommended Approach

### 1. `TaxonomiesModelAdminGroup` → `ModelViewSetGroup`

- **Target surface:** `ModelViewSetGroup` containing one `ModelViewSet` per model.
- **Why this target fits:** These are plain Django CRUD models, not pages. They are
  referenced from pages via `ForeignKey` + plain `FieldPanel` (e.g.
  `FieldPanel("programme_type")`, `event_type = ForeignKey(...)`), so they currently
  render as **select dropdowns**, not snippet choosers. `ModelViewSet` preserves
  that exactly and keeps the models **out of the Snippets index**.
  `ModelViewSetGroup` preserves the single grouped "Taxonomies" menu. (A
  `SnippetViewSetGroup` is a viable alternative — see "Behavior requiring human
  approval".)
- **Current registration location:** `rca/utils/wagtail_hooks.py`
  (`modeladmin_register(TaxonomiesModelAdminGroup)`).
- **Migration-stage replacement location:** Same module —
  `rca/utils/wagtail_hooks.py` — registered via `register_admin_viewset`.
- **Post-migration move planned?:** Optional later cleanup only (e.g. splitting
  viewsets into per-app modules). Not part of the migration.
- **Behavior that should remain unchanged:** Single "Taxonomies" menu group;
  submenu item order; `tag` icons; per-model add/edit/delete; FK fields on pages
  stay as dropdowns (no chooser modal); models stay out of the Snippets index.
- **Filter widgets / result expectations:** No `list_filter` defined on the group
  items — no filter parity work for taxonomies.
- **List columns / custom cells / thumbnails / table markup:** Items rely on default
  `__str__` listing; no custom columns or thumbnail cells to port.
- **Admin URL path/namespace compatibility:** **DECIDED (2026-06-16): old
  modeladmin URL paths may change.** Old modeladmin paths (`/admin/utils/<model>/…`
  style) will move to viewset namespaces; no `url_prefix` work is required and no
  reverse-name preservation is needed for these. (No external links or tests depend
  on them — none found.)
- **Menu placement / grouped membership / Snippets index:** Preserve grouped menu;
  with `ModelViewSet` the items do **not** appear in the Snippets index (intended).
- **Behavior that may intentionally change:** Listing actions and table styling
  follow generic viewset templates rather than modeladmin templates.
- **Behavior requiring human approval:** ~~Whether any taxonomy should instead become
  a `SnippetViewSet`.~~ **DECIDED (2026-06-16): taxonomies use `ModelViewSet`.** This
  preserves the current FK-dropdown editor behaviour and keeps the models out of the
  Snippets index. No taxonomy is to be registered as a snippet.

#### 1a. `ProgrammeType` (orderable) — DECIDED: native reorder, remove `wagtail-orderable`

**DECISION (2026-06-16): `ProgrammeType` keeps drag-and-drop reordering using
Wagtail core's native `ModelViewSet` reorder, and `wagtail-orderable` is removed
entirely.**

This is supported in the running Wagtail (verified in the local venv, 7.4.2):

- `wagtail.admin.viewsets.model.ModelViewSet` defines `sort_order_field` and
  **auto-detects it** from the model when the model exposes a `sort_order_field`
  attribute (`viewsets/model.py:117-121`). When set, `reorder_view_enabled` becomes
  true and a `reorder/<pk>/` URL + drag handle are wired automatically
  (`viewsets/model.py:154-155, 605-607`), driven by
  `wagtail.admin.views.generic.ordering.ReorderView`.
- **Swap the model base** `wagtailorderable.models.Orderable` →
  **`wagtail.models.Orderable`** (`rca/programmes/models.py:37,112`). The two are
  **field-identical**: both define
  `sort_order = IntegerField(null=True, blank=True, editable=False)` and
  `sort_order_field = "sort_order"`. Same DB column → expect at most an
  options-only / no-op migration (Wagtail core's `Orderable.Meta` also sets
  `ordering = ["sort_order"]`). **Verify the generated migration is a no-op.**
- `ProgrammeType`'s `ModelViewSet` then needs **no explicit reorder config** — the
  `sort_order_field` is auto-detected from the new base.

**Removing `wagtail-orderable` (no other consumers — `WagtailOrdable` is used only
by `ProgrammeType`; the modeladmin `OrderableMixin` import disappears with this
migration):**

- Remove `"wagtailorderable"` from `INSTALLED_APPS` (`rca/settings/base.py:97`).
- Remove the `OrderableMixin` import (`rca/utils/wagtail_hooks.py:6`).
- Remove `wagtailorderable` from `.isort.cfg` `known_third_party` (line 8).
- Remove the `wagtail-orderable` dependency from `pyproject.toml` and re-lock.

**Parity note to verify:** the torchbox `wagtail-orderable` `Orderable` auto-assigns
`sort_order` on first `save()` of a new object; Wagtail core's `Orderable` relies on
the admin's `set_max_order` helper instead. Add a test that a newly created
`ProgrammeType` receives a usable `sort_order` and that drag-reorder persists.

**Version dependency:** native `ModelViewSet` reorder is present in the venv's
7.4.2 but **`poetry.lock` pins 7.3.2**. Confirm the deployed version ships
`ModelViewSet.sort_order_field` (Wagtail ≥ 7.4 to be safe) and reconcile the
lock/venv drift before relying on this.

#### 1b. `ProgrammeStudyMode` (near-singleton) — custom behaviour

- Custom `ProgrammeStudyModeIndexView(IndexView)` hides the "Add" button once
  `ProgrammeStudyMode.objects.count() >= 2`. Reproduce on `ModelViewSet` by
  overriding the index view context or gating add permission. Preserve the
  "max-two-instances" intent; do not regress to unrestricted add.

### 2. `EnquiryFormSubmissionAdmin` → `ModelViewSet` + custom behaviour

- **Target surface:** `ModelViewSet` (model is `EnquiryFormSubmission`, a
  `ClusterableModel`) with create disabled, and a custom **index view that reuses
  Wagtail's core form-submissions listing** rather than a ported modeladmin
  template (see decision below).
- **Why this target fits:** It is a read-only submission log/report, not editor CRUD.
  Wagtail's core form-submissions listing
  (`wagtail.contrib.forms.views.SubmissionsListView`, built on
  `BaseListingView` + `SpreadsheetExportMixin`, template
  `wagtailforms/submissions_index.html`) already provides exactly this workflow:
  date-filtered listing, CSV/XLSX export, ordering, and delete. The enquiry admin's
  `list_export`/`list_filter`/search map onto it directly.
- **DECIDED (2026-06-16): the listing uses the core form-submissions listing.**
  Build the index view on the same machinery the core submissions listing uses —
  `SpreadsheetExportMixin` for export, a date-range `filterset_class`, and the
  `wagtailforms/submissions_index.html` template family — pointed at
  `EnquiryFormSubmission` (override `get_base_queryset`, columns, and export fields).
  Do **not** rebuild or extend the old `modeladmin/index.html` template. A custom
  `ViewSet` is an acceptable alternative to `ModelViewSet` here if subclassing the
  core listing view is cleaner than fitting it into `ModelViewSet`'s index slot.
- **Current registration location:** `rca/enquire_to_study/wagtail_hooks.py`
  (`modeladmin_register(EnquiryFormSubmissionAdmin)`), plus a `register_admin_urls`
  hook exposing `enquiretostudy_delete`.
- **Migration-stage replacement location:** Same module —
  `rca/enquire_to_study/wagtail_hooks.py`.
- **Post-migration move planned?:** No.
- **Behavior that should remain unchanged:**
  - **No create:** `EnquiryFormSubmissionPermissionHelper.user_can_create` returns
    `False`. Replace with a `ModelViewSet`/`PermissionPolicy` that disables add.
  - **Export:** `list_export` (15 fields incl. `get_*` callables). Preserve the
    export columns and the export buttons.
  - **Custom list columns:** `get_programmes`, `get_country_of_residence`,
    `get_country_of_citizenship` callable columns must be reproduced.
  - **Querysets:** `select_related` / `prefetch_related` optimisation must be
    carried over.
  - **Search:** `search_fields = ("first_name","last_name","email","country_of_residence")`.
  - **Custom bulk-delete:** header "Delete submissions" button → `enquiretostudy_delete`
    view (`rca/enquire_to_study/views.py`). Keep this URL/view working.
- **Filter widgets / result expectations:** `list_filter` is
  `(("submission_date", DateTimeRangeFilter), "enquiry_submission_programmes__programme")`.
  `DateTimeRangeFilter` comes from `wagtail-rangefilter` (django-filter based) and
  must be wired through a `filterset_class` on the viewset. **DECIDED (2026-06-16):
  the programme `list_filter` stays a dropdown.** Define the relation filter
  explicitly in the `filterset_class` (e.g. a django-filter `ModelChoiceFilter` /
  `ModelMultipleChoiceFilter` on `enquiry_submission_programmes__programme`) so it
  renders as a select dropdown rather than the default text/auto widget.
- **List columns / custom cells / table markup:** See callable columns above; no
  thumbnail cells.
- **Admin URL path/namespace compatibility:** The custom `enquiretostudy_delete`
  URL name is referenced by the index template (`{% url 'enquiretostudy_delete' %}`)
  and is covered by `rca/enquire_to_study/tests/test_views.py` — **preserve this URL
  name**.
- **Menu placement:** `menu_label = "Enquiry Submissions"`, `menu_icon = "doc-full"`,
  `menu_order = 200`, top-level (not settings menu). Preserve placement; note
  viewset default menu order differs from modeladmin's, so set `menu_order`
  explicitly.
- **Behavior that may intentionally change:** Listing chrome moves to generic
  viewset templates.
- **Behavior requiring human approval:** ~~Whether to rebuild the custom index
  template.~~ **DECIDED (2026-06-16): use the core form-submissions listing** (see
  Target surface). The old `enquire_to_study/index.html` (which
  `{% extends "modeladmin/index.html" %}` and loads `modeladmin_tags`) is
  **deleted**, not ported. The custom export/delete header actions are re-homed onto
  the core submissions-listing equivalents (export buttons + a delete view modeled on
  the core `DeleteSubmissionsView`, while preserving the existing
  `enquiretostudy_delete` URL name and its custom logic).

## Page Workflow Risks

**No `ModelAdmin` manages a `Page` subclass.** Page-specific modeladmin migration
(PageListingViewSet / PageViewSet / choose-parent labels / explorer visibility /
page listing actions) is **not required**.

- No `exclude_from_explorer` intent is in play (the one occurrence,
  `exclude_from_explorer = False` on the enquiry admin, is the default and concerns
  a non-page model).
- Existing page-related hooks unaffected by this migration: the
  `register_rich_text_features` external-link handler in `rca/utils/wagtail_hooks.py`
  (keep as-is) and the Django-admin `StaffPage`/`Page` import-export admins in
  `rca/people/admin/__init__.py` (out of scope).

## Custom Workflow Risks

- **Near-singleton admin:** `ProgrammeStudyMode` add-button suppression at `>= 2`
  instances (custom `IndexView`). Preserve.
- **Read-only / restricted actions:** `EnquiryFormSubmission` create disabled via
  `PermissionHelper`. Preserve as disabled-add on the viewset.
- **Custom delete / bulk action:** `enquiretostudy_delete` custom view + header
  button. Preserve view, URL name, and entry point.
- **Custom list buttons / header actions:** Enquiry index header actions (delete +
  export buttons). Re-home onto viewset header-button hooks or a custom template.
- **Custom templates:** `enquire_to_study/index.html` extends a `modeladmin/`
  template — **resolved: deleted, replaced by the core form-submissions listing**
  (`wagtailforms/submissions_index.html` family). See §2.
- **Orderable admin UI:** `ProgrammeType` drag-reorder — **resolved**: use native
  `ModelViewSet` reorder (swap base to `wagtail.models.Orderable`) and drop
  `wagtail-orderable`. See §1a.
- No manually-composed `get_admin_urls_for_registration()` / `get_menu_item()`
  modeladmin instances were found (the only custom hook is the standalone delete URL).

## Implementation Sequence

1. **Taxonomies (lowest risk first):** Build `ModelViewSet`s + `ModelViewSetGroup`
   in `rca/utils/wagtail_hooks.py`, registered via `register_admin_viewset`, beside
   the existing modeladmin group. Verify menu, ordering, CRUD, and that page FK
   fields still render as dropdowns. As part of this step: swap `ProgrammeType` to
   `wagtail.models.Orderable` (verify no-op migration) so its `ModelViewSet` gets
   native drag-reorder, and reproduce `ProgrammeStudyMode` add-suppression.
2. **Enquiry submissions:** Build the viewset with add disabled and an index view
   that reuses the **core form-submissions listing** (`SpreadsheetExportMixin` +
   `BaseListingView` + `wagtailforms/submissions_index.html`), pointed at
   `EnquiryFormSubmission`: override base queryset (with the existing
   `select_related`/`prefetch_related`), columns (incl. `get_programmes` etc.),
   export fields (`list_export`), date-range filter (`DateTimeRangeFilter`), and
   search. Delete the old `enquire_to_study/index.html`. Preserve the
   `enquiretostudy_delete` URL name and its custom logic. Verify against
   `test_views.py`.
3. **Remove `wagtail-modeladmin` and `wagtail-orderable`** only after both
   migrations are verified: delete `"wagtail_modeladmin"` and `"wagtailorderable"`
   from `INSTALLED_APPS` (`rca/settings/base.py:117,97`), remove all
   `wagtail_modeladmin` / `wagtailorderable` imports, drop both from `.isort.cfg`
   and `pyproject.toml`, re-lock, and confirm no remaining references.
4. **Optional later cleanup:** reorganise viewsets into per-app modules.

Decisions in "Unknowns" can block steps 1–2; resolve before implementing those
items.

## Execution Handoff

- **Admins ready for implementation (pending no blocking decisions):** the 20
  plain taxonomy `ModelViewSet`s.
- **Admins blocked pending decisions:** None. All design decisions are resolved —
  taxonomies → `ModelViewSet`; `ProgrammeType` → native reorder + remove
  `wagtail-orderable`; old modeladmin URLs may change; enquiry → core
  form-submissions listing with a dropdown programme filter. `ProgrammeStudyMode`
  "max two" is confirm-only (implement to preserve current behaviour). **Brief is
  ready for implementation.**
- **Shared helpers/hooks to create first:** a reusable disabled-add permission
  policy/mixin for the enquiry viewset. (`ProgrammeType` reorder needs no helper —
  it uses native `ModelViewSet` reorder via `wagtail.models.Orderable`.)
- **Registration location decisions:** keep replacements in their existing
  `wagtail_hooks.py` modules during migration (`rca/utils/`, `rca/enquire_to_study/`).
- **Optional post-migration move targets:** per-app taxonomy viewset modules.
- **Files likely to change:** `rca/utils/wagtail_hooks.py`,
  `rca/programmes/models.py` (`Orderable` base swap + a no-op/options migration),
  `rca/enquire_to_study/wagtail_hooks.py`,
  `rca/enquire_to_study/templates/enquire_to_study/index.html` (**delete** — replaced
  by the core form-submissions listing),
  `rca/settings/base.py` (remove `wagtail_modeladmin` and `wagtailorderable`),
  `.isort.cfg` (remove `wagtailorderable`),
  `pyproject.toml` (remove `wagtail-modeladmin` **and** `wagtail-orderable`).
- **Dependencies to remove:** `wagtail-modeladmin` (after both migrations verified)
  **and** `wagtail-orderable` (after `ProgrammeType` swaps to
  `wagtail.models.Orderable`).
- **Dependencies to keep:** `wagtail-rangefilter` (still needed for the enquiry
  `DateTimeRangeFilter`).

## Test Scenarios

- "Taxonomies" menu group visible with all members and stable order.
- Each taxonomy: create / edit / delete works; FK fields on related pages still
  render as a select dropdown (not a chooser); model absent from Snippets index
  (under `ModelViewSet`).
- `ProgrammeType`: drag-and-drop reorder works via native `ModelViewSet` reorder
  (after the `wagtail.models.Orderable` base swap); listing ordered by `sort_order`;
  a newly created instance gets a usable `sort_order`; the base-swap migration is a
  no-op/options-only change.
- `ProgrammeStudyMode`: "Add" hidden once two instances exist; allowed below two.
- Enquiry listing: add disabled for all users; columns incl. `get_programmes` etc.
  render; queryset optimisation intact.
- Enquiry filters: `submission_date` range filter and programme filter return the
  correct sets; assert the programme filter renders as a **dropdown** (select), not a
  text input.
- Enquiry export: export produces the full `list_export` column set.
- Enquiry bulk delete: `enquiretostudy_delete` URL name resolves and the header
  button links to it; existing `test_views.py` still passes.
- Enquiry search across configured `search_fields`.
- After dependency removal: app boots with `wagtail_modeladmin` absent from
  `INSTALLED_APPS` and no import errors.

## Unknowns (require human approval)

- ~~Should any taxonomy model become a `SnippetViewSet`?~~ **RESOLVED
  (2026-06-16): all taxonomies use `ModelViewSet`.**
- ~~For `ProgrammeType`: is losing the drag-to-reorder UI acceptable?~~ **RESOLVED
  (2026-06-16): keep drag-and-drop via native `ModelViewSet` reorder; swap base to
  `wagtail.models.Orderable`; remove `wagtail-orderable`.** (Confirm deploy runs
  Wagtail ≥ 7.4 and reconcile the `poetry.lock` 7.3.2 vs venv 7.4.2 drift.)
- ~~Should old modeladmin URL paths be preserved with a `url_prefix`?~~ **RESOLVED
  (2026-06-16): old modeladmin URL paths may change — no `url_prefix` needed.** (Note:
  this does not cover the custom `enquiretostudy_delete` URL **name**, which is
  referenced by a template and `test_views.py` and must still be preserved.)
- ~~Should the enquiry custom index template be rebuilt?~~ **RESOLVED (2026-06-16):
  use the core form-submissions listing; delete `enquire_to_study/index.html`.**
- ~~Must the enquiry programme `list_filter` remain a dropdown?~~ **RESOLVED
  (2026-06-16): yes — define a `ModelChoiceFilter`/`ModelMultipleChoiceFilter` in the
  `filterset_class` to keep the dropdown.**
- Confirm the `ProgrammeStudyMode` "max two instances" rule is still desired.
  _(Confirm-only; not a blocker — implement to preserve current behaviour by default.)_

---

## Implementation Notes (2026-06-16, post-implementation)

Implementation carried out by the
`wagtail-modeladmin-migration-implementation` skill. All tests pass (full suite:
245 tests; targeted admin tests: 28). `manage.py check` and
`makemigrations --check` are clean.

### Done

- **Taxonomies → `ModelViewSetGroup`** in `rca/utils/wagtail_hooks.py`
  (`TaxonomiesViewSetGroup`, 22 `ModelViewSet`s via a shared `TaxonomyViewSet`
  base with `exclude_form_fields = []`). Grouped "Taxonomies" menu, item order,
  `tag` icons, and `menu_label`s preserved; models stay out of the Snippets index.
- **`ProgrammeType`** base swapped to `wagtail.models.Orderable`
  (`rca/programmes/models.py`); native `ModelViewSet` drag-reorder confirmed and
  the base swap generated **no migration** (field-identical). Create-time
  `sort_order` assignment preserved via the create view's `set_max_order`.
- **`ProgrammeStudyMode`** add-button suppression at ≥2 reproduced by overriding
  `header_buttons` on a custom `IndexView` (the model's own `save()`/manager also
  hard-enforce the max-two rule).
- **`EnquiryFormSubmission` → `ModelViewSet`** in
  `rca/enquire_to_study/wagtail_hooks.py`: add disabled for all users via a
  reusable `DisableCreatePermissionPolicy`; `list_display`/`list_export` callable
  columns moved onto the model; queryset `select_related`/`prefetch_related`
  carried over; search preserved; "Delete submissions" header button re-homed via
  `header_buttons`. Old `enquire_to_study/index.html` deleted; `confirm_delete.html`
  re-based off `wagtailadmin/base.html`. `enquiretostudy_delete` URL name preserved;
  `views.delete()` and `test_views.py` now use `reverse("enquiryformsubmission:index")`.
- **`wagtail-orderable` removed** (no remaining consumers anywhere): dropped from
  `INSTALLED_APPS`, `.isort.cfg`, `pyproject.toml`, and re-locked.
- Deleted an **orphaned** modeladmin template,
  `rca/scholarships/templates/scholarships/index.html` (unreferenced dead code
  that extended `modeladmin/index.html`).

### Corrections to this brief found during implementation

- **`wagtail-modeladmin` CANNOT be removed yet — BLOCKED by
  `wagtail-personalisation`.** The torchbox `wagtail-personalisation` fork
  (`wagtail_personalisation/views.py`) imports `wagtail_modeladmin.options` and
  registers its own `SegmentModelAdmin`; its only fallback is the
  `wagtail.contrib.modeladmin` that Wagtail 7 removed. So both the package and the
  `"wagtail_modeladmin"` `INSTALLED_APPS` entry must stay until
  `wagtail-personalisation` itself stops depending on modeladmin. The brief's
  "remove `wagtail-modeladmin`" step is therefore deferred; the entry is kept with
  an explanatory comment. The project's **own** modeladmin usage is fully migrated.
  - **Re-checked 2026-06-17 against `wagtail-personalisation` `0.17.0+tbx`** (the
    currently pinned tag, fork commit `6b4fc8a`, PR #14
    `support/wagtail-74-maintenance`). That release is a **Wagtail 7.4 maintenance
    bump only** — it does **not** drop modeladmin. `views.py` still imports
    `wagtail_modeladmin.options` / `.views` and registers `SegmentModelAdmin`, and
    the fork's own `pyproject.toml` still pins `wagtail-modeladmin>=1`. The blocker
    is unchanged.
- **`wagtail-rangefilter` is NOT django-filter based** (the brief assumed it was).
  Its `DateTimeRangeFilter` subclasses `django.contrib.admin.filters.FieldListFilter`
  and cannot be used inside a `WagtailFilterSet`. The `submission_date` filter was
  ported to django-filter's native `DateFromToRangeFilter` + `DateRangePickerWidget`
  (the same mechanism Wagtail core's form-submissions listing uses). As a result
  `wagtail-rangefilter`/`rangefilter` became **unused** and were **removed**
  (from `INSTALLED_APPS` and `pyproject.toml`, re-locked), superseding the brief's
  "keep `wagtail-rangefilter`" line.
- The brief missed `enquire_to_study/confirm_delete.html`, which also extended
  `modeladmin/index.html`; it was re-based so the delete workflow survives.

### Dependencies removed

- `wagtail-orderable` (no remaining consumers).
- `wagtail-rangefilter` / `django-admin-rangefilter` (`rangefilter`), replaced by
  django-filter's native date-range filter.

### Still blocked

- `wagtail-modeladmin` removal, blocked by `wagtail-personalisation` (see above).
  Confirmed still blocking at the pinned `0.17.0+tbx` tag (checked 2026-06-17).
  Evidence in the installed fork
  (`.venv/src/wagtail-personalisation/src/wagtail_personalisation/`):
  - `views.py:11-12` — `from wagtail_modeladmin.options import ModelAdmin,
modeladmin_register` and `from wagtail_modeladmin.views import DeleteView, IndexView`.
  - `views.py:74-75` — `@modeladmin_register class SegmentModelAdmin(ModelAdmin)`.
  - `wagtail_hooks.py:181,230` — reverse `wagtail_personalisation_segment_modeladmin_create`
    / `..._index`.
  - the fork's `pyproject.toml` declares `wagtail-modeladmin>=1`.
  - **To unblock:** migrate the fork's `SegmentModelAdmin` to a Wagtail core ViewSet —
    preserving its custom dashboard/list-toggle index view, the cascade page-variant
    delete view, the `..._create` / `..._index` URL names referenced by hooks and
    templates, and the `modeladmin/wagtail_personalisation/segment/*` templates — then
    release a new `+tbx` tag, re-pin it here, and only then drop `wagtail-modeladmin`
    from `INSTALLED_APPS` and `pyproject.toml`. This is upstream package work (use the
    `wagtail-package-modernizer` skill against the fork repo), out of scope for this branch.

---

_Handoff: this brief is the single strategy artifact. Implementation should be
carried out by the `wagtail-modeladmin-migration-implementation` skill after the
Unknowns above are resolved._
