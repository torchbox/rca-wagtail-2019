# Programme Page

The new programme page will feature many fields and will be split out into 'tabs' as sections on the front end. The programme page form should be split out into the sections in the page form:

- Programme overview
- Curriculum
- Requirements
- Fees and Funding
- Apply
- Contact us

Due to the large amount of feilds, we will need to utilize blocks and FK relationships as much as possible.

### Programme Overview

Features a 'preview' of the pathways information added in Curriculum

### Breadcrumb

TODO, probably work from the school taxonomy of a link field?

### Taxonomy

The new Programme Page will use the following taxonomies

- Programme Type (Used to show related programmes at the foot of the page)
  - Animation
  - Architecture
    ...
- Degree levels

  - MA
    ...

- Schools (For phase 1, used in the breadcrumb)
  - School of architecture
  - School of Arts & Humanities
    ...

The old taxonomy values will need copying over from the current live site.

### Links

- [Field spec](https://docs.google.com/spreadsheets/d/1DOIRsxvQd67Frr_zNqG0zWGLfljJMvd_oru9h4L-qE8/edit#gid=190429136)
- [Functional spec](https://docs.google.com/document/d/1ZZfvg_2NqfU1mHFYpb73uaCOrlI23aSVz0oZoFX_Tuc/edit?ts=5d3afefd#heading=h.sxufov4gsz5k)

### Content relationships.

The new programme page will feature some areas for related content. These are to be related by the taxonomy programme type, the models will be:

- StaffIems
- AlumniStories (which are StandardPage tagged with 'story-page')
- EventItems
- NewsItem

The plan for implementing these is:

- Update the current API to enable filtering the page listing to give us the required content for each model, eg
  `/api/v2/pages/?type=rca.NewsItem&related_programme=[programme_taxonomy_id]`
- Override the `get_context()` method on the model to request content from the api using `self.programme_taxonomy` and deliver it to the template

This was confirmed possible during a spike. Exsiting work can be seen on the following branches:

- This repo, `kevin/spike-api-pull`
- verdant-rca repo `spike/api-relate-programme-filter`
