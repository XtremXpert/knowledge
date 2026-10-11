from odoo import fields, models


class KnowledgePageTemplate(models.Model):
    _name = "knowledge.page.template"
    _description = "Wiki page template"
    _order = "sequence, name, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    icon = fields.Char(
        default="description",
        help="Icon name shown on the template card "
        "(e.g. checklist, build, restaurant).",
    )
    description = fields.Char(translate=True, help="One line shown under the name.")
    content = fields.Html(translate=True, sanitize=False)
    category_id = fields.Many2one(
        "document.page",
        string="Default category",
        domain=[("type", "=", "category")],
        help="Category set on the new page when none is chosen yet.",
    )
