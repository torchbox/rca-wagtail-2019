# RCA - Anonymising data

When pulling data from any hosted instance, take a cautious approach about whether you need full details of potentially personally-identifying, confidential or sensitive data.

## General principles:

- Pull data from staging rather than production servers, if this is good enough for your needs
- If it is necessary to pull data from production, e.g. for troubleshooting, consider whether anonymising personal data is possible and compatible with your needs
- If it is necessary to pull non-anonymised data from production, consider destroying this copy of the data as soon as you no longer need it

In more sensitive cases, consider a data protection policy to prevent access to production data except for authorised users.

## Anonymise

`django-birdbath` provides a management command (`run_birdbath`) that will anonymise the database.

As and when models/fields are added that may be populated with sensitive data (such as email addresses) a processor should be added to ensure that the data can be anonymised or deleted when it is copied from the production environment.

For full documentation see https://git.torchbox.com/internal/django-birdbath/-/blob/master/README.md.

The `flightpath` tool can be used to copy production data (and media) from the production environment to staging. It will automatically `run_birdbath` immediately following this sync operation. A manual CI action is included that will trigger flightpath to sync the environments.

Intended workflow:

1. Production data is synced to rca-development by flightpath
   - Birdbath anonymises rca-development database
2. Anonymised data is pulled from **rca-production** to rca-development environments

This workfow should mean that un-anonymised data is never present on a developer's machine. If data directly from **production** is required, then `run_birdbath` command should be run immediately after download.

## Student User Account Anonymisation

Student User Accounts are anonymised in the usual way by updating the fields using fake data.

As a student account can also have a related StudentPage, these are also anonymised by using fake data or removing related personal records.

As user groups and collections are created when each student is created they are also anonymised by using the fake data from a student user account (username)
