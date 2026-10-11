from odoo.tests import Form, TransactionCase


class TestKnowledgeResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["document.page"].create(
            {"name": "Home", "type": "category"}
        )
        cls.record = cls.env["res.partner"].create({"name": "Heating Inc."})

    def test_link_and_count(self):
        page = self.env["document.page"].create(
            {
                "name": "Annual check",
                "parent_id": self.category.id,
                "content": "<p>x</p>",
                "partner_ids": [(6, 0, self.record.ids)],
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
        self.assertEqual(form.record.partner_ids, self.record)

    def test_group_pages_by_record(self):
        self.env["document.page"].create(
            {
                "name": "Manual",
                "parent_id": self.category.id,
                "content": "<p>x</p>",
                "partner_ids": [(6, 0, self.record.ids)],
            }
        )
        groups = self.env["document.page"].read_group(
            [("partner_ids", "in", self.record.ids)], ["partner_ids"], ["__count"]
        )
        self.assertIn((self.record.id, 1), groups)
