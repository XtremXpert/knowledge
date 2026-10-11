{
    "name": "Knowledge Templates",
    "summary": "Page templates: pick one when creating a page, save a page as template",
    "author": "Benoit Vézina, Odoo Community Association (OCA)",
    "category": "Knowledge",
    "version": "20.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/knowledge",
    "depends": ["knowledge_page"],
    "data": [
        "security/ir.access.csv",
        "views/page_template_views.xml",
        "views/document_page_views.xml",
        "data/page_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "knowledge_templates/static/src/**/*",
        ],
    },
    "installable": True,
}
