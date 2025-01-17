from django.utils.html import mark_safe
from wagtail.admin.forms import WagtailAdminPageForm


class RCAPageAdminForm(WagtailAdminPageForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if seo_title_field := self.fields.get("seo_title"):
            seo_title_field.required = True
            seo_title_field.max_length = 80
            seo_title_field.help_text = mark_safe(
                "This is displayed as the clickable headline of the search snippet on search engine results pages "
                "(SERPs). It's important for UX, SEO and social shares. The text '| Royal College of Art' is "
                "appended automatically and should not be repeated here. <strong>Recommended length: 50–60 "
                "characters</strong>."
            )

        if search_description_field := self.fields.get("search_description"):
            search_description_field.required = True
            search_description_field.max_length = 160
            search_description_field.help_text = mark_safe(
                "This is displayed as part of the search snippet on SERPs. Its purpose is to give an idea of the "
                "content users can expect to find on the page. <strong>Recommended length: 50 to 160 "
                "characters</strong>."
            )

        # Listing Image field configuration
        if listing_image_field := self.fields.get("listing_image"):
            listing_image_field.required = True
            listing_image_field.help_text = "This image is required for listings."

        # Social Image field configuration
        if social_image_field := self.fields.get("social_image"):
            social_image_field.required = True
            social_image_field.help_text = "You must specify a social image."

        # Social Text field configuration
        if social_text_field := self.fields.get("social_text"):
            social_text_field.required = True
            social_text_field.help_text = "You must specify a social text."
