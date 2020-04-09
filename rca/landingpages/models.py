from rca.utils.models import BasePage


class LandingPage(BasePage):
    template = "patterns/pages/landingpage/landing_page.html"


class ResearchLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page.html"


class InovationLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page.html"


class EnterpriseLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page.html"
