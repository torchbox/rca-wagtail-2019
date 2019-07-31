Initial investigation notes for rebuild options considered.
Refer to 'Finalised rebuild approach' for the implementation.

# **RCA Initial Rebuild Approach Investigation**

## **Overview**

The New RCA website will be completed in phases, the first of which will be to replace the current live home page and the individual programme pages (not sections/listings yet). The end goal will be a full rebuild of the current site which will be hosted on Heroku by Torchbox and the code will be hosted on GitHub.

We have a number of implementation options for managing this phased release requirement but the following points will heavily influence the approach:

- The deadline for the first phase of work is very short and will launch September 16.
- The current site is using old versions of Django and Wagtail.
- The current site has a lot of untested custom code.
- Content relationships
- At some point, we will need to migrate or import the old content into the new site.
- If we need to relate and sync content (see below) from phase 1.
- Auto-complete and preview of site search
- Searching for programmes on the new instance will need redirects putting in place.
- Navigation, we will need to decide upon a manual navigation system or hardcoded in the template.

The old sites content is heavily related, programmes have related pages, taxonomy, and related models for sections like key details and how to apply.

In phase 1, RCA is still considering if it will be acceptable to manually add content links to the current site from the new one. For example, if a programme has a related 'staff' item, this would be a system of fields the publisher would fill in. This is fine for the home page but the programme page is under discussion. More details and suggestions about this are below under Page Choosers

---

## **Options for Phase 1**

The work in Phase 1 will see us replace the following models with new ones

- HomePage
- Programme

For this Phase we have the following options:

- Implement the new models on the current site.
- Create and host a new instance with the new models.

Implementing the new models on the current site has less effect on the deadline, however, we will be working with old technology and could see problems implementing new features, especially with the Front End as the design is completely new.

Should we decide to host start with a new instance in phase 1, we will need to decide an approach to take hosting both the current and new instances at the same time...

### **1. Create and host a new instance with the new models.**

#### **Using Cloudflare or Nginx Proxy**

##### **Cloudflare**

We can set up Cloudflare on the current live site with a worker that will proxy specific URLs to the new instance...

- The live domain gets routed through Cloudflare.
- Requests to any paths eg /programmes/architecture get put through a Cloudflare Worker.
- The worker proxies the request through to the new instance and caches the response in Cloudflare.

Possible issue with this approach:

- Cache purging.
- If RCA wants to add a new programme, they will have to create it in both instances. Although we have been assured RCA will be replacing programmes by publishing them Should we decide to host start with a new instance in phase 1, we will need to decide an approach to take hosting both the current and new instances at the same time

This will not have an effect on the search indexing as google will follow Cloudflare and only index the new pages.

##### **Nginx Proxy**

If we cannot use Cloudflare on the old site we can proxy using Nginx or ATS. This will involve mapping specific URLs/requests for https://www.rca.ac.uk/ to https://www.newsite.rca.ac.uk/

Other sites that had similar requirements are:

- Hotjar - Blog section only
- Hamilton trust - Phased release, the home page being the last phase.

##### **Pros**

- No updates to the new site will be needed as the new work will be on a new instance.
- Faster setup and implementation of new models.
- Less likely to encounter unknown issues.
- Much more stable codebase.

##### **Cons**

- Content relationships would only be possible if we use the sync module from the intranet site and copy the required models over.
- We would create a very bespoke and custom situation without knowing an end date. This could create problems should the rest of the rebuild be delayed.

### **2. Build the new instance inside the current wagtail site.**

Another approach would be to host the new instance _inside_ the current site. For this the following step would need to be taken for this:

- Write tests for current models and custom code.
- Update Wagtail and Django.
- Fix the now failing tests.
- Update the codebase with all the up to date tooling we use (pattern library, fabric, aws bucket etc).
- Move the site to Heroku.
- Implement the new models.

##### **Pros**

- No need for Cloudflare.
- No need for content syncing and content relationships could use page choosers.

##### **Cons**

- The increased workload for phase 1 will likely push the deadline unless we have more developer resources.
- Higher cost for phase 1 to RCA
- An unknown amount of problems with the upgrade of Wagtail and Django.
- Lot's of custom code would need testing and fixing.
- We would need to update the intranet syncing code to work from the new Heroku site. Eventually, we will need to do this whatever option we choose though.

---

### **Page Choosers**

The new website will, at some point, need page choosers to select and relate content from elsewhere in the site, however, content needs to be available _in_ the new instance in order for it to be selected. A solution to this has already been implemented on the intranet site. It works by periodically importing/syncing content with the current live RCA site. This gives us the following choices of approach:

#### **1: Implement page choosers and relationships from the start**

For page choosers to be supported on the new instance from the start the following work would need to be completed:

- Copy all the models we want to sync to the new instance and refactor them into apps.
- Implement the same syncing functionality from the intranet. Can be found [here](https://git.torchbox.com/rca/intranet.rca.ac.uk/tree/master/inforca/content/sync)
- Implement either the intranet [content importer](https://git.torchbox.com/rca/intranet.rca.ac.uk/tree/master/inforca/admin/content_importer/static/content_importer) or @gasmans new [generic page chooser](https://github.com/wagtail/wagtail-generic-chooser)

##### **Pros**

- Doing this at the start means we won't need to pick it further down the line and will help us solve potential problems sooner.
- All related content areas on the new models will use page choosers, eg selecting 'Events' on the home page will look for imported/synced content.

##### **Cons**

- We will be using old code (syncing module) that may need debugging/fixing to work with a newer instance of Wagtail.
- It will add a significant amount of time to the first phase.
- We will need to copy over every model we want to support importing/syncing. For example, we would copy the blog page model to the new instance so we can import blog content. This would need to be done for every item we want to import.

#### **2: Using the new Wagtail Generic Page Chooser**

@gasmans new [generic page chooser](https://github.com/wagtail/wagtail-generic-chooser) can read from an API. So a solution could be to use this and read from the current live sites API and once the content is selected, import it.

##### **Pros**

- No manual content linking from the start.
- Importing items gradually starts in phase 1.

##### **Cons**

- We would need to extend the chooser to import and create content selected from the API.
- We may need to tweak the API on the current RCA site.

#### **3: Switching to Page Choosers in later phases**

As the content sync work would delay the first phase, the alternative approach would be to set the new models related content areas as manual fields. Meaning when an 'Event' needs to be selected to be related or embedded, the publisher will fill out an image, title, description and link (to the current live site). Then in a later phase, we would switch to page choosers and import content.

##### **Pros**

- Faster and simpler implement.
- No need to sync content in the first phase.

##### **Cons**

- Increases publishing time and complexity.
- Eventually, we will need to swap out the manual fields for page choosers anyway.

### **Navigation and global elements if we build a new instance in phase 1**

For the initial phases, the navigation elements will be hardcoded and will link back to the current live site. Proxying will handle linking to the new instance.

<!-- Docs to Markdown version 1.0β17 -->
