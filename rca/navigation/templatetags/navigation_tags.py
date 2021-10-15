import logging

from django import template

from rca.navigation.templatetags import utils

logger = logging.getLogger(__name__)
register = template.Library()


# Primary nav snippets
@register.inclusion_tag(
    "patterns/molecules/navigation/primarynav.html", takes_context=True
)
def primarynav(context):
    request = context["request"]
    settings = context["settings"]

    links = settings["navigation"]["NavigationSettings"].primary_navigation
    items = []

    for link_block in links:
        if link_block.block_type != "link" or not link_block.value["primary_link"]:
            continue
        page = link_block.value["primary_link"]["page"]
        title = link_block.value["primary_link"]["title"]
        if page:
            url = page.get_url(request)
        else:
            url = link_block.value["primary_link"]["url"]
        if not title and page:
            title = page.title

        # Add the sub links
        sub_pages = link_block.value["secondary_links"]
        secondary_links = []
        if sub_pages:
            for link in sub_pages:
                if not link["page"] and not link["url"]:
                    continue
                sub_url = link["page"].get_url(request) if link["page"] else link["url"]
                sub_title = link["title"]
                if not sub_title:
                    sub_title = link["page"].title

                # Add the teritiary links
                tertiary_pages = link["tertiary_links"]
                tertiary_links = []
                if tertiary_pages:
                    for i in tertiary_pages:
                        if not i["page"] and not i["url"]:
                            logger.warning(
                                "A page has been deleted that is still referenced in the navigation."
                            )
                            continue
                        tertiary_url = (
                            i["page"].get_url(request) if i["page"] else i["url"]
                        )
                        tertiary_page = i["page"].pk if i["page"] else None
                        tertiary_title = i["title"]
                        if not tertiary_title:
                            tertiary_title = i["page"].title
                        tertiary_links.append(
                            {
                                "page": tertiary_page,
                                "text": tertiary_title,
                                "url": tertiary_url,
                            }
                        )

                secondary_links.append(
                    {
                        "page": link["page"].pk if link["page"] else None,
                        "text": sub_title,
                        "url": sub_url,
                        "tertiary_links": tertiary_links,
                    }
                )
        items.append(
            {
                "page": page,
                "text": title,
                "url": url,
                "secondary_links": secondary_links,
            }
        )

    return {"primarynav": items}


# Header nav snippets
@register.simple_tag(takes_context=True)
def audience_links(context):
    request = context["request"]

    settings = context["settings"]
    audience_links = settings["navigation"]["NavigationSettings"].quick_links
    audience_link_items = []
    for link in audience_links:
        link = link.value
        title = link["title"]
        if not title:
            title = link["page"].title
        url = link["page"].get_url(request) if link["page"] else link["url"]
        audience_link_items.append(
            {
                "url": url,
                "text": title,
                "page": link["page"].pk if link["page"] else None,
                "sub_text": link["sub_text"],
            }
        )

    return audience_link_items


# Footer nav snippets
@register.inclusion_tag(
    "patterns/molecules/navigation/footernav.html", takes_context=True
)
def footernav(context):
    request = context["request"]
    settings = context["settings"]
    links = settings["navigation"]["NavigationSettings"].footer_navigation
    items = utils.process_link_block(links, request)
    return {"footernav": items}


# Footer nav snippets
@register.inclusion_tag(
    "patterns/molecules/navigation/sidebar.html", takes_context=True
)
def sidebar(context):
    return {
        "children": context["page"].get_children().live().public().in_menu(),
        "request": context["request"],
    }


# Footer nav snippets
@register.inclusion_tag(
    "patterns/molecules/navigation/footerlinks.html", takes_context=True
)
def footerlinks(context):
    request = context["request"]
    settings = context["settings"]
    links = settings["navigation"]["NavigationSettings"].footer_links
    items = utils.process_link_block(links, request)
    return {"footerlinks": items}
