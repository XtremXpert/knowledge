from odoo import fields, models


class DocumentPage(models.Model):
    _inherit = "document.page"

    partner_ids = fields.Many2many(
        "res.partner",
        "document_page_res_partner_rel",
        "page_id",
        "partner_id",
        string="Contacts",
    )


class ResPartner(models.Model):
    _inherit = "res.partner"

    knowledge_page_ids = fields.Many2many(
        "document.page",
        "document_page_res_partner_rel",
        "partner_id",
        "page_id",
        string="Knowledge pages",
    )
    knowledge_page_count = fields.Integer(
        string="Knowledge", compute="_compute_knowledge_page_count"
    )

    def _compute_knowledge_page_count(self):
        for record in self:
            record.knowledge_page_count = len(record.knowledge_page_ids)

    def action_open_knowledge_pages(self):
        """Pages about this record; a new one from there is linked to it."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Knowledge: %s", self.display_name),
            "res_model": "document.page",
            "view_mode": "kanban,list,form",
            "domain": [("partner_ids", "in", self.ids)],
            "context": {
                "default_type": "content",
                "default_partner_ids": [self.id],
            },
        }
