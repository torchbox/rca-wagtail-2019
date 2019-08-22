# Content relationships using the current live RCA site

The new programme page will feature some areas for related content. These are to be related by the taxonomy programme type, the models will be:

- StaffPages
- AlumniStories (which are StandardPage tagged with 'alumni-stories')
- EventItems
- NewsItem

The plan for implementing these is:

- Update the current API to enable filtering the page listing to give us the required content for each model, eg
  `/api/v2/pages/?type=rca.NewsItem&related_programme=[programme_taxonomy_id]`
- Override the `get_context()` method on the model to request content from the api using `self.programme_taxonomy` and deliver it to the template

This was confirmed possible during a spike. Exsiting work can be seen on the following branches:

- This repo, [kevin/spike-api-pull](https://github.com/torchbox/rca-wagtail-2019/tree/kevin/spike-api-pull)
- verdant-rca repo [spike/api-relate-programme-filter](https://github.com/torchbox/verdant-rca/pull/186) This contains all the work needed to request content over the api using a filter for related programmes

## Context example

An example for adding data requested from the API in the new page models would be:

```

def get_context(self, request, *args, **kwargs):
    context = super().get_context(request, *args, **kwargs)
    # TODO query by taxonomy
    # related_programmes programme id 1 # change to slug
    url = "https://www.rca.ac.uk/api/v2/pages/?type=rca.NewsItem[filter-value]"
    resp = requests.get(url=url)
    data = resp.json()
    _data = []
    # TODO limit the api to 3 results rather than slicing
    # TODO Split to method and decorate with cache
    # see https://docs.djangoproject.com/en/2.2/topics/cache/#the-low-level-cache-api
    # Also we would need to make changes to the current API related_programmes
    for item in data["items"][:3]:
        _item = {}
        # an extra qurey for more information is needed
        detail = item["meta"]["detail_url"] + "?fields=_,date,feed_image"
        resp = requests.get(url=detail)
        data = resp.json()
        feed_image = data["feed_image"]["meta"]["detail_url"]
        feed_image = requests.get(url=feed_image)
        feed_image = feed_image.json()
        feed_image = feed_image["original"]["url"]
        date = data["date"]
        _item["title"] = item["title"]
        _item["date"] = date
        _item["image"] = feed_image
        _data.append(_item)

    context["data"] = _data
    return context

```

### Updating the RCA API

As metnioned above, we will need to update the RCA api so we can filter content by vertain criterea.

Example query for NewsItems related by the current programme page

```
/api/v2/pages/?type=rca.NewsItem&related_programme=[programme_taxonomy_slug]
```

#### For the above query to be supported we will need to do the following:

Ensure that the new ProgrammePage model has relationships similar to the current live site. For example, on the current site, a programme has a `programme taxonomy`. This taxonomy has a `slug` field which will be easier for mapping the relationship, rather than using ID. In the new site we will need a similar `programme type taxonomy` to use the same values, mainly `slug` as this will be used for the query. In psuedo code the query will breakdown like:

```
/api/v2/pages/?type=[the rca page model]&[related_programme_taxonomy]=[self.programme_taxonomy_slug]
```

#### Existing relationships on the current site

The following live RCA page models relate to programmes in the following ways:

- StaffPage > StaffPageRole > `programme`
- AlumniStories (StandardPage tagged with 'alumni-stories') > `related_programme`
- EventItems > related_programmes
- NewsItem > related_programmes

Example for implementing new query support is https://github.com/torchbox/verdant-rca/pull/186/files

#### Example queries:

##### EventItems

http://0.0.0.0:8000/api/v2/pages/?type=rca.EventItem&rp=animation

##### NewsItem

http://0.0.0.0:8000/api/v2/pages/?type=rca.NewsItem&rp=animation

##### StaffPage

http://0.0.0.0:8000/api/v2/pages/?type=rca.StaffPage&rp=animation

##### AlumniStories

StandardPage tagged with 'alumni-stories')

http://0.0.0.0:8000/api/v2/pages/?type=rca.StandardPage&rp=animation&tags=alumni-story
