import base64
from datetime import timedelta

from odoo import fields
from odoo.tests import HttpCase, tagged

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgYGD4DwABBAEAwS2OUAAAAABJRU5ErkJggg=="
)


@tagged("post_install", "-at_install")
class TestShare(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Page = cls.env["document.page"]
        cls.category = Page.create({"name": "Home", "type": "category"})
        cls.page = Page.create(
            {
                "name": "Boiler",
                "parent_id": cls.category.id,
                "content": "<p>Check the <b>pressure</b>.</p>",
            }
        )
        cls.other = Page.create(
            {
                "name": "Private notes",
                "parent_id": cls.category.id,
                "content": "<p>Secret.</p>",
            }
        )

    def _get(self, path):
        return self.url_open(path, allow_redirects=False)

    def test_not_shared_by_default(self):
        self.assertFalse(self.page.share_active)
        self.assertFalse(self.page.share_url)

    def test_enable_read_disable(self):
        self.page.action_share_enable()
        token = self.page.share_token
        self.assertGreaterEqual(len(token), 30)
        self.assertTrue(self.page.share_url.endswith(f"/knowledge/share/{token}"))
        response = self._get(f"/knowledge/share/{token}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Check the <b>pressure</b>.", response.text)
        self.assertIn("noindex", response.headers.get("X-Robots-Tag", ""))
        self.assertNotIn("Secret.", response.text)
        self.page.action_share_disable()
        self.assertEqual(self._get(f"/knowledge/share/{token}").status_code, 404)

    def test_renew_invalidates_old_link(self):
        self.page.action_share_enable()
        old = self.page.share_token
        self.page.action_share_renew()
        self.assertNotEqual(self.page.share_token, old)
        self.assertEqual(self._get(f"/knowledge/share/{old}").status_code, 404)
        self.assertEqual(
            self._get(f"/knowledge/share/{self.page.share_token}").status_code, 200
        )

    def test_expired_link(self):
        self.page.action_share_enable()
        self.page.share_expiration = fields.Date.today() - timedelta(days=1)
        self.assertEqual(
            self._get(f"/knowledge/share/{self.page.share_token}").status_code, 404
        )

    def test_unknown_or_short_token(self):
        self.assertEqual(self._get("/knowledge/share/abc").status_code, 404)
        self.assertEqual(self._get("/knowledge/share/" + "x" * 32).status_code, 404)

    def test_only_the_page_images_are_served(self):
        Attachment = self.env["ir.attachment"]
        own = Attachment.create(
            {
                "name": "photo.png",
                "raw": PNG,
                "res_model": "document.page",
                "res_id": self.page.id,
            }
        )
        foreign = Attachment.create(
            {
                "name": "other.png",
                "raw": PNG,
                "res_model": "document.page",
                "res_id": self.other.id,
            }
        )
        self.page.content = (
            f'<p><img src="/web/image/{own.id}-abc123/photo.png?access_token=x"/>'
            f'<img src="/web/image/{foreign.id}"/></p>'
        )
        self.page.action_share_enable()
        token = self.page.share_token
        html = self._get(f"/knowledge/share/{token}").text
        self.assertIn(f"/knowledge/share/{token}/file/{own.id}", html)
        self.assertIn(f"/web/image/{foreign.id}", html)
        self.assertEqual(
            self._get(f"/knowledge/share/{token}/file/{own.id}").status_code, 200
        )
        self.assertEqual(
            self._get(f"/knowledge/share/{token}/file/{foreign.id}").status_code, 404
        )

    def test_pdf(self):
        self.page.action_share_enable()
        response = self._get(f"/knowledge/share/{self.page.share_token}/pdf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        # Test runs render the report as HTML instead of calling wkhtmltopdf.
        self.assertIn(b"Boiler", response.content)
