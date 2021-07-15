from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.editorial import admin_forms
from rca.utils.models import BasePage, ContactFieldsMixin, RelatedPage


class EditorialPageRelatedSchoolsAndResearchPages(RelatedPage):
    source_page = ParentalKey(
        "EditorialPage", related_name="related_schools_and_research_pages"
    )
    panels = [
        PageChooserPanel("page", ["schools.SchoolPage", "research.ResearchCentrePage"])
    ]


class Author(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class EditorialPageArea(models.Model):
    page = ParentalKey("EditorialPage", related_name="areas")
    area = models.ForeignKey(
        "people.AreaOfExpertise", related_name="editorial", on_delete=models.CASCADE
    )
    panels = [FieldPanel("area")]

    def __str__(self):
        return self.area.title


class EditorialPage(ContactFieldsMixin, BasePage):
    base_form_class = admin_forms.EditorialPageAdminForm
    template = "patterns/pages/editorial/editorial_detail.html"
    introduction = models.CharField(blank=True, max_length=255)
    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    video = models.URLField(blank=True)
    video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text="The text displayed next to the video play button",
    )
    introduction_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    author = models.ForeignKey(
        "editorial.Author",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    published_at = models.DateField()
    contact_email = models.EmailField(blank=True, max_length=254)

    body = StreamField(
        [
            ("heading", blocks.CharBlock()),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("embed", EmbedBlock()),
        ],
        blank=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        ImageChooserPanel("hero_image"),
        MultiFieldPanel(
            [
                FieldPanel("video"),
                FieldPanel("video_caption"),
                ImageChooserPanel("introduction_image"),
            ],
            heading="Introductory Video",
        ),
        StreamFieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("contact_model_title"),
                FieldPanel("contact_model_email"),
                FieldPanel("contact_model_url"),
                PageChooserPanel("contact_model_form"),
                FieldPanel("contact_model_link_text"),
                FieldPanel("contact_model_text"),
                ImageChooserPanel("contact_model_image"),
            ],
            "Large Call To Action",
        ),
    ]

    key_details_panels = [
        FieldPanel("published_at"),
        MultiFieldPanel(
            [
                InlinePanel(
                    "related_schools_and_research_pages",
                    label="School or Research Centre",
                ),
                InlinePanel("areas", label="Area"),
            ],
            heading="Related School, Research Centre or Area",
        ),
        FieldPanel("author"),
        FieldPanel("contact_email"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        taxonomy_tags = []

        if self.related_schools_and_research_pages:
            for related_page in self.related_schools_and_research_pages.all():
                taxonomy_tags.append({"title": related_page.page.title})
        if self.areas:
            for area in self.areas.all():
                taxonomy_tags.append({"title": area})

        context["taxonomy_tags"] = taxonomy_tags
        context["hero_image"] = self.hero_image

        return context


class EditorialListingRelatedEditorialPage(RelatedPage):
    source_page = ParentalKey(
        "EditorialListingPage", related_name="related_editorial_pages"
    )
    panels = [PageChooserPanel("page", ["editorial.EditorialPage"])]


class EditorialListingPage(BasePage):
    template = "patterns/pages/editorial/editorial_listing.html"
    subpage_types = ["editorial.EditorialPage"]

    introduction = models.CharField(max_length=200, blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        MultiFieldPanel(
            [
                InlinePanel(
                    "related_editorial_pages", max_num=6, label="Editorial Pages"
                ),
            ],
            heading="Editors picks",
        ),
    ]

    def get_editor_picks(self, pages):
        related_pages = []
        for value in pages.select_related("page"):
            if value.page and value.page.live:
                page = value.page.specific

                meta = None
                if page.related_schools_and_research_pages.exists():
                    meta = page.related_schools_and_research_pages.first().page.title

                related_pages.append(
                    {
                        "title": page.title,
                        "link": page.url,
                        "image": page.listing_image or page.hero_image,
                        "description": page.introduction
                        if hasattr(page, "introduction")
                        else page.listing_summary,
                        "meta": meta,
                    }
                )
        return related_pages

    def get_base_queryset(self):
        return EditorialPage.objects.child_of(self).live().order_by("-published_at")

    def modify_results(self, paginator_page, request):
        for obj in paginator_page.object_list:
            obj.link = obj.get_url(request)
            obj.image = obj.listing_image or obj.hero_image
            obj.year = obj.published_at
            obj.title = obj.listing_title or obj.title
            if obj.related_schools_and_research_pages.exists():
                obj.school = obj.related_schools_and_research_pages.first().page.title

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["featured_editorial"] = self.get_editor_picks(
            self.related_editorial_pages
        )

        queryset = self.get_base_queryset().all()
        # Paginate filtered queryset
        per_page = 12

        page_number = request.GET.get("page")
        paginator = Paginator(queryset, per_page)
        try:
            results = paginator.page(page_number)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        # Set additional attributes etc
        self.modify_results(results, request)

        # Finalise and return context
        context.update(
            filters={
                "title": "Filter by",
                "aria_label": "Filter results",
                # TODO wire up filters as `items` when taxonomies are there
                "items": [],
            },
            results=results,
            result_count=paginator.count,
        )
        return context
