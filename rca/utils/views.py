from django.views import defaults


class MetaTitleMixin:
    meta_title = ""

    def get_meta_title(self):
        return self.meta_title

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["meta_title"] = self.get_meta_title()
        return context


def page_not_found(request, exception, template_name="patterns/pages/errors/404.html"):
    return defaults.page_not_found(request, exception, template_name)


def server_error(request, template_name="patterns/pages/errors/500.html"):
    return defaults.server_error(request, template_name)
