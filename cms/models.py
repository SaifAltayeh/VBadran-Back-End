from django.db import models

from .defaults import DEFAULT_HOME


class SiteHome(models.Model):
    data = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "homepage content"
        verbose_name_plural = "homepage content"

    def __str__(self):
        return "Homepage"

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1, defaults={"data": DEFAULT_HOME})
        if not obj.data:
            obj.data = DEFAULT_HOME
            obj.save(update_fields=["data"])
        return obj
