import re
from urllib.parse import urlencode

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.text import slugify
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from rca.editorial import admin_forms
from rca.editorial.utils import get_linked_taxonomy
from rca.events.serializers import (
    RelatedDirectoratesSerializer,
    RelatedSchoolSerializer,
)
from rca.people.filter import SchoolCentreDirectorateFilter
from rca.people.models import Directorate
from rca.programmes.filter import ProgrammeStyleFilter
from rca.research.models import ResearchCentrePage
from rca.schools.models import SchoolPage
from rca.utils.blocks import (
    AccordionBlockWithTitle,
    CallToActionBlock,
    GalleryBlock,
    QuoteBlock,
)
from rca.utils.filter import TabStyleFilter
from rca.utils.models import BasePage, ContactFieldsMixin, RelatedPage, StickyCTAMixin
from rca.utils.shorthand import ShorthandContentMixin

from .blocks import EditorialPageBlock
from .serializers import (
    CTABlockSerializer,
    EditorialTypeTaxonomySerializer,
    RelatedAuthorSerializer,
)


class Author(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class RelatedEditorialPage(Orderable):
    source_page = ParentalKey(Page, related_name="related_editorialpages")
    page = models.ForeignKey("editorial.EditorialPage", on_delete=models.CASCADE)

    panels = [FieldPanel("page")]


class EditorialPageRelatedProgramme(RelatedPage):
    source_page = ParentalKey("EditorialPage", related_name="related_programmes")
    panels = [PageChooserPanel("page", ["programmes.ProgrammePage"])]


class EditorialType(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    panels = [FieldPanel("title")]


class EditorialPageTypePlacement(Orderable):
    page = ParentalKey("EditorialPage", related_name="editorial_types")
    type = models.ForeignKey(
        EditorialType,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name="editorial_pages",
    )
    panels = [FieldPanel("type")]


class EditorialPageDirectorate(models.Model):
    page = ParentalKey("EditorialPage", related_name="related_directorates")
    directorate = models.ForeignKey(
        Directorate,
        on_delete=models.CASCADE,
        related_name="related_editorial_pages",
        verbose_name="Directorates",
    )
    panels = [FieldPanel("directorate")]


class EditorialPage(
    ShorthandContentMixin, ContactFieldsMixin, StickyCTAMixin, BasePage
):
    base_form_class = admin_forms.EditorialPageAdminForm
    template = "patterns/pages/editorial/editorial_detail.html"
    introduction = RichTextField(
        blank=True,
        features=(["bold", "italic"]),
        help_text="Maximum of 140 characters supported in listings",
    )
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

    body = StreamField(EditorialPageBlock(), blank=True)
    cta_block = StreamField(
        [("call_to_action", CallToActionBlock(label="text promo"))],
        blank=True,
        verbose_name="Text promo",
    )
    quote_carousel = StreamField(
        [("quote", QuoteBlock())],
        blank=True,
        verbose_name="Quote Carousel",
    )
    gallery = StreamField(
        [("slide", GalleryBlock())],
        blank=True,
        verbose_name="Gallery",
    )
    more_information_title = models.CharField(max_length=80, default="More information")
    more_information = StreamField(
        [("accordion_block", AccordionBlockWithTitle())],
        blank=True,
        verbose_name="More information",
    )
    download_assets_heading = models.CharField(
        blank=True,
        max_length=125,
        help_text="The heading text displayed above download link",
    )
    download_assets_url = models.URLField(blank=True)
    download_assets_link_title = models.CharField(
        blank=True,
        max_length=125,
        help_text="The text displayed as the download link",
    )

    show_in_index_page = models.BooleanField(
        default=True,
        help_text="Toggle to show/hide in the index page.",
    )
    show_on_home_page = models.BooleanField(
        default=True,
        help_text="Toggle to show/hide in the listing on the home page.",
    )
    show_on_landing_page = models.BooleanField(
        default=True,
        help_text="Toggle to show/hide in the listing on the landing page.",
    )

    content_panels = (
        BasePage.content_panels
        + [
            FieldPanel("introduction"),
            FieldPanel("shorthand_story_url"),
            FieldPanel("hero_image"),
            MultiFieldPanel(
                [
                    FieldPanel("video"),
                    FieldPanel("video_caption"),
                    FieldPanel("introduction_image"),
                ],
                heading="Introductory Video",
            ),
            FieldPanel("body"),
            FieldPanel("cta_block"),
            FieldPanel("quote_carousel"),
            FieldPanel("gallery"),
            MultiFieldPanel(
                [
                    FieldPanel("more_information_title"),
                    FieldPanel("more_information"),
                ],
                heading="More information",
            ),
            InlinePanel(
                "related_editorialpages", label="Related Editorial Pages", max_num=6
            ),
            MultiFieldPanel(
                [
                    FieldPanel("contact_model_title"),
                    FieldPanel("contact_model_email"),
                    FieldPanel("contact_model_url"),
                    FieldPanel("contact_model_form"),
                    FieldPanel("contact_model_link_text"),
                    FieldPanel("contact_model_text"),
                    FieldPanel("contact_model_image"),
                ],
                "Large Call To Action",
            ),
        ]
        + [StickyCTAMixin.panels]
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
        index.RelatedFields("author", [index.SearchField("name")]),
        index.SearchField("more_information"),
    ]

    key_details_panels = [
        FieldPanel("published_at"),
        MultiFieldPanel(
            [
                InlinePanel("related_schools", label="Related Schools"),
                InlinePanel(
                    "related_research_centre_pages", label="Related Research Centres "
                ),
                InlinePanel("related_directorates", label="Area / Directorate"),
            ],
            heading="Related School, Research Centre or Area",
        ),
        InlinePanel(
            "related_landing_pages",
            heading="Related Landing Pages",
            label="Landing Page",
        ),
        InlinePanel("editorial_types", label="Editorial Type"),
        InlinePanel("related_programmes", label="Programme Page"),
        FieldPanel("author"),
        MultiFieldPanel(
            [
                FieldPanel("download_assets_heading"),
                FieldPanel("download_assets_url"),
                FieldPanel("download_assets_link_title"),
            ],
            heading="Download assets",
        ),
        FieldPanel("contact_email"),
    ]
    promote_panels = BasePage.promote_panels + [
        FieldPanel("show_in_index_page"),
        FieldPanel("show_on_home_page"),
        FieldPanel("show_on_landing_page"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    api_fields = BasePage.api_fields + [
        APIField("hero_image"),
        APIField("introduction"),
        APIField("video"),
        APIField("video_caption"),
        APIField("introduction_image"),
        APIField("body"),
        APIField("cta_block", serializer=CTABlockSerializer()),
        APIField("quote_carousel"),
        APIField("gallery"),
        APIField("more_information_title"),
        APIField("more_information"),
        APIField("related_editorialpages"),
        APIField("contact_model_title"),
        APIField("contact_model_email"),
        APIField("contact_model_url"),
        APIField("contact_model_form"),
        APIField("contact_model_link_text"),
        APIField("contact_model_text"),
        APIField("contact_model_image"),
        APIField("published_at"),
        APIField("related_schools", serializer=RelatedSchoolSerializer()),
        APIField("related_research_centre_pages"),
        APIField("related_directorates", serializer=RelatedDirectoratesSerializer()),
        APIField("related_landing_pages"),
        APIField("editorial_types", serializer=EditorialTypeTaxonomySerializer()),
        APIField("related_programmes"),
        APIField("download_assets_heading"),
        APIField("download_assets_url"),
        APIField("download_assets_link_title"),
        APIField("contact_email"),
        APIField("author_as_string", serializer=RelatedAuthorSerializer()),
        "related_programmes_api",
    ]

    @property
    def listing_meta(self):
        # Returns a page 'type' value that's readable for listings,
        editorial_type = self.editorial_types.first()
        if editorial_type:
            return editorial_type.type

    def search_listing_summary(self):
        """Method to return the summary without html

        Returns:
            string: text with html tags removed
        """
        text = self.listing_summary or self.introduction
        text = re.sub("<[^<]+?>", "", text)
        return text

    def author_as_string(self):
        if self.author:
            return self.author
        else:
            return ""

    def related_programmes_api(self):
        programmes = []
        for related_page in self.related_programmes.all():
            page = related_page.page.specific
            programmes.append(
                {
                    "page": {
                        "title": page.title,
                        "id": page.id,
                        "slug": page.slug,
                        "intranet_slug": page.intranet_slug,
                    },
                }
            )
        return programmes

    def get_related_pages(self):
        related_pages = {"title": "Also of interest", "items": []}
        pages = self.related_editorialpages.all().prefetch_related(
            "page__hero_image", "page__listing_image"
        )
        for value in pages:
            page = value.page
            if not page.live:
                continue
            meta = ""
            editorial_type = page.editorial_types.first()
            if editorial_type:
                meta = editorial_type.type

            related_pages["items"].append(
                {
                    "title": page.title,
                    "link": page.url,
                    "image": page.listing_image or page.hero_image,
                    "description": page.listing_summary or page.introduction,
                    "meta": meta,
                }
            )
        return related_pages

    def has_sticky_cta(self):
        data = self.get_sticky_cta()
        return all(data.get(key) for key in ["message", "action", "link"])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["hero_image"] = self.hero_image

        if not self.shorthand_embed_code:
            # Link taxonomy/page relations to a parent page so they can be clicked
            # and applied as filters on the parent listing page
            context["taxonomy_tags"] = get_linked_taxonomy(self, request)
            if self.has_sticky_cta():
                context["sticky_cta"] = self.get_sticky_cta()
            context["related_pages"] = self.get_related_pages()
        return context


class EditorialListingRelatedEditorialPage(Orderable):
    page = models.ForeignKey(
        EditorialPage,
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name="+",
    )
    source_page = ParentalKey(
        "EditorialListingPage", related_name="related_editorial_pages"
    )
    panels = [FieldPanel("page")]


class EditorialListingPage(ContactFieldsMixin, BasePage):
    base_form_class = admin_forms.EditorialPageAdminForm
    template = "patterns/pages/editorial/editorial_listing.html"
    subpage_types = ["editorial.EditorialPage"]

    introduction = models.CharField(max_length=200, blank=True)

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
    ]

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
        MultiFieldPanel(
            [
                FieldPanel("contact_model_title"),
                FieldPanel("contact_model_email"),
                FieldPanel("contact_model_url"),
                FieldPanel("contact_model_form"),
                FieldPanel("contact_model_link_text"),
                FieldPanel("contact_model_text"),
                FieldPanel("contact_model_image"),
            ],
            "Large Call To Action",
        ),
    ]

    def get_editor_picks(self):
        related_pages = []
        pages = self.related_editorial_pages.all().prefetch_related(
            "page__hero_image", "page__listing_image"
        )
        for value in pages:
            page = value.page
            if page and page.live:
                meta = None
                school = page.related_schools.first()
                if school:
                    meta = school.page.title

                related_pages.append(
                    {
                        "title": page.title,
                        "link": page.url,
                        "image": page.listing_image or page.hero_image,
                        "description": page.introduction or page.listing_summary,
                        "meta": meta,
                    }
                )
        return related_pages

    def get_active_filters(self, request):
        return {
            "type": request.GET.getlist("type"),
            "school_or_centre": request.GET.getlist("school-centre-or-area"),
            "programme": request.GET.getlist("programme"),
        }

    def get_extra_query_params(self, request, active_filters):
        extra_query_params = []
        for filter_name in active_filters:
            for filter_id in active_filters[filter_name]:
                extra_query_params.append(urlencode({filter_name: filter_id}))
        return extra_query_params

    def get_base_queryset(self):
        return (
            EditorialPage.objects.exclude(show_in_index_page=False)
            .child_of(self)
            .live()
            .order_by("-published_at")
        )

    def modify_results(self, paginator_page, request):
        for obj in paginator_page.object_list:
            obj.link = obj.get_url(request)
            obj.image = obj.listing_image or obj.hero_image
            obj.date = obj.published_at
            obj.title = obj.listing_title or obj.title
            editorial_type = obj.editorial_types.first()
            if editorial_type:
                obj.type = editorial_type.type

    def get_context(self, request, *args, **kwargs):
        from rca.programmes.models import ProgrammePage

        context = super().get_context(request, *args, **kwargs)
        context["featured_editorial"] = self.get_editor_picks()

        base_queryset = self.get_base_queryset()
        queryset = base_queryset.all()

        filters = (
            SchoolCentreDirectorateFilter(
                "School, Centre or Area",
                school_queryset=SchoolPage.objects.live().filter(
                    id__in=base_queryset.values_list(
                        "related_schools__page_id", flat=True
                    )
                ),
                centre_queryset=ResearchCentrePage.objects.live().filter(
                    id__in=base_queryset.values_list(
                        "related_research_centre_pages__page_id", flat=True
                    )
                ),
                directorate_queryset=Directorate.objects.filter(
                    id__in=base_queryset.values_list(
                        "related_directorates__directorate_id", flat=True
                    )
                ),
            ),
            TabStyleFilter(
                "Type",
                queryset=(
                    EditorialType.objects.filter(
                        id__in=base_queryset.values_list(
                            "editorial_types__type_id", flat=True
                        )
                    )
                ),
                filter_by="editorial_types__type__slug__in",
                option_value_field="slug",
            ),
            ProgrammeStyleFilter(
                "Programme",
                queryset=(
                    ProgrammePage.objects.filter(
                        id__in=base_queryset.values_list(
                            "related_programmes__page_id", flat=True
                        )
                    )
                ),
                filter_by="related_programmes__page__slug__in",
                option_value_field="slug",
            ),
        )
        # Apply filters
        for f in filters:
            queryset = f.apply(queryset, request.GET)

        queryset = queryset.distinct()

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
                "items": filters,
            },
            results=results,
            result_count=paginator.count,
        )
        context["show_picks"] = True
        extra_query_params = self.get_extra_query_params(
            request, self.get_active_filters(request)
        )
        if extra_query_params or (page_number and page_number != "1"):
            context["show_picks"] = False

        return context
