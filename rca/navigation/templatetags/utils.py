def process_link_block(links, request):
    items = []
    for link_block in links:
        if link_block.block_type != "link":
            continue
        value = link_block.value
        title = value["title"]
        if not title:
            title = value["page"].title
        url = value["url"] if value["url"] else value["page"].get_url(request)
        items.append(
            {
                "page": value["page"].pk if value["page"] else None,
                "text": title,
                "url": url,
            }
        )
    return items
