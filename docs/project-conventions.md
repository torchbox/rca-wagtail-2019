# RCA Wagtail 2019 project conventions

## Git branching model

We follow a loose version of the [Git flow branching model](https://nvie.com/posts/a-successful-git-branching-model/).

- Make pull requests against: `master`
- The release prep branch is: `master`
- The client QA and internal QA branch is: `staging`
- Do not treat `staging` as a merge source.

1. Make changes on a new branch, including a broad category and the ticket number if relevant e.g. `feature/123-extra-squiggles`, `fix/newsletter-signup`.
2. Push your branch to the remote.
3. Make merge requests to `master` setting the 'Source branch' to your feature branch and the 'Target branch' to `master`. Select 'Compare branches and continue'.
4. Edit details as necessary.

If you need to preview work on `staging`, this can be merged and deployed without making a merge request. You can still make the merge request as above, but apply the label 'on-staging' to say that this is on staging, and not yet ready to be merged to `master`.

## Deployment Cycle

### Simple flavour

Make sure `master` contains all the desired changes (and is pushed to the remote repository and has passed CI). Deploy to production (see [deployment documentation](deployment.md)).
