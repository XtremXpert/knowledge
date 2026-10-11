import re

from odoo import api, fields, models
from odoo.exceptions import UserError

# Links inserted by the editor ("[[", "@") or pasted page URLs.
PAGE_LINK = re.compile(r"/document_pages/(\d+)(?!\d)")


class DocumentPage(models.Model):
    _inherit = "document.page"

    backlink_ids = fields.Many2many(
        "document.page",
        string="Linked from",
        compute="_compute_backlink_ids",
        help="Pages whose current version links to this page.",
    )
    backlink_count = fields.Integer(compute="_compute_backlink_ids")

    def _compute_backlink_ids(self):
        for rec in self:
            pages = self.browse()
            if rec.id:
                revisions = self.env["document.page.history"].search(
                    [("content", "ilike", f"/document_pages/{rec.id}")]
                )
                pages = revisions.page_id.filtered(
                    lambda page, rec=rec: (
                        page != rec and rec.id in page._linked_page_ids()
                    )
                )
            rec.backlink_ids = pages
            rec.backlink_count = len(pages)

    def _linked_page_ids(self):
        self.ensure_one()
        return {int(found) for found in PAGE_LINK.findall(self.content or "")}

    def action_open_backlinks(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Linked from %s", self.name),
            "res_model": "document.page",
            "view_mode": "kanban,list,form",
            "domain": [("id", "in", self.backlink_ids.ids)],
        }

    @api.model
    def maison_link_search(self, term, exclude_id=False, limit=8):
        """Pages offered by the editor's page search ("[[", "@")."""
        domain = [("type", "=", "content")]
        if term:
            domain.append(("name", "ilike", term))
        if exclude_id:
            domain.append(("id", "!=", exclude_id))
        pages = self.search(domain, limit=limit, order="write_date desc, id desc")
        return [
            {"id": page.id, "name": page.name, "category": page.parent_id.name or ""}
            for page in pages
        ]

    @api.model
    def maison_link_create(self, name, category_id=False):
        """Create an empty page from the editor's page search."""
        name = (name or "").strip()[:160]
        if not name:
            raise UserError(self.env._("A page title is required."))
        page = self.create(
            {
                "name": name,
                "type": "content",
                "parent_id": category_id or False,
                "content": "<p><br></p>",
            }
        )
        return {"id": page.id, "name": page.name}
