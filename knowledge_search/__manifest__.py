{
    "name": "Knowledge Search",
    "summary": "Full-text wiki search: title and content, highlighted excerpts, Ctrl+K",
    "author": "Benoit Vézina",
    "category": "Knowledge",
    "version": "20.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["knowledge_page"],
    "data": [
        "views/search_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "knowledge_search/static/src/**/*",
        ],
    },
    "installable": True,
}
