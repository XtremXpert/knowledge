from odoo import api, models
from odoo.exceptions import UserError

TREE_LIMIT = 5000


class DocumentPage(models.Model):
    _inherit = "document.page"

    @api.model
    def maison_tree_nodes(self):
        """Categories and pages readable by the user, for the wiki tree."""
        records = self.search([], order="name, id", limit=TREE_LIMIT)
        return [
            {
                "id": rec.id,
                "name": rec.name,
                "type": rec.type,
                "parent_id": rec.parent_id.id or False,
            }
            for rec in records
        ]

    def maison_tree_move(self, category_id):
        """Drag and drop in the tree: put pages or categories in a category."""
        category = self.browse(category_id).exists()
        if not category or category.type != "category":
            raise UserError(self.env._("Pages can only be moved into a category."))
        if category in self:
            raise UserError(self.env._("A category cannot be moved into itself."))
        # Recursion (a category into one of its subcategories) is refused by
        # document_page's own parent constraint.
        self.write({"parent_id": category.id})
        return True
