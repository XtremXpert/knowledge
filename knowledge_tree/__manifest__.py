{
    "name": "Knowledge Tree",
    "summary": "Wiki tree beside the page, with drag and drop and quick add",
    "author": "Benoit Vézina, Odoo Community Association (OCA)",
    "category": "Knowledge",
    "version": "20.0.1.0.1",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/knowledge",
    "depends": ["knowledge_page"],
    "data": [
        "views/document_page_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "knowledge_tree/static/src/**/*",
        ],
    },
    "installable": True,
}
