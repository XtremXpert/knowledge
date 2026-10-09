from odoo.tests import TransactionCase

from ..models.document_page import fold, highlight


class TestWikiSearch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Page = cls.env["document.page"]
        cls.category = Page.create({"name": "Maison", "type": "category"})
        cls.boiler = Page.create({
            "name": "Chaudière",
            "parent_id": cls.category.id,
            "content": "<p>Vérifier la <b>pression</b> chaque automne.</p>",
        })
        cls.filter_page = Page.create({
            "name": "Filtre à air",
            "parent_id": cls.category.id,
            "content": "<p>Changer le filtre de la chaudière chaque mois.</p>",
        })

    def search(self, query, **kw):
        return self.env["document.page"].maison_search(query, **kw)

    def test_fold_keeps_length(self):
        self.assertEqual(fold("Été À"), "ete a")
        self.assertEqual(len(fold("œuvre ß")), len("œuvre ß"))

    def test_accents_and_case_ignored(self):
        ids = [r["id"] for r in self.search("CHAUDIERE")]
        self.assertEqual(ids[0], self.boiler.id, "title match ranks first")
        self.assertIn(self.filter_page.id, ids, "content match is found too")

    def test_every_word_required(self):
        self.assertEqual([r["id"] for r in self.search("pression automne")], [self.boiler.id])
        self.assertFalse(self.search("pression mois"))
        self.assertFalse(self.search("a"), "one-letter words are ignored")

    def test_highlighted_excerpt_is_escaped(self):
        page = self.env["document.page"].create({
            "name": "Code",
            "parent_id": self.category.id,
            "content": "<p>Taper &lt;script&gt; puis pression.</p>",
        })
        result = next(r for r in self.search("pression") if r["id"] == page.id)
        self.assertIn("<mark>pression</mark>", result["snippet"])
        self.assertIn("&lt;script&gt;", result["snippet"])
        self.assertEqual(result["title"], "Code")

    def test_highlight_keeps_original_accents(self):
        self.assertEqual(str(highlight("Été chaud", ["ete"])), "<mark>Été</mark> chaud")

    def test_categories_are_not_results(self):
        self.assertNotIn(self.category.id, [r["id"] for r in self.search("maison")])
