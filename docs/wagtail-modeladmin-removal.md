# wagtail-modeladmin & wagtail-orderable: Migration Inventory

This document inventories all usage of the `wagtail-modeladmin` and `wagtail-orderable` packages in preparation for their eventual removal. No code changes are described here — this is a scoping document only.

See ticket: [R1-319](https://torchbox.atlassian.net/browse/R1-319)

---

## Overview

The project currently depends on two packages that are candidates for removal:

- **`wagtail-modeladmin`** — a third-party continuation of `wagtail.contrib.modeladmin` which was removed from Wagtail core in Wagtail 6.0. It is not actively maintained long-term and will need to be replaced.
- **`wagtail-orderable`** (torchbox fork) — provides drag-and-drop ordering for ModelAdmin list views. Its usefulness is tied to `wagtail-modeladmin`; removing modeladmin makes this package redundant too.

The replacement path for both is Wagtail's built-in **`SnippetViewSet`** / **`ModelViewSet`** (available since Wagtail 5.0), which covers the same use cases natively.

**Scope summary:**

| Area                                    | Count |
| --------------------------------------- | ----- |
| Files with modeladmin imports           | 3     |
| ModelAdmin classes registered           | 25    |
| ModelAdminGroup containers              | 2     |
| Classes using `OrderableMixin`          | 1     |
| Custom PermissionHelper implementations | 2     |
| Custom IndexView implementations        | 1     |

---

## Package versions

| Package              | Version                     | Location            |
| -------------------- | --------------------------- | ------------------- |
| `wagtail-modeladmin` | `~2.2`                      | `pyproject.toml:32` |
| `wagtail-orderable`  | `1.3.1+tbx` (torchbox fork) | `pyproject.toml:33` |

Both are registered in `INSTALLED_APPS` in `rca/settings/base.py`:

- `wagtailorderable` — line 97
- `wagtail_modeladmin` — line 117

---

## ModelAdmin registrations

### `rca/utils/wagtail_hooks.py` — 23 classes

All registered together under **`TaxonomiesModelAdminGroup`**.

| ModelAdmin class                           | Model                            | Notes                                                           |
| ------------------------------------------ | -------------------------------- | --------------------------------------------------------------- |
| `DegreeLevelModelAdmin`                    | `DegreeLevel`                    |                                                                 |
| `AuthorModelAdmin`                         | `Author`                         |                                                                 |
| `SubjectModelAdmin`                        | `Subject`                        |                                                                 |
| `ProgrammeStudyModeModelAdmin`             | `ProgrammeStudyMode`             | Custom `IndexView` — hides "Add" button when instance count ≥ 2 |
| `ProgrammeTypeModelAdmin`                  | `ProgrammeType`                  | Uses `OrderableMixin` for drag-and-drop ordering                |
| `ProgrammeLocationModelAdmin`              | `ProgrammeLocation`              |                                                                 |
| `ResearchTypeModelAdmin`                   | `ResearchType`                   |                                                                 |
| `AreaOfExpertiseModelAdmin`                | `AreaOfExpertise`                |                                                                 |
| `ResearchThemeModelAdmin`                  | `ResearchTheme`                  |                                                                 |
| `SectorModelAdmin`                         | `Sector`                         |                                                                 |
| `DegreeTypeModelAdmin`                     | `DegreeType`                     |                                                                 |
| `DegreeStatusModelAdmin`                   | `DegreeStatus`                   |                                                                 |
| `DirectorateModelAdmin`                    | `Directorate`                    |                                                                 |
| `EventAvailabilityModelAdmin`              | `EventAvailability`              |                                                                 |
| `EventEligibilityModelAdmin`               | `EventEligibility`               |                                                                 |
| `EventLocationModelAdmin`                  | `EventLocation`                  |                                                                 |
| `EventSeriesModelAdmin`                    | `EventSeries`                    |                                                                 |
| `EventTypeModelAdmin`                      | `EventType`                      |                                                                 |
| `EditorialTypeModelAdmin`                  | `EditorialType`                  |                                                                 |
| `ScholarshipEligibilityCriteriaModelAdmin` | `ScholarshipEligibilityCriteria` |                                                                 |
| `ScholarshipFeeStatusModelAdmin`           | `ScholarshipFeeStatus`           |                                                                 |
| `ScholarshipFundingModelAdmin`             | `ScholarshipFunding`             |                                                                 |
| `ScholarshipLocationModelAdmin`            | `ScholarshipLocation`            |                                                                 |

---

### `rca/scholarships/wagtail_hooks.py` — 1 class

Registered under **`ScholarshipAdminGroup`** (menu order: 200).

| ModelAdmin class                        | Model                              | Notes                                                                                                                                                                                      |
| --------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ScholarshipEnquiryFormSubmissionAdmin` | `ScholarshipEnquiryFormSubmission` | Custom `PermissionHelper` (disables create); custom index template (`scholarships/index.html`); list export with multiple fields; custom `scholarships()` and `eligibility()` list columns |

---

### `rca/enquire_to_study/wagtail_hooks.py` — 1 class

Registered directly (no group).

| ModelAdmin class             | Model                   | Notes                                                                                                                                                                                                                                                                                                                |
| ---------------------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EnquiryFormSubmissionAdmin` | `EnquiryFormSubmission` | Custom `PermissionHelper` (disables create); custom index template (`enquire_to_study/index.html`); list export with multiple fields; `DateTimeRangeFilter`; custom `get_programmes()`, `get_country_of_residence()`, `get_country_of_citizenship()` list columns; queryset uses `select_related`/`prefetch_related` |

---

## wagtail-orderable usage

### Active usage

- **`OrderableMixin`** — imported from `wagtailorderable.modeladmin.mixins` in `rca/utils/wagtail_hooks.py`
- Applied to `ProgrammeTypeModelAdmin` to enable drag-and-drop reordering of `ProgrammeType` instances via a `sort_order` field

### Unused import

- `wagtailorderable.models.Orderable` is imported (aliased as `WagtailOrdable`) in `rca/programmes/models.py:37` but is not used anywhere in that file — can be removed independently.

### Not affected

All other `Orderable` usage in the codebase imports from `wagtail.models` (core Wagtail), which is unaffected by this migration. These models do not need to change.

---

## Migration complexity notes

These notes are to inform future planning — no code changes are being specified here.

| Area                                    | Complexity | Reason                                                      |
| --------------------------------------- | ---------- | ----------------------------------------------------------- |
| 21 simple taxonomy ModelAdmins          | Low        | Straightforward swap to `SnippetViewSet`                    |
| `ProgrammeStudyModeModelAdmin`          | Medium     | Custom `IndexView` logic to replicate                       |
| `ProgrammeTypeModelAdmin`               | Medium     | `OrderableMixin` drag-and-drop needs replacement strategy   |
| `ScholarshipEnquiryFormSubmissionAdmin` | High       | Custom permissions, export, and column methods              |
| `EnquiryFormSubmissionAdmin`            | High       | Custom permissions, export, date filter, and column methods |
