from django.core.management.base import BaseCommand

from cms.models import SiteHome
from cms.sanitize import replace_stale_copy


class Command(BaseCommand):
    help = (
        "Replace known outdated default CMS sentences with current copy. "
        "Custom client text that does not match those sentences is left unchanged."
    )

    def handle(self, *args, **options):
        page = SiteHome.load()
        original = page.data or {}
        cleaned = replace_stale_copy(original)
        if cleaned == original:
            self.stdout.write("No known outdated default sentences were found.")
            return
        page.data = cleaned
        page.save(update_fields=["data"])
        self.stdout.write(self.style.SUCCESS("Replaced known outdated default CMS sentences. Custom copy was preserved."))
