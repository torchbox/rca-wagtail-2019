## Resetting the Staging site

Steps for resetting the `staging` git branch, and deploying it with a cloned/anonymised copy of the production site database and media files.

### Pre-flight checks

1. Is this okay with the client, and other developers?
2. Is there any test content on `staging` that may need to be recreated, or be a reason to delay?
3. What branches are currently merged to staging?

   ```bash
   $ git branch -a --merged origin/staging > branches_on_staging.txt
   $ git branch -a --merged origin/master > branches_on_master.txt
   $ diff branches_on_{master,staging}.txt
   ```

   Take note if any of the above are stale, not needing to be recreated.

4. Are there any user accounts on staging only, which will need to be recreated? Check with the client, and record them.
5. Make a copy of the staging `Wagtail Site records` urls and site names.
6. Take a backup of staging
   ```bash
   $ heroku pg:backups:capture -a rca-staging
   ```

### Git

1. Reset the staging branch
   ```bash
   $ git checkout staging && git fetch && git reset --hard origin/master && git push --force
   ```
2. Tell your colleagues
   > @here I have reset the staging branch. Please delete your local staging branches
   >
   > ```
   > $ git branch -D staging
   > ```
   >
   > to avoid accidentally merging in the old version
3. Force-push to Heroku, otherwise CI will later fail `$ git push --force heroku-staging master` (this will trigger a deployment, bear in mind that there may be incompatibilities between the old staging database and the new code from master; this will be resolved in the Database step below)
4. Merge in the relevant branches that need to be added back on staging.
   ```bash
   $ git merge --no-ff origin/feature/123-extra-spangles
   ```
   You may need to create merge migrations here depending on the type of work you need to merge.

## Database

1. To copy the production database over to staging, run the management command `./manage.py copy_db_to_staging` from the Heroku console on staging
   This is a destructive action. Proofread it thoroughly.
2. To copy media across as well as data, you can use the optional argument `--media` with the above command, using a value of 1, e.g. `--media=1`
3. By default, a backup of the staging database is created before the database is copied. If you don't want this behaviour, you can set the optional argument `--backup` with a value of 0, e.g. `--backup=0`
4. By default, a snapshot of the production base is taken before the database is copied. If you don't want this behaviour, you can se the option agrument `--snapshot` with a value of 0, e.g. `--snapshot=0`
5. Flightpath will anonymise the database for you at the end of the copy process.

### Cleanup

1. Check the staging site loads
2. Update the Wagtail Site records, as the database will contain the production URLs

### Comms

1. Inform the client of the changes, e.g.
   > All user accounts have been copied across, so your old staging password will no longer work. Log in with your production password (and then change it), or use the 'forgot password' feature.
   > Any test content has been reset. This is probably the biggest inconvenience. Sorry.
   > I have deleted the personally-identifying data from form submissions **and anywhere else relevant**. If there's any more on production (there shouldn't be) then please let me know and I'll remove it from staging.
