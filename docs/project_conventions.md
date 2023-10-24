# RCA Wagtail 2019 project conventions

## Working with dev and staging

Since phase 3.2 (September 2021) Due to RCA using `staging` as more of a UAT environment, the code and database on [`rca-staging.herokuapp.com`](https://rca-staging.herokuapp.com/) is old, much older than `production` or `dev`.

For this reason it's important to push and test code to the `dev` site only. At the time of writing this RCA are having content on `staging` reviewed and copied over from `staging`. When that process is complete we can reset `staging` to match `production` again.

To reiterate: Staging should be considered **out of action for development work and QA**. For more information check with the tech lead - Kevin.

## Git branching model

We follow a loose version of the [Git flow branching model](https://nvie.com/posts/a-successful-git-branching-model/).

- Make pull requests against: `master`
- The release prep branch is: `master`
- The client QA branch is: `dev`
- The internal QA branch is: `dev`
- Do not treat the following branches as merge sources: `dev`, `staging`

1. Make changes on a new branch, including a broad category and the ticket number if relevant e.g. `feature/123-extra-squiggles`, `fix/newsletter-signup`.
2. Push your branch to the remote.
3. Make merge requests at e.g. https://git.torchbox.com/rca/intranet.rca.ac.uk, no trailing slash/merge_requests/new, setting the 'Source branch' to your feature branch and the 'Target branch' to `master`. Select 'Compare branches and continue'.
4. Edit details as necessary.

If you need to preview work on `dev`, this can be merged and deployed manually without making a merge request. You can still make the merge request as above, but add a note to say that this is on `dev`, and not yet ready to be merged to `master`.

## Deployment Cycle

### Simple flavour

Make sure `master` contains all the desired changes (and is pushed to the remote repository and has passed CI). Deploy to production (see [deployment documentation](deployment.md)).
