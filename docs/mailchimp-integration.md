# Mailchimp

We make use of Mailchimp's API to subscribe people as members when they submit a sign up form (rca.enquire_to_study.views.EnquireToStudyFormView).

There are two fields used to provide the enquire to study form with values we can use to better integrate with mailchimp, the `mailchimp_group_name` on programme pages and the `mailchimp_label` field within StartDate snippets.

More details on the MailChimp client [here](https://github.com/mailchimp/mailchimp-marketing-python).

## Developing

If wanting to update the mailchimp integration, request access to the mailchimp account and ask which audience list to use. They have a `Test` list which may be worth using on staging, providing that the mailchimp sign up forms match the list you wish to use on production.

### API keys & IDs

You can get the `MAILCHIMP_API_KEY` from their mailchimp account or from the heroku config.
For info on finding the `MAILCHIMP_LIST_ID` read this [article](https://mailchimp.com/help/find-audience-id/).
To get the `MAILCHIMP_PROGRAMMES_INTEREST_CATEGORY_ID` value which is used to map values from the `mailchimp_group_name` field to values within a mailchimp "group", you will have to use the snippet below as group ids are currently only available via the API.

```python
from mailchimp_marketing import Client
mailchimp = Client()
mailchimp.set_config(
    {
        "api_key": settings.MAILCHIMP_API_KEY,
        "server": settings.MAILCHIMP_API_KEY.split("-")[-1],
    }
)
mailchimp.get_list_interest_categories(MAILCHIMP_LIST_ID)
```

You're interested in the `id` value for which `title` matches the one in mailchimp i.e. 'Programme of interest'. Set `MAILCHIMP_PROGRAMMES_INTEREST_CATEGORY_ID` to this value (i.e. `0da07d9429`).

Example response:

```python
'categories':
    [
        {
            'list_id': '07bbaca3ef',
            'id': '0da07d9429',
            'title': 'Programme of interest',
    ...
```

You an use the endpoint below to confirm the ID works.

```python
mailchimp.lists.list_interest_category_interests(settings.MAILCHIMP_LIST_ID, MAILCHIMP_PROGRAMMES_INTEREST_CATEGORY_ID)
```
