{
    "name": "Knowledge Links",
    "summary": 'Links between wiki pages ("[[", "@", "/page") and backlinks',
    "author": "Benoit Vézina, Odoo Community Association (OCA)",
    "category": "Knowledge",
    "version": "20.0.1.0.1",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/knowledge",
    "depends": ["knowledge_page", "html_editor"],
    "data": [
        "views/document_page_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "knowledge_links/static/src/**/*",
        ],
    },
    "installable": True,
}
