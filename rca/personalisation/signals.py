from functools import partial

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from wagtail.models import PageViewRestriction

from rca.utils.cache import purge_page_restriction_cache


@receiver(post_save, sender=PageViewRestriction)
@receiver(post_delete, sender=PageViewRestriction)
def purge_restriction_cache(sender, instance, using, **kwargs):
    if kwargs.get("raw"):
        return
    transaction.on_commit(
        partial(purge_page_restriction_cache, instance.page), using=using
    )
