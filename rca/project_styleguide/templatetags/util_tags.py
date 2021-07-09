from pattern_library.monkey_utils import override_tag

from rca.utils.templatetags.util_tags import register

override_tag(register, name="social_media_links")
override_tag(register, name="get_all_active_filters")
