from odoo.tests import Form, TransactionCase


class TestPageTemplates(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["document.page"].create(
            {"name": "Home", "type": "category"}
        )
        cls.kitchen = cls.env["document.page"].create(
            {"name": "Kitchen", "type": "category"}
        )
        cls.recipe = cls.env.ref("knowledge_templates.template_recipe")

    def _form(self):
        model = self.env["document.page"].with_context(default_type="content")
        return Form(model, view="document_page.view_wiki_form")

    def test_shipped_templates(self):
        names = self.env["knowledge.page.template"].search([]).mapped("name")
        self.assertEqual(
            names, ["Procedure", "Equipment sheet", "Recipe", "Meeting notes"]
        )

    def test_template_fills_content_and_category(self):
        self.recipe.category_id = self.kitchen
        with self._form() as form:
            form.name = "Pizza dough"
            form.page_template_id = self.recipe
            self.assertIn("Ingredients", form.content)
            self.assertEqual(form.parent_id, self.kitchen)
        self.assertEqual(form.record.page_template_id, self.recipe)

    def test_chosen_category_is_kept(self):
        self.recipe.category_id = self.kitchen
        with self._form() as form:
            form.name = "Soup"
            form.parent_id = self.category
            form.page_template_id = self.recipe
            self.assertEqual(form.parent_id, self.category)

    def test_save_page_as_template(self):
        page = self.env["document.page"].create(
            {
                "name": "Boiler check",
                "parent_id": self.category.id,
                "content": "<p>Check the pressure.</p>",
            }
        )
        action = page.action_save_as_template()
        template = self.env["knowledge.page.template"].browse(action["res_id"])
        self.assertEqual(template.name, "Boiler check")
        self.assertIn("Check the pressure.", template.content)
        self.assertEqual(template.category_id, self.category)
