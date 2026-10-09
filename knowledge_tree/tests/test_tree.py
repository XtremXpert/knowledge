from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase


class TestWikiTree(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Page = cls.env["document.page"]
        cls.home = Page.create({"name": "Home", "type": "category"})
        cls.heating = Page.create(
            {"name": "Heating", "type": "category", "parent_id": cls.home.id}
        )
        cls.boiler = Page.create(
            {"name": "Boiler", "parent_id": cls.heating.id, "content": "<p>x</p>"}
        )

    def test_nodes_list_categories_and_pages(self):
        nodes = {n["id"]: n for n in self.env["document.page"].maison_tree_nodes()}
        self.assertEqual(nodes[self.home.id]["type"], "category")
        self.assertEqual(nodes[self.heating.id]["parent_id"], self.home.id)
        self.assertEqual(
            nodes[self.boiler.id],
            {"id": self.boiler.id, "name": "Boiler", "type": "content",
             "parent_id": self.heating.id},
        )

    def test_move_page_into_category(self):
        kitchen = self.env["document.page"].create({"name": "Kitchen", "type": "category"})
        self.boiler.maison_tree_move(kitchen.id)
        self.assertEqual(self.boiler.parent_id, kitchen)

    def test_move_refuses_pages_and_cycles(self):
        with self.assertRaises(UserError):
            self.heating.maison_tree_move(self.boiler.id)
        with self.assertRaises(UserError):
            self.heating.maison_tree_move(self.heating.id)
        with self.assertRaises(ValidationError):
            self.home.maison_tree_move(self.heating.id)
