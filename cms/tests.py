from rest_framework.test import APITestCase

from cms.models import SiteHome
from cms.sanitize import replace_stale_copy


class SiteHomeSanitizeTests(APITestCase):
    def test_stale_defaults_are_replaced_and_custom_copy_is_kept(self):
        page = SiteHome.load()
        page.data = {
            "about": {
                "paragraphs": {
                    "en": [
                        "VBADRAN is a personal training and online coaching practice. It started from a simple problem: people were training hard and still guessing.",
                        "Custom Spark gym note from the client.",
                    ]
                }
            }
        }
        page.save(update_fields=["data"])
        response = self.client.get("/api/site/")
        self.assertEqual(response.status_code, 200)
        paragraphs = response.data["about"]["paragraphs"]["en"]
        self.assertEqual(
            paragraphs[0],
            "Badran offers training packages, personal workout plans, and instructional exercise videos.",
        )
        self.assertEqual(paragraphs[1], "Custom Spark gym note from the client.")
        self.assertNotIn("Nutrition guidance", str(response.data))
        self.assertEqual(response.data["hero"]["primary"]["label"]["en"], "View packages")

    def test_missing_fields_use_current_defaults_not_old_promises(self):
        page = SiteHome.load()
        page.data = {}
        page.save(update_fields=["data"])
        response = self.client.get("/api/site/")
        blob = str(response.data)
        self.assertNotIn("weekly check-in", blob.lower())
        self.assertNotIn("Nutrition Guidance, Training + Nutrition", blob)
        self.assertEqual(response.data["sections"]["cta"]["label"]["en"], "View packages")

    def test_sanitize_command_persists_only_known_stale_sentences(self):
        from django.core.management import call_command

        page = SiteHome.load()
        page.data = {
            "pages": {
                "about": {
                    "chapters": [
                        {
                            "title": {"en": "The problem", "ar": "المشكلة"},
                            "body": {
                                "en": "VBADRAN started from a simple problem. People were training hard and still guessing. The sessions changed every week because nothing was written down, and the food had no relationship to the work.",
                                "ar": "Custom Arabic chapter the client wrote.",
                            },
                        }
                    ]
                }
            }
        }
        page.save(update_fields=["data"])
        call_command("sanitize_site_home")
        page.refresh_from_db()
        body = page.data["pages"]["about"]["chapters"][0]["body"]
        self.assertEqual(
            body["en"],
            "Badran started from a simple problem. People were training hard without a written plan or clear exercise references.",
        )
        self.assertEqual(body["ar"], "Custom Arabic chapter the client wrote.")

    def test_replace_stale_copy_skips_unrelated_strings(self):
        payload = {"lead": "Client custom nutrition workshop next month."}
        self.assertEqual(replace_stale_copy(payload), payload)
