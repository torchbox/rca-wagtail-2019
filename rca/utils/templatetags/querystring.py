from django import template
from django.http.request import QueryDict

register = template.Library()

MODE_ADD = "__add"
MODE_REMOVE = "__remove"


@register.simple_tag(takes_context=True)
def querystring(context, base=None, remove_blanks=False, remove_utm=True, **kwargs):
    """
    Renders a URL and IRI encoded querystring (e.g. "q=Hello%20World&amp;category=1") that is safe to include in links.
    The querystring for the current request (``request.GET``) is used as a base by default, or an alternative
    ``QueryDict``, ``dict`` or querystring value can be provided as the first argument. The base value can be modified
    by providing any number of additional key/value pairs. ``None`` values are discounted automatically, and blank
    values can be optionally discounted by specifying ``remove_blanks=True``.

    When specifying key/value pairs, any keys that do not already exist in the base value will be added, and those
    that do will have their value replaced. Specifying a value of ``None`` for an existing item will result in it being
    discounted. For example, if the querystring for the current request were "foo=ORIGINALFOOVAL&bar=ORIGINALBARVAL",
    but you wanted to:

    * Change the value of "foo" to "NEWFOOVAL"
    * Remove "bar"
    * Add a new "baz" item with the value `1`

    You could do so using the following:

    ```{% querystring foo="NEWFOOVAL" bar=None baz=1 %}```

    The output of the above would be "foo=NEWFOOVAL&amp;baz=1".

    As with other template tags, values can be strings, booleans, integers or references to other variables in the
    current context. For example, if the tag were being used to generate pagination links, where the page number
    was a variable named ``page_num``, you could reference that value like so:

    ```{% querystring p=page_num %}```

    You can also specify more than one value for a key by providing an iterable as a value. For example, if the context
    contained a variable ``tag_list``, which was list of 'tag' values (```['tag1', 'tag2', 'tag3']```), you include all
    of those values by referencing the list value. For example:

    ```{% querystring tags=tag_list %}```

    The output of the above would be "tags=tag1&amp;tags=tag2&amp;tags=tag3" (plus whatever other values were in the
    base value).
    """
    querydict = get_base_querydict(context, base)
    for key, value in kwargs.items():
        if key.endswith(MODE_ADD):
            key = key[: -len(MODE_ADD)]
            values = set(querydict.get_list(key))
            if value not in values:
                values.add(value)
                querydict.set_list(list(values))
            continue

        if key.endswith(MODE_REMOVE):
            key = key[: -len(MODE_REMOVE)]
            values = set(querydict.get_list(key))
            if value in values:
                values.remove(value)
                querydict.set_list(list(values))
            continue

        if value is None:
            querydict.pop(key, None)
        else:
            if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
                querydict.setlist(key, list(value))
            else:
                querydict[key] = value

    clean_querydict(querydict, remove_blanks, remove_utm)

    return f"?{querydict.urlencode()}"


def get_base_querydict(context, base):
    if base is None and "request" in context:
        return context["request"].GET.copy()
    if isinstance(base, QueryDict):
        return base.copy()
    if isinstance(base, dict):
        return QueryDict.fromkeys(base, mutable=True)
    if isinstance(base, str):
        return QueryDict(base, mutable=True)
    # request not present or base value unsupported
    return QueryDict("", mutable=True)


def clean_querydict(querydict, remove_blanks=False, remove_utm=True):
    remove_vals = {None}
    if remove_blanks:
        remove_vals.add("")

    if remove_utm:
        for key in querydict.keys():
            if key.lower().startswith("utm_"):
                querydict.pop(key)

    for key, values in querydict.lists():
        cleaned_values = [v for v in values if v not in remove_vals]
        if cleaned_values:
            querydict.setlist(key, cleaned_values)
        else:
            del querydict[key]
