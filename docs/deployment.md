# RCA Wagtail 2019 — hosts and deployment

The VM comes preinstalled with Fabric, Heroku CLI and AWS CLI.

## Deployed environments

| Environment                        | Branch    | URL                                        | Heroku                 |
| ---------------------------------- | --------- | ------------------------------------------ | ---------------------- |
| Production                         | `master`  | e.g. https://chi.org                       | e.g. `chi-production`  |
| Staging (considered out of action) | `staging` | e.g. https://chi.staging.torchbox.com      | e.g. `chi-staging`     |
| Development                        | `dev`     | e.g. https://chi-development.herokuapp.com | e.g. `chi-development` |

## Login to Heroku

Please log in to Heroku before executing any commands for servers hosted there
using the `Heroku login -i` command. You have to do it both in the VM and your
host machine if you want to be able to use it in both places.

## Scheduled tasks

When you set up a server you should make sure the following scheduled tasks are set.

- `django-admin publish_scheduled_pages` - every 10 minutes or more often. This is necessary to make publishing scheduled pages work.
- `django-admin fetch_access_planit_data` - every 10 minutes or more often.
- `django-admin clearsessions` - once a day (not necessary, but useful).
- `django-admin update_index` - once a day (not necessary, but useful to make sure the search index stays intact).
