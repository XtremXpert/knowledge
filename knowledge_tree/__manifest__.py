{
    "name": "Knowledge Tree",
    "summary": "Wiki tree beside the page: categories and pages, drag and drop, quick add",
    "author": "Benoit Vézina",
    "category": "Knowledge",
    "version": "20.0.1.0.1",
    "license": "AGPL-3",
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
