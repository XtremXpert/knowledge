from odoo import api, models

HOME_TREE_LIMIT = 5000
HOME_RECENT_LIMIT = 12


class DocumentPage(models.Model):
    _inherit = "document.page"

    @api.model
    def maison_home_data(self):
        """Categories, their readable pages, and the most recent pages.

        Every record is fetched with search(), so record rules and the
        company filter apply. A page whose category is not readable is left
        out entirely, and a category whose parent is not readable is exposed
        at the root: the landing page never reveals a category name, an id
        or a parent link the user is not allowed to read.
        """
        categories = self.search(
            [("type", "=", "category")],
            order="name, id",
            limit=HOME_TREE_LIMIT,
        )
        cat_by_id = {category.id: category for category in categories}

        nodes = []
        for category in categories:
            parent = category.parent_id
            nodes.append(
                {
                    "id": category.id,
                    "name": category.name,
                    "is_category": True,
                    # Never expose a parent the user cannot read.
                    "parent_id": (
                        parent.id if parent and parent.id in cat_by_id else False
                    ),
                }
            )

        tree_pages = self.search(
            [("type", "=", "content")],
            order="name, id",
            limit=HOME_TREE_LIMIT,
        )
        for page in tree_pages:
            parent = page.parent_id
            if parent and parent.id not in cat_by_id:
                # The category is not readable: do not reveal the page.
                continue
            nodes.append(
                {
                    "id": page.id,
                    "name": page.name,
                    "is_category": False,
                    "parent_id": parent.id if parent else False,
                }
            )

        recent = self.search(
            [("type", "=", "content")],
            order="write_date desc, id desc",
            limit=HOME_RECENT_LIMIT,
        )
        recent_data = []
        for page in recent:
            parent = page.parent_id
            if parent and parent.id not in cat_by_id:
                continue
            recent_data.append(
                {
                    "id": page.id,
                    "name": page.name,
                    "category": parent.name if parent else "",
                    "write_date": page.write_date,
                }
            )

        return {"nodes": nodes, "recent": recent_data}
