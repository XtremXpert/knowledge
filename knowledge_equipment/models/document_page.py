from odoo import fields, models


class DocumentPage(models.Model):
    _inherit = "document.page"

    equipment_ids = fields.Many2many(
        "maintenance.equipment",
        "document_page_maintenance_equipment_rel",
        "page_id",
        "equipment_id",
    )


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    knowledge_page_ids = fields.Many2many(
        "document.page",
        "document_page_maintenance_equipment_rel",
        "equipment_id",
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
            "domain": [("equipment_ids", "in", self.ids)],
            "context": {
                "default_type": "content",
                "default_equipment_ids": [self.id],
            },
        }
