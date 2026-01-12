# Support runbook

This document describes possible ways in which the system may fail or malfunction, with instructions how to handle and recover from these scenarios.

This runbook is supplementary to the [general 24/7 support runbook](https://intranet.torchbox.com/propositions/design-and-build-proposition/delivering-projects/dedicated-support-team/247-support-out-of-hours-runbook/), with details about project-specific actions which may be necessary for troubleshooting and restoring service.

See also our [incident process](https://intranet.torchbox.com/propositions/design-and-build-proposition/delivering-projects/application-support/incident-process/) if you're not already following this.

**Note: Remove the above intranet references if this project will be supported by the client's team, or handed to a third party for support. Consider whether to incorporate any scenarios from the general runbook in these cases.**

## Support resources

- Git repositories:
  - [Project repository](https://github.com/torchbox/rca-wagtail-2019)
- Papertrail logs:
  - [Production](https://my.papertrailapp.com/systems/rca-production/events)
  - [Development](https://my.papertrailapp.com/systems/rca-staging/events) - note, we do not use staging at all - it's held as a UAT environment.
  - [Development](https://my.papertrailapp.com/systems/rca-development/events)
- [Sentry project](https://sentry.io/organizations/torchbox/issues/?project=1542908)
- S3 buckets:
  - `rca-media2.rca.ac.uk`
  - `buckup-rca-staging`
  - `buckup-rca-development`

## SSO

SSO has been added using `social-auth-app-django`. This handles logging in and creating of the necessary user -- see `SOCIAL_AUTH_PIPELINE` in `rca.settings.base`.

The Azure environment is handled by RCA. If we need to update keys or redirect URLs, we'll need to contact RCA.

## Enquire to study form throwing 500s:

### 1. Check the data

The programme values the user select on the form have 'qs_code` values in Wagtail. As do some of the taxonomies. These 'qs_codes' and to lookup data from the QS endpoint. Usually the form throws 500s if these values change on the QS side but aren't updated in Wagtail. You can view the QS endpoint and inspect what codes a course should have - the endpoint is set as an env var in heroku.

If it turns out a programme/course has the wrong QS code, update it in wagtail with the right one from the endpoint.

## Personalised CTAs

### CTA Not Appearing

Check the following:

1. **Segment rules**: Verify the user meets segment criteria

- Check `get_segment_adapter(request).get_segments()`

2. **Page type**: Ensure CTA is configured for the current page type

3. **Scheduling**: Verify go-live and expiry dates

- CTAs won't show before go-live or after expiry or if those fields are left blank

4. **Priority**: Only the first matching CTA per type is shown

- Check if another CTA is being selected first

### CTA Showing Incorrectly

1. **Verify segment configuration**: Check if segment rules are too broad
2. **Check page type selection**: Ensure correct page types are selected
3. **Review scheduling**: Confirm dates are set correctly
4. **Clear cache**: If using page caching, clear it
