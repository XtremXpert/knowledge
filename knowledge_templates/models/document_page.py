from odoo import api, fields, models


class DocumentPage(models.Model):
    _inherit = "document.page"

    page_template_id = fields.Many2one(
        "knowledge.page.template",
        string="Template",
        ondelete="set null",
        help="Template the page was started from.",
    )

    @api.onchange("page_template_id")
    def _onchange_page_template_id(self):
        template = self.page_template_id
        if not template:
            return
        self.content = template.content
        if not self.parent_id and template.category_id:
            self.parent_id = template.category_id

    def action_save_as_template(self):
        """Actions menu of a page: start a template from its content."""
        self.ensure_one()
        template = self.env["knowledge.page.template"].create(
            {
                "name": self.name,
                "content": self.content,
                "category_id": self.parent_id.id,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "knowledge.page.template",
            "res_id": template.id,
            "views": [[False, "form"]],
            "target": "current",
        }
