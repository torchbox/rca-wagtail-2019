from collections import defaultdict
from itertools import chain

from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils import timezone
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import VideoChooserBlock

from rca.editorial.models import EditorialPage
from rca.events.models import EventDetailPage
from rca.home.utils import partnerships_slides_formatter, related_news_events_formatter
from rca.navigation.models import LinkBlock
from rca.utils.blocks import RelatedPageListBlockPage, StatisticBlock


class StraplineBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    cta_url = blocks.URLBlock(required=False, label="Call to action URL")
    cta_text = blocks.CharBlock(required=False, label="Call to action text")

    class Meta:
        template = "patterns/molecules/streamfield/blocks/strapline_block.html"
        icon = "title"
        label = "Strapline"

    def clean(self, value):
        if not value:
            return value

        errors = defaultdict(list)
        cta_url = value.get("cta_url", "")
        cta_text = value.get("cta_text", "")

        if cta_url and not cta_text:
            errors["cta_text"].append("Please add the text to be displayed as a link")
        if cta_text and not cta_url:
            errors["cta_url"].append("Please add a URL value")

        if errors:
            raise ValidationError(errors)

        return value


class TransformationBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        max_length=125, help_text="Large heading displayed above the image"
    )
    image = ImageChooserBlock(required=False, help_text="Select an image")
    video = blocks.URLBlock(required=False, help_text="URL to a video")
    video_caption = blocks.CharBlock(
        required=False,
        max_length=80,
        help_text="The text displayed next to the video play button",
    )
    sub_heading = blocks.CharBlock(
        required=False, max_length=125, help_text="The title below the image"
    )
    page_title = blocks.CharBlock(
        required=False,
        max_length=125,
        help_text="Please add informative help text that includes the name or nature of the target content",
    )
    page_summary = blocks.CharBlock(
        required=False,
        max_length=250,
        help_text="A summary for the linked related page",
    )
    page_link_url = blocks.URLBlock(
        required=False, help_text="A url to a related page", label="Page link URL"
    )
    read_more_link_text = blocks.CharBlock(
        required=False,
        max_length=125,
        help_text="Specific text to use for the 'read more' link",
    )

    class Meta:
        template = "patterns/molecules/streamfield/blocks/transformation_block.html"
        label = "Transformation Block"


class FeaturedAlumniStoriesBlock(blocks.StructBlock):
    stories = blocks.ListBlock(
        blocks.PageChooserBlock(
            target_model=["editorial.EditorialPage"],
        ),
        required=True,
        help_text="Select alumni stories to feature",
    )

    class Meta:
        template = (
            "patterns/molecules/streamfield/blocks/featured_alumni_stories_block.html"
        )
        icon = "user"
        label = "Featured Alumni Stories"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        context["stories"] = [
            related_news_events_formatter(
                story, long_description=True, editorial_meta_label="Alumni Story"
            )
            for story in value["stories"]
        ]

        return context


class PartnershipsBlock(blocks.StructBlock):
    title = blocks.CharBlock(help_text="Enter the partnerships title")
    summary = blocks.TextBlock(help_text="Enter a summary for the partnerships section")
    slides = RelatedPageListBlockPage()

    class Meta:
        template = "patterns/molecules/streamfield/blocks/partnerships_block.html"
        icon = "group"
        label = "Partnerships"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        context["slides"] = partnerships_slides_formatter(value["slides"])

        return context


class NewsEventsBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        required=False,
        help_text="The title to display above the news and events listing",
    )
    link_text = blocks.CharBlock(
        required=False,
        help_text="The text to display for the 'View all news and events' link",
    )
    link_target_url = blocks.URLBlock(
        required=False,
        help_text="Add a link to view all news and events",
        label="Link target URL",
    )
    featured_event = blocks.PageChooserBlock(
        required=False,
        target_model=["events.EventDetailPage"],
        help_text=(
            "The featured event to display. "
            "If none is selected, this defaults to the next upcoming event. "
            "If the selected event's end date is in the past, this defaults to the next upcoming event."
        ),
    )

    class Meta:
        template = "patterns/molecules/streamfield/blocks/news_events_block.html"
        icon = "doc-full-inverse"
        label = "News and Events"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        event = None

        if (
            value["featured_event"]
            and value["featured_event"].end_date > timezone.now().date()
        ):
            # Since we chain news items to events, this needs to be in a list.
            event = [value["featured_event"]]
        else:
            # If no featured event is selected or the selected event has ended,
            # get the next upcoming event.
            try:
                event = EventDetailPage.objects.filter(
                    end_date__gte=timezone.now().date()
                ).order_by("start_date")[:1]
            except EventDetailPage.DoesNotExist:
                event = None

        # If there is an event, we'll show 2 news items and 1 event.
        NEWS_ITEMS = 2 if event else 3

        news = (
            EditorialPage.objects.filter(editorial_types__type__slug="news")
            .live()
            .filter(show_on_home_page=True)
            .select_related("listing_image")
            .order_by("-published_at")[:NEWS_ITEMS]
        )
        news_and_events = list(chain(news, event))

        context["news_and_events"] = [
            related_news_events_formatter(page, editorial_meta_label="News")
            for page in news_and_events
        ]

        return context


class BodySectionBlock(blocks.StructBlock):
    background_color = blocks.ChoiceBlock(
        choices=[("light", "Light"), ("dark", "Dark")],
        default="light",
        help_text="Select the background color for this section",
    )
    content = blocks.StreamBlock(
        [
            ("strapline", StraplineBlock()),
            ("transformation", TransformationBlock()),
            ("featured_alumni_stories", FeaturedAlumniStoriesBlock()),
            ("partnerships", PartnershipsBlock()),
            ("news_events", NewsEventsBlock()),
        ],
        required=True,
        help_text="Add content to this section",
    )


class StatisticsBlock(blocks.StructBlock):
    title = blocks.CharBlock(help_text="Enter the statistics section title")
    # The shared template expects a stream block.
    statistics = blocks.StreamBlock([("statistic", StatisticBlock())])
    background_image = ImageChooserBlock(
        required=False, help_text="Select a background image for the statistics section"
    )

    class Meta:
        icon = "user"
        label = "Statistics"


class PromoBannerBlock(blocks.StructBlock):
    background_color = blocks.ChoiceBlock(
        choices=[("light", "Light"), ("dark", "Dark")],
        default="light",
        help_text="Select the background color for this promo banner",
    )
    image = ImageChooserBlock(required=False)
    video = VideoChooserBlock(required=False)
    title = blocks.CharBlock()
    strapline = blocks.CharBlock()
    cta = LinkBlock(label="Call to Action")

    class Meta:
        template = "patterns/molecules/streamfield/blocks/promo_banner_block.html"
        icon = "image"
        label = "Promo Banner"

    def clean(self, value):
        value = super().clean(value)
        errors = {}

        if value["image"] and value["video"]:
            error = ["Please select either an image or a video, but not both."]
            errors["image"] = errors["video"] = ErrorList(error)

        if not value["image"] and not value["video"]:
            error = ["Please select either an image or a video."]
            errors["image"] = errors["video"] = ErrorList(error)

        if errors:
            raise StructBlockValidationError(errors)

        return value


class HomePageBodyBlock(blocks.StreamBlock):
    body_section = BodySectionBlock()
    promo_banner = PromoBannerBlock()
    statistics = StatisticsBlock()
