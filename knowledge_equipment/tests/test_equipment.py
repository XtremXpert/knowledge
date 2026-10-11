from odoo.tests import Form, TransactionCase


class TestKnowledgeMaintenanceEquipment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["document.page"].create(
            {"name": "Home", "type": "category"}
        )
        cls.record = cls.env["maintenance.equipment"].create({"name": "Boiler"})

    def test_link_and_count(self):
        page = self.env["document.page"].create(
            {
                "name": "Annual check",
                "parent_id": self.category.id,
                "content": "<p>x</p>",
                "equipment_ids": [(6, 0, self.record.ids)],
            }
        )
        self.assertEqual(self.record.knowledge_page_ids, page)
        self.assertEqual(self.record.knowledge_page_count, 1)
        action = self.record.action_open_knowledge_pages()
        self.assertEqual(self.env["document.page"].search(action["domain"]), page)

    def test_new_page_from_record_is_linked(self):
        action = self.record.action_open_knowledge_pages()
        model = self.env["document.page"].with_context(**action["context"])
        with Form(model, view="document_page.view_wiki_form") as form:
            form.name = "Contract"
            form.parent_id = self.category
            form.content = "<p>Yearly visit.</p>"
        self.assertEqual(form.record.equipment_ids, self.record)

    def test_group_pages_by_record(self):
        self.env["document.page"].create(
            {
                "name": "Manual",
                "parent_id": self.category.id,
                "content": "<p>x</p>",
                "equipment_ids": [(6, 0, self.record.ids)],
            }
        )
        groups = self.env["document.page"].read_group(
            [("equipment_ids", "in", self.record.ids)], ["equipment_ids"], ["__count"]
        )
        self.assertIn((self.record.id, 1), groups)
