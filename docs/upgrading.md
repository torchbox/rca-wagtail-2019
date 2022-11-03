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

### Student account vs Admin account editor viewing permissions.

1. The site has custom code to show/hide fields and panels depending on if a StudentPage is viewed by an admin (superuser) or a Student (none superuser).
2. The site has custom code to show/hide sidebar elements depending on if a Student is viewing the editor vs an admin (superuser).

#### Wagtail v3 Upgrade

When the site was upgraded to Wagtail v3 the original issue at v2.15 & v2.16 noted above was fixed.

Wagtail 3 introduced a lot of Javascript generated editor template "furniture" such as the admin side bar. To accommodate hiding the search input for Student accounts the following has been implemented.

- New wagtail_hooks [global_admin_css](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/people/wagtail_hooks.py#L21) and [global_admin_js](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/people/wagtail_hooks.py#L13)
- Wagtail [Base.html](https://github.com/torchbox/rca-wagtail-2019/blob/support/wagtail-3.0-upgrade/rca/account_management/templates/wagtailadmin/base.html) override. Specifically [here](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/account_management/templates/wagtailadmin/base.html#L12) Which adds a new data-attribute for the hooks above to operate on.

Wagtail 3 introduced a new [FieldPanel `permission` parameter](https://docs.wagtail.org/en/stable/reference/pages/panels.html#wagtail.admin.panels.FieldPanel.permission) which has been use on many fields of the [StudentPage](https://github.com/torchbox/rca-wagtail-2019/blob/support/wagtail-3.0-upgrade/rca/people/models.py#L777) content_panels.

Additionally there are some Custom Panels which help to add the `permission` parameter to child FieldPanels and control panel visibility in general.

- [StudentPageInlinePanel](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/people/utils.py#L72)
- [StudentPagePromoteTab](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/people/utils.py#L86)
- [StudentPageSettingsTab](https://github.com/torchbox/rca-wagtail-2019/blob/7e5bb3c9201d8a7b7fa6e0288d4bee0ba1c79f52/rca/people/utils.py#L107)
