from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase


class TestPageLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["document.page"].create(
            {"name": "Recipes", "type": "category"}
        )

    def _new_page(self):
        model = self.env["document.page"].with_context(default_type="content")
        with Form(model) as form:
            form.name = "Pizza dough"
            form.parent_id = self.category
            form.content = "<p>Flour, water, salt.</p>"
        return form.record

    def test_link_search_lists_other_pages(self):
        page = self._new_page()
        other = self.env["document.page"].create(
            {
                "name": "Pizza oven",
                "parent_id": self.category.id,
                "content": "<p>Hot.</p>",
            }
        )
        found = self.env["document.page"].maison_link_search(
            "pizza", exclude_id=page.id
        )
        self.assertEqual(
            found, [{"id": other.id, "name": "Pizza oven", "category": "Recipes"}]
        )
        listed = self.env["document.page"].maison_link_search("")
        self.assertNotIn(self.category.id, [p["id"] for p in listed])

    def test_link_create_makes_empty_page_in_category(self):
        created = self.env["document.page"].maison_link_create(
            "  Tomato sauce ", self.category.id
        )
        page = self.env["document.page"].browse(created["id"])
        self.assertEqual(
            (page.name, page.parent_id, page.type),
            ("Tomato sauce", self.category, "content"),
        )
        with self.assertRaises(UserError):
            self.env["document.page"].maison_link_create("   ")

    def test_backlinks_follow_current_version(self):
        target = self._new_page()
        source = self.env["document.page"].create(
            {
                "name": "Menu",
                "parent_id": self.category.id,
                "content": (
                    f'<p>See <a href="/odoo/document_pages/{target.id}">dough</a>.</p>'
                ),
            }
        )
        # An id sharing the same prefix is not a link to the target.
        self.env["document.page"].create(
            {
                "name": "Unrelated",
                "parent_id": self.category.id,
                "content": f'<p><a href="/odoo/document_pages/{target.id}0">x</a></p>',
            }
        )
        self.assertEqual(target.backlink_ids, source)
        self.assertEqual(target.backlink_count, 1)
        source.content = "<p>No more link.</p>"
        target.invalidate_recordset(["backlink_ids", "backlink_count"])
        self.assertFalse(target.backlink_ids)
