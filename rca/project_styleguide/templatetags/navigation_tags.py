from pattern_library.monkey_utils import override_tag

from rca.navigation.templatetags.navigation_tags import register

override_tag(register, name="primarynav")
override_tag(register, name="footernav")
override_tag(register, name="audience_links")
override_tag(register, name="sidebar")
override_tag(register, name="footerlinks")
