{
    "name": "Knowledge Pages",
    "summary": "Document-style wiki pages: cover, cards, optional revision note",
    "author": "Benoit Vézina, Odoo Community Association (OCA)",
    "category": "Knowledge",
    "version": "20.0.1.1.1",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/knowledge",
    "depends": ["document_page", "document_page_project"],
    "data": [
        "views/document_page_views.xml",
        "views/document_page_kanban.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "knowledge_page/static/src/scss/document_page.scss",
        ],
    },
    "installable": True,
}
