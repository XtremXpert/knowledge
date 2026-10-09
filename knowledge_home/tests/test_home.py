from odoo.tests import TransactionCase, new_test_user


class TestKnowledgeHome(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Page = cls.env["document.page"]
        cls.company_a = cls.env.company
        cls.company_b = cls.env["res.company"].create({"name": "Autre société"})
        cls.usage = Page.create(
            {"name": "Utilisation", "type": "category", "company_id": cls.company_a.id}
        )
        cls.dev = Page.create(
            {
                "name": "Développement",
                "type": "category",
                "parent_id": cls.usage.id,
                "company_id": cls.company_a.id,
            }
        )
        cls.page = Page.create(
            {
                "name": "Chaudière",
                "parent_id": cls.usage.id,
                "content": "<p>Vérifier la pression.</p>",
                "company_id": cls.company_a.id,
            }
        )
        # Company B data, unreadable by a user restricted to company A.
        cls.other_cat = Page.create(
            {
                "name": "Infrastructure",
                "type": "category",
                "company_id": cls.company_b.id,
            }
        )
        cls.other_page = Page.create(
            {
                "name": "Serveur k8s",
                "parent_id": cls.other_cat.id,
                "content": "<p>x</p>",
                "company_id": cls.company_b.id,
            }
        )
        # A readable page (no company) whose category belongs to another
        # company: its name must never reach a company A user.
        cls.orphan = Page.create(
            {
                "name": "Page hors société",
                "parent_id": cls.other_cat.id,
                "content": "<p>y</p>",
                "company_id": False,
            }
        )
        # A readable category (company A) whose parent is a company B
        # category: the parent id must not leak either.
        cls.shared_cat = Page.create(
            {
                "name": "Catégorie partagée",
                "type": "category",
                "parent_id": cls.other_cat.id,
                "company_id": cls.company_a.id,
            }
        )
        cls.user_a = new_test_user(
            cls.env,
            login="home-a",
            groups="document_knowledge.group_document_user",
        )
        cls.user_a.write(
            {
                "company_id": cls.company_a.id,
                "company_ids": [(6, 0, [cls.company_a.id])],
            }
        )

    def test_lists_categories_and_subpages(self):
        data = self.env["document.page"].maison_home_data()
        nodes = {node["id"]: node for node in data["nodes"]}
        self.assertTrue(nodes[self.usage.id]["is_category"])
        self.assertEqual(nodes[self.dev.id]["parent_id"], self.usage.id)
        self.assertFalse(nodes[self.page.id]["is_category"])
        self.assertEqual(nodes[self.page.id]["parent_id"], self.usage.id)

    def test_recent_pages_carry_their_category(self):
        data = self.env["document.page"].maison_home_data()
        recent = {page["id"]: page for page in data["recent"]}
        self.assertIn(self.page.id, recent)
        self.assertEqual(recent[self.page.id]["category"], "Utilisation")
        self.assertNotIn(self.usage.id, recent, "categories are not recent pages")

    def test_restricted_user_never_sees_other_company(self):
        Page = self.env["document.page"].with_user(self.user_a)
        data = Page.maison_home_data()
        node_ids = {node["id"] for node in data["nodes"]}
        recent_ids = {page["id"] for page in data["recent"]}
        self.assertIn(self.usage.id, node_ids)
        self.assertIn(self.page.id, node_ids)
        self.assertNotIn(self.other_cat.id, node_ids)
        self.assertNotIn(self.other_page.id, node_ids)
        self.assertNotIn(self.other_page.id, recent_ids)
        # No node points to a category the user cannot read.
        for node in data["nodes"]:
            self.assertIn(node["parent_id"], node_ids | {False})

    def test_readable_page_with_unreadable_parent_is_hidden(self):
        Page = self.env["document.page"].with_user(self.user_a)
        data = Page.maison_home_data()
        node_ids = {node["id"] for node in data["nodes"]}
        recent_ids = {page["id"] for page in data["recent"]}
        self.assertNotIn(self.orphan.id, node_ids)
        self.assertNotIn(self.orphan.id, recent_ids)

    def test_readable_category_with_unreadable_parent_is_root(self):
        Page = self.env["document.page"].with_user(self.user_a)
        data = Page.maison_home_data()
        nodes = {node["id"]: node for node in data["nodes"]}
        self.assertIn(self.shared_cat.id, nodes)
        self.assertEqual(
            nodes[self.shared_cat.id]["parent_id"],
            False,
            "the unreadable parent id must not leak",
        )
        self.assertNotIn(self.other_cat.id, nodes)
