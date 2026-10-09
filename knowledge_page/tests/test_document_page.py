from odoo.tests import Form, TransactionCase


class TestDocumentPage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["document.page"].create(
            {"name": "Recipes", "type": "category"}
        )

    def _new_page(self, env=None):
        model = (env or self.env)["document.page"].with_context(default_type="content")
        with Form(model) as form:
            form.name = "Pizza dough"
            form.parent_id = self.category
            form.content = "<p>Flour, water, salt.</p>"
        return form.record

    def test_create_needs_only_title_category_content(self):
        page = self._new_page()
        self.assertEqual(page.history_head.name, "Rev. 1")
        self.assertEqual(page.history_head.summary, "Created")
        self.assertEqual(page.content, "<p>Flour, water, salt.</p>")

    def test_edit_adds_revision_without_touching_previous(self):
        page = self._new_page()
        first = page.history_head
        with Form(page) as form:
            form.content = "<p>Flour, water, salt, yeast.</p>"
        self.assertEqual(len(page.history_ids), 2)
        self.assertEqual(page.history_head.name, "Rev. 2")
        self.assertEqual(page.history_head.summary, "Edited")
        self.assertEqual((first.name, first.summary), ("Rev. 1", "Created"))

    def test_note_hidden_until_saved(self):
        form = Form(self.env["document.page"].with_context(default_type="content"))
        with self.assertRaises(AssertionError):
            form.revision_note = "Too early"

    def test_note_becomes_summary(self):
        page = self.env["document.page"].create({
            "name": "Pizza dough",
            "parent_id": self.category.id,
            "content": "<p>Flour, water, salt.</p>",
            "revision_note": "Grandma's version",
        })
        self.assertEqual(page.history_head.summary, "Grandma's version")
        with Form(page) as form:
            form.content = "<p>With yeast.</p>"
            form.revision_note = "Add yeast"
        self.assertEqual(page.history_head.summary, "Add yeast")
        self.assertEqual(page.history_ids[1].summary, "Grandma's version")

    def test_explicit_history_values_are_kept(self):
        page = self._new_page()
        copy = page.copy()
        self.assertEqual(copy.history_head.name, "1.0")

    def test_edit_is_kept_after_reload(self):
        page = self._new_page()
        page.write({"content": "<p>v2</p>"})
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertEqual(page.history_head, page.history_ids.sorted("id")[-1])
        self.assertEqual(page.content, "<p>v2</p>")

    def test_card_fields(self):
        self.category.color = 4
        page = self._new_page()
        long_page = self.env["document.page"].create(
            {
                "name": "Long",
                "parent_id": self.category.id,
                "content": "<p>%s</p>" % ("word " * 100),
            }
        )
        self.assertEqual(page.content_excerpt, "Flour, water, salt.")
        self.assertEqual(len(long_page.content_excerpt), 158)
        self.assertTrue(long_page.content_excerpt.endswith("…"))
        self.assertEqual(page.cover_color, 4)
        page.color = 2
        self.assertEqual(page.cover_color, 2)
        self.assertEqual(self.category.page_count, 2)

    def test_french_translation(self):
        self.env["res.lang"]._activate_lang("fr_CA")
        self.env["ir.module.module"]._load_module_terms(["knowledge_page"], ["fr_CA"])
        page = self._new_page(env=self.env(context={"lang": "fr_CA"}))
        self.assertEqual(page.history_head.name, "Rév. 1")
        self.assertEqual(page.history_head.summary, "Création")

    def test_excerpt_skips_link_references(self):
        page = self.env["document.page"].create({
            "name": "Menu",
            "parent_id": self.category.id,
            "content": '<p>See <a href="/odoo/document_pages/1">dough</a>.</p>',
        })
        self.assertIn("See dough", page.content_excerpt)
        self.assertNotIn("[1]", page.content_excerpt)
