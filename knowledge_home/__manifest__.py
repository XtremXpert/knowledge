{
    "name": "Knowledge Home",
    "summary": "Knowledge landing page: category tree, recent pages and search",
    "author": "Benoit Vézina, Odoo Community Association (OCA)",
    "category": "Knowledge",
    "version": "20.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/knowledge",
    "depends": [
        "document_knowledge",
        "knowledge_page",
        "knowledge_tree",
        "knowledge_search",
    ],
    "data": [
        "views/knowledge_home_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "knowledge_home/static/src/**/*",
        ],
    },
    "installable": True,
    "application": False,
}
