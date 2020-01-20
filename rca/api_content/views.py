from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView


class ApiContentCacheSettings(TemplateView):
    template_name = "api_content/api_content_admin.html"


def ApiContentCacheClear(request):
    cache_keys = ["latest_news_and_events", "latest_alumni_stories"]
    cache.delete_many(cache_keys)
    return HttpResponseRedirect("/admin/api-cache/")
