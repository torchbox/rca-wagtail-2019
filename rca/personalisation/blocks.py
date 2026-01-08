from wagtail import blocks


class CollapsibleNavigationLinkBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock()
    title = blocks.CharBlock(
        required=False, max_length=25, help_text="Leave blank to use page title."
    )

    class Meta:
        icon = "link"
