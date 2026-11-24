from django.shortcuts import render

from wagtail.models import PreviewableMixin


class StyledPreviewableMixin(PreviewableMixin):
    """A custom PreviewableMixin that renders previews with proper styling."""

    def serve_preview(self, request, mode_name):
        template = self.get_preview_template(request, mode_name)
        context = self.get_preview_context(request, mode_name)
        context.update(
            {
                "request": request,
                "is_preview": True,
                "template_name": template,
            }
        )
        return render(request, "patterns/preview_wrapper.html", context)
