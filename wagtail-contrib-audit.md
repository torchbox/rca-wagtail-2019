# Wagtail Contrib Dependency Audit

_Generated: 2026-04-09_

## Summary

| Package                   | In Dependencies | Used in Code | Usage Count |
| ------------------------- | --------------- | ------------ | ----------- |
| wagtail-modeladmin        | Yes             | Yes          | 7           |
| wagtail-orderable         | Yes             | Yes          | 4           |
| wagtail-instance-selector | No              | No           | 0           |
| wagtail-generic-chooser   | No              | No           | 0           |
| wagtail-personalisation   | Yes             | Yes          | 25          |
| wagtail-rangefilter       | Yes             | Yes          | 3           |

---

## wagtail-modeladmin

**Declared in dependencies:** Yes

- File: `pyproject.toml`, version: `~2.2`

**Used in source code:** Yes

### Usages

| File                                    | Line | Context                                                                                   |
| --------------------------------------- | ---- | ----------------------------------------------------------------------------------------- |
| `rca/settings/base.py`                  | 117  | `"wagtail_modeladmin"` (INSTALLED_APPS)                                                   |
| `rca/utils/wagtail_hooks.py`            | 4    | `from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register` |
| `rca/utils/wagtail_hooks.py`            | 5    | `from wagtail_modeladmin.views import IndexView`                                          |
| `rca/enquire_to_study/wagtail_hooks.py` | 3    | `from wagtail_modeladmin.helpers import PermissionHelper`                                 |
| `rca/enquire_to_study/wagtail_hooks.py` | 4    | `from wagtail_modeladmin.options import ModelAdmin, modeladmin_register`                  |
| `rca/scholarships/wagtail_hooks.py`     | 3    | `from wagtail_modeladmin.helpers import PermissionHelper`                                 |
| `rca/scholarships/wagtail_hooks.py`     | 4    | `from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register` |

---

## wagtail-orderable

**Declared in dependencies:** Yes

- File: `pyproject.toml`, version: git fork `torchbox-forks/wagtail-orderable`, tag `1.3.1+tbx`

**Used in source code:** Yes

### Usages

| File                         | Line | Context                                                           |
| ---------------------------- | ---- | ----------------------------------------------------------------- |
| `rca/settings/base.py`       | 97   | `"wagtailorderable"` (INSTALLED_APPS)                             |
| `rca/utils/wagtail_hooks.py` | 6    | `from wagtailorderable.modeladmin.mixins import OrderableMixin`   |
| `rca/programmes/models.py`   | 37   | `from wagtailorderable.models import Orderable as WagtailOrdable` |
| `.isort.cfg`                 | 8    | `wagtailorderable` listed in `known_third_party`                  |

---

## wagtail-instance-selector

**Declared in dependencies:** No

**Used in source code:** No

---

## wagtail-generic-chooser

**Declared in dependencies:** No

**Used in source code:** No

---

## wagtail-personalisation

**Declared in dependencies:** Yes

- File: `pyproject.toml`, version: git fork `torchbox-forks/wagtail-personalisation`, branch `feature/customisable-base-rules`

**Used in source code:** Yes

### Usages

| File                                                                                                  | Line | Context                                                                       |
| ----------------------------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------- |
| `rca/settings/base.py`                                                                                | 118  | `"wagtail_personalisation"` (INSTALLED_APPS)                                  |
| `rca/settings/base.py`                                                                                | 913  | `"wagtail_personalisation.TimeRule"` (WAGTAIL_PERSONALISATION rules)          |
| `rca/settings/base.py`                                                                                | 914  | `"wagtail_personalisation.DayRule"` (WAGTAIL_PERSONALISATION rules)           |
| `rca/settings/base.py`                                                                                | 915  | `"wagtail_personalisation.DeviceRule"` (WAGTAIL_PERSONALISATION rules)        |
| `rca/settings/base.py`                                                                                | 917  | `"wagtail_personalisation.OriginCountryRule"` (WAGTAIL_PERSONALISATION rules) |
| `rca/utils/models.py`                                                                                 | 28   | `from wagtail_personalisation.adapters import get_segment_adapter`            |
| `rca/personalisation/apps.py`                                                                         | 11   | comment: `wagtail_personalisation`'s `get_geoip_module()`                     |
| `rca/personalisation/apps.py`                                                                         | 23   | `from wagtail_personalisation.rules import OriginCountryRule`                 |
| `rca/personalisation/factories.py`                                                                    | 4    | `from wagtail_personalisation.models import Segment`                          |
| `rca/personalisation/models.py`                                                                       | 14   | `from wagtail_personalisation.models import Segment`                          |
| `rca/personalisation/models.py`                                                                       | 15   | `from wagtail_personalisation.rules import AbstractBaseRule`                  |
| `rca/personalisation/models.py`                                                                       | 1139 | comment: visit_count tracked by wagtail-personalisation                       |
| `rca/personalisation/migrations/0001_initial.py`                                                      | 16   | migration dependency on `wagtail_personalisation`                             |
| `rca/personalisation/migrations/0001_initial.py`                                                      | 155  | FK to `wagtail_personalisation.segment`                                       |
| `rca/personalisation/migrations/0002_embeddedfootercalltoaction_and_more.py`                          | 14   | migration dependency on `wagtail_personalisation`                             |
| `rca/personalisation/migrations/0002_embeddedfootercalltoaction_and_more.py`                          | 90   | FK to `wagtail_personalisation.segment`                                       |
| `rca/personalisation/migrations/0002_embeddedfootercalltoaction_and_more.py`                          | 122  | FK to `wagtail_personalisation.segment`                                       |
| `rca/personalisation/migrations/0004_eventcountdowncalltoaction_eventcountdownctasegment_and_more.py` | 14   | migration dependency on `wagtail_personalisation`                             |
| `rca/personalisation/migrations/0004_eventcountdowncalltoaction_eventcountdownctasegment_and_more.py` | 156  | FK to `wagtail_personalisation.segment`                                       |
| `rca/personalisation/migrations/0005_collapsiblenavigationcalltoaction_and_more.py`                   | 14   | migration dependency on `wagtail_personalisation`                             |
| `rca/personalisation/migrations/0005_collapsiblenavigationcalltoaction_and_more.py`                   | 96   | FK to `wagtail_personalisation.segment`                                       |
| `rca/personalisation/migrations/0007_usertyperule.py`                                                 | 12   | migration dependency on `wagtail_personalisation`                             |
| `rca/personalisation/migrations/0007_usertyperule.py`                                                 | 45   | FK to `wagtail_personalisation.segment`                                       |
| `rca/personalisation/migrations/0010_origincontinentrule.py`                                          | 12   | migration dependency on `wagtail_personalisation`                             |
| `rca/personalisation/migrations/0010_origincontinentrule.py`                                          | 52   | FK to `wagtail_personalisation.segment`                                       |

---

## wagtail-rangefilter

**Declared in dependencies:** Yes

- File: `pyproject.toml`, version: `~0.2`

**Used in source code:** Yes

### Usages

| File                                    | Line | Context                                                       |
| --------------------------------------- | ---- | ------------------------------------------------------------- |
| `rca/settings/base.py`                  | 115  | `"wagtail_rangefilter"` (INSTALLED_APPS)                      |
| `rca/enquire_to_study/wagtail_hooks.py` | 5    | `from wagtail_rangefilter.filters import DateTimeRangeFilter` |
