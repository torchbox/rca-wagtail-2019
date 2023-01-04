## Resetting the Development site

Steps for resetting the `dev` git branch, and deploying it with a cloned/anonymised copy of the production site database and media files.

### Pre-flight checks

1. Is this okay with the client, and other developers?
2. Is there any test content on staging that may need to be recreated, or be a reason to delay?
3. What branches are currently merged to staging?

   ```bash
   $ git branch -a --merged origin/staging > branches_on_staging.txt
   $ git branch -a --merged origin/master > branches_on_master.txt
   $ diff branches_on_{master,staging}.txt
   ```

   Take note if any of the above are stale, not needing to be recreated.

   or use this tool [https://git.torchbox.com/alex.bridge/misc-utils](https://git.torchbox.com/alex.bridge/misc-utils)

4. Are there any user accounts on staging only, which will need to be recreated? Check with the client, and record them.
5. Make a copy of the staging site `Wagtail Site records` urls and site names.
6. Take a backup of staging
   ```bash
   $ heroku pg:backups:capture -a [app-staging-name]
   ```

A CI/CD Job is available to copy the production database to the development environment. **Do make sure to follow the above pre-flight checks before using the job!** It will copy across the database as well as the media files.

### Git

1. Reset the dev branch
   ```bash
   $ git checkout dev && git fetch && git reset --hard origin/master && git push --force
   ```
2. Tell your colleagues
   > @here I have reset the dev branch. Please delete your local dev branches
   >
   > ```
   > $ git branch -D dev
   > ```
   >
   > to avoid accidentally merging in the old version
3. Force-push to Heroku, otherwise CI will later fail `$ git push --force heroku-development master` (this will trigger a deployment, bear in mind that there may be incompatibilities between the old staging database and the new code from master; this will be resolved in the Database step below)
4. Merge in the relevant branches that need to be added back on staging.
   ```bash
   $ git merge --no-ff origin/feature/123-extra-spangles
   ```
   You may need to create merge migrations here depending on the type of work you need to merge.

### Cleanup

1. Check the staging site loads
2. Update the Wagtail Site records, as the database will contain the production URLs

### Comms

1. Inform the client of the changes, e.g.
   > All user accounts have been copied across, so your old staging password will no longer work. Log in with your production password (and then change it), or use the 'forgot password' feature.
   > Any test content has been reset. This is probably the biggest inconvenience. Sorry.
   > I have deleted the personally-identifying data from form submissions **and anywhere else relevant**. If there's any more on production (there shouldn't be) then please let me know and I'll remove it from staging.
