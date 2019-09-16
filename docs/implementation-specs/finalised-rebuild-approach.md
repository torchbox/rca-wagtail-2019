# RCA Rebuild Implementation Spec

More information about the overall structure is in progress [here](https://docs.google.com/document/d/1C81sH3YsxsC98dC_mqMw6e3KOCgWkYPGOkl72k6qkx0/edit?ts=5d6e8bd6#)

## This page describes how we will manage the phased release requirement of the RCA rebuild.

The New RCA website will be completed in phases, the first of which will be to replace the current live home page and the individual programme pages. The end goal will be a full rebuild of the current site which will be hosted on Heroku by Torchbox and the code will be open-source on GitHub.

We have a number of implementation options for managing this phased release requirement but the following points will heavily influence the approach:

- The deadline for the first phase of work is very short and will launch September 16.
- The current site is using old versions of Django and Wagtail.
- The current site has a high amount of untested custom code.
- Content relationships (related pages).
- If there is a requirement to sync/import content from the current site.

## Our Advised Approach

From our investigation, the best approach for the rebuild will be to build a new instance where we will add the new page models and features required in each phase.

So both instances can work together, we will use Nginx Proxies to forward specific requests for certain pages to the new site. For example:

https://www.rca.ac.uk/schools/school-of-architecture/architecture/ would forward to https://www.new.rca.ac.uk/programmes/architecture/

Technical details on this can be read further below under Detailed Proxying Information

### Benefits of using a new instance

- Has the minimal impact on the deadline and cost for phase 1.
- Does not require updating the old RCA website codebase.
- Much more stable environment and codebase from the start.

### Disadvantages of the new instance approach

- Content relationship will need to be set using a system of fields rather than Page Choosers until we have the other page models and content in the new site either by migrating or syncing the content in a later phase. If and when content is later migrated or synced to the new instance, we would change content relationships using fields to use page choosers in later phases.
- Increase in hosting cost for 2 sites.
- Publishers will need to sign in to the new site when editing models that have been updated, this would be a gradual shift as we complete the phases. \

### What are the SEO impacts of using 2 instances?

None, search engine crawlers will follow the redirects we put in place to forward people to pages on the new site. This means that the new content will eventually be indexed. We are discussing this with our search and analytics team for further confidence.

Google will treat the subdomain as it's own entity. Some authority may be shared from the root domain, and any backlinks from the old redirected URLs will also pass over to the new subdomain. We may see a decrease in traffic as it is similar to a small scale migration, but there are a few things we will do to minimise drops, such as informing Google of the change via GSC and going through the migration steps.

### Site Search

For Phase 1, the site search on the new site will be a simple form that submits to the current live site. The design changes have auto-complete and search previews but that would come in a later phase.

After phase 1, we would recommend 2-3 days of development work is carried out to enhance the site search so we can index and query both instances. This would involve updates to Elastic Search but a better, long term option for indexing would be to switch to [Algolia](https://www.algolia.com/).

### Detailed proxying information

As mentioned above we will forward users from the current live site to the new site. Usually, we would advise using [Cloudflare](https://www.cloudflare.com/) for this, however, setting up Cloudflare on a site that has already been launched can be time-consuming and depends on RCA having control over the name servers.

Using Cloudflare typically requires switching DNS to name servers that CloudFlare control; however, rca.ac.uk has JANET DNS name servers, which RCA may not be able to change.

If it’s possible to use Cloudflare there will need to be a CNAME from www.rca.ac.uk to a Cloudflare CDN entry-point hostname. This will cost $200, as CloudFlare's CNAME capability is only available on $200 business plans.

#### What we plan to implement instead of using Cloudflare

Given the above technical complexity and the unwanted extra cost, we will set up proxying using Nginx on the current site. With Nginx, our Puppet module has the capability to insert proxy config per site, so we can proxy from Bytemark to Heroku. The extra estimated sysadmin time for this would be 3 hours

### Other points to be aware of or discussed

- In what phase will the new site support Single Sign-On?
- The main navigation is large and currently works by automatically rendering links from specific pages/sections. In the new site, this will be a manually managed menu system. Although in a later phase this can be switched.
- Torchbox will recommend what parts of the site should be rebuilt in the upcoming phases, the main concern here is importing pages that relate heavily with other pages. For example, we would want to implement Staff and Research in the same phase as they are heavily related.
- Changes to taxonomy on the old site could slow down the process.
- For future changes, we would need to refactor content relationships that use manual fields to related Page Chooser. For example, if in Phase 2 we rebuild events, we would check where events have been referenced in the new site via manual fields and swap them for page choosers. This will also involve updating the relationship itself either manually or programmatically.
- Would we need to import any content to the new site at all, or will it all be newly published?
- The intranet site is currently syncing content with the RCA site, in a later phase we will need to switch this to sync to the rebuilt website.
- We will not be importing or syncing content in Phase 1, this will happen in later phases with specific models.
