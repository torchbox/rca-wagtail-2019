from urllib.parse import urlencode

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.text import slugify
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
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.editorial import admin_forms
from rca.editorial.utils import get_linked_taxonomy
from rca.people.filter import SchoolCentreDirectorateFilter
from rca.people.models import Directorate
from rca.programmes.models import Subject
from rca.research.models import ResearchCentrePage
from rca.schools.models import SchoolPage
from rca.utils.blocks import (
    AccordionBlockWithTitle,
    CallToActionBlock,
    GalleryBlock,
    QuoteBlock,
)
from rca.utils.filter import TabStyleFilter
from rca.utils.models import BasePage, ContactFieldsMixin

from .blocks import EditorialPageBlock


class Author(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class EditorialType(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(EditorialType, self).save(*args, **kwargs)

    panels = [FieldPanel("title")]


class EditorialPageTypePlacement(models.Model):
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


class EditorialPageSubjectPlacement(models.Model):
    page = ParentalKey("EditorialPage", related_name="subjects")
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name="editorial_pages",
    )
    panels = [FieldPanel("subject")]


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

    body = StreamField(EditorialPageBlock())
    cta_block = StreamField(
        [("call_to_action", CallToActionBlock(label="text promo"))],
        blank=True,
        verbose_name="Text promo",
    )
    quote_carousel = StreamField(
        [("quote", QuoteBlock())], blank=True, verbose_name="Quote Carousel"
    )
    gallery = StreamField(
        [("slide", GalleryBlock())], blank=True, verbose_name="Gallery"
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
        blank=True, max_length=125, help_text="The text displayed as the download link",
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
        StreamFieldPanel("cta_block"),
        StreamFieldPanel("quote_carousel"),
        StreamFieldPanel("gallery"),
        MultiFieldPanel(
            [
                FieldPanel("more_information_title"),
                StreamFieldPanel("more_information"),
            ],
            heading="More information",
        ),
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
                InlinePanel("related_schools", label="Related Schools"),
                InlinePanel(
                    "related_research_centre_pages", label="Related Research Centres "
                ),
                InlinePanel("related_directorates", label="Area / Directorate"),
            ],
            heading="Related School, Research Centre or Area",
        ),
        InlinePanel("subjects", label="Subject"),
        InlinePanel("editorial_types", label="Editorial Type"),
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

        # Link taxonomy/page relations to a parent page so they can be clicked
        # and applied as filters on the parent listing page
        context["taxonomy_tags"] = get_linked_taxonomy(self, request)
        context["hero_image"] = self.hero_image

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
    panels = [PageChooserPanel("page")]


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

    def get_editor_picks(self):
        related_pages = []
        pages = (
            self.related_editorial_pages.all()
            .prefetch_related("page__hero_image", "page__listing_image")
            .filter(page__live=True)
        )
        for value in pages:
            page = value.page
            if page:
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
            "subject": request.GET.getlist("subject"),
            "school_or_centre": request.GET.getlist("school-centre-or-area"),
        }

    def get_extra_query_params(self, request, active_filters):
        extra_query_params = []
        for filter_name in active_filters:
            for filter_id in active_filters[filter_name]:
                extra_query_params.append(urlencode({filter_name: filter_id}))
        return extra_query_params

    def get_base_queryset(self):
        return EditorialPage.objects.child_of(self).live().order_by("-published_at")

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
            TabStyleFilter(
                "Subject",
                queryset=(
                    Subject.objects.filter(
                        id__in=base_queryset.values_list(
                            "subjects__subject_id", flat=True
                        )
                    )
                ),
                filter_by="subjects__subject__slug__in",
                option_value_field="slug",
            ),
        )
        # Apply filters
        for f in filters:
            queryset = f.apply(queryset, request.GET)

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
