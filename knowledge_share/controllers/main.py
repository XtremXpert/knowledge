import re

from markupsafe import Markup
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request
from odoo.http.stream import content_disposition

# Images and files inserted in the page, served by the editor from /web/...
ATTACHMENT_URL = re.compile(
    r"/web/(?:image|content)/(\d+)(?:-[0-9a-f]+)?(?:/[^\"'?\s]*)?(?:\?[^\"'\s]*)?"
)


class KnowledgeShare(http.Controller):
    def _shared_page(self, token):
        """The page shared under this token, or 404 (unknown, disabled, expired)."""
        if not token or len(token) < 20:
            raise NotFound()
        page = (
            request.env["document.page"]
            .sudo()
            .search([("share_token", "=", token)], limit=1)
        )
        if not page or not page._share_is_valid():
            raise NotFound()
        return page

    def _page_attachments(self, page):
        return (
            request.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "document.page"),
                    ("res_id", "=", page.id),
                ]
            )
        )

    def _public_content(self, page, token):
        """Content with the page's own images rewritten to the shared route."""
        allowed = set(self._page_attachments(page).ids)

        def rewrite(match):
            attachment_id = int(match.group(1))
            if attachment_id in allowed:
                return f"/knowledge/share/{token}/file/{attachment_id}"
            return match.group(0)

        return Markup(ATTACHMENT_URL.sub(rewrite, page.content or ""))

    def _lang(self, page):
        return page.create_uid.lang or "en_US"

    @http.route(
        "/knowledge/share/<string:token>", type="http", auth="public", sitemap=False
    )
    def share_page(self, token, **kwargs):
        page = self._shared_page(token)
        page = page.with_context(lang=self._lang(page))
        _ = page.env._
        return request.render(
            "knowledge_share.public_page",
            {
                "page": page,
                "token": token,
                "content": self._public_content(page, token),
                "labels": {
                    "updated": request.env._("Updated on"),
                    "footer": request.env._(
                        "Shared read-only from the household wiki."
                    ),
                    "pdf": request.env._("Download as PDF"),
                },
            },
            headers={"X-Robots-Tag": "noindex, nofollow"},
        )

    @http.route(
        "/knowledge/share/<string:token>/file/<int:attachment_id>",
        type="http",
        auth="public",
        sitemap=False,
    )
    def share_file(self, token, attachment_id, **kwargs):
        page = self._shared_page(token)
        attachment = self._page_attachments(page).filtered(
            lambda a: a.id == attachment_id
        )
        if not attachment:
            raise NotFound()
        return request.env["ir.binary"]._get_stream_from(attachment).get_response()

    @http.route(
        "/knowledge/share/<string:token>/cover",
        type="http",
        auth="public",
        sitemap=False,
    )
    def share_cover(self, token, **kwargs):
        page = self._shared_page(token)
        if not page.image:
            raise NotFound()
        return (
            request.env["ir.binary"]
            ._get_image_stream_from(page, "image")
            .get_response()
        )

    @http.route(
        "/knowledge/share/<string:token>/pdf", type="http", auth="public", sitemap=False
    )
    def share_pdf(self, token, **kwargs):
        page = self._shared_page(token)
        report = request.env.ref("document_page.report_document_page").sudo()
        pdf, _type = report.with_context(lang=self._lang(page))._render_qweb_pdf(
            report.report_name, page.ids
        )
        filename = re.sub(r"[^\w\- ]+", "", page.name or "").strip() or "page"
        return request.make_response(
            pdf,
            headers=[
                ("Content-Type", "application/pdf"),
                (
                    "Content-Disposition",
                    content_disposition(f"{filename}.pdf", "inline"),
                ),
                ("X-Robots-Tag", "noindex, nofollow"),
            ],
        )
