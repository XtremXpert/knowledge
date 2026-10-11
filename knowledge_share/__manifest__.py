{
    "name": "Knowledge Share",
    "summary": "Share a wiki page with a public read-only link, download it as PDF",
    "author": "Benoit Vézina, Odoo Community Association (OCA)",
    "category": "Knowledge",
    "version": "20.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/knowledge",
    "depends": ["knowledge_page"],
    "data": [
        "views/document_page_views.xml",
        "views/public_templates.xml",
        "views/report_templates.xml",
    ],
    "installable": True,
}
