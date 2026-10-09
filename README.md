
[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# knowledge
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/knowledge&target_branch=20.0)
[![Pre-commit Status](https://github.com/OCA/knowledge/actions/workflows/pre-commit.yml/badge.svg?branch=20.0)](https://github.com/OCA/knowledge/actions/workflows/pre-commit.yml?query=branch%3A20.0)
[![Build Status](https://github.com/OCA/knowledge/actions/workflows/test.yml/badge.svg?branch=20.0)](https://github.com/OCA/knowledge/actions/workflows/test.yml?query=branch%3A20.0)
[![codecov](https://codecov.io/gh/OCA/knowledge/branch/20.0/graph/badge.svg)](https://codecov.io/gh/OCA/knowledge)
[![Translation Status](https://translation.odoo-community.org/widgets/knowledge-20-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/knowledge-20-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

knowledge

## Shared wiki interface (Odoo 20)

This fork also maintains the reusable wiki interface extracted from
`XtremXpert/maison` at commit `59ce177e5ccd567b51fccf0515e8136c65c42cfc`:

- `knowledge_page`: document-style pages, category/project cards and revision notes.
- `knowledge_tree`: page/category navigation, quick creation and drag-and-drop moves.
- `knowledge_search`: full-text search, highlighted excerpts and the command palette.
- `knowledge_home`: default landing page with a tree, recent pages and mobile navigation.

Install `knowledge_home` to enable the complete interface and its dependencies.
The technical module names, XML IDs, versions and existing APIs are retained so
consuming projects can change source paths without reinstalling existing modules.
Maintain these four modules here. Maison imports their exact pinned contents
through `addons.lock` / `odoo-dev vendor` and retains its integration tests.

The extraction itself does not activate the home module on an existing database;
installation and production promotion are separate operations.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

This part will be replaced when running the oca-gen-addons-table script from OCA/maintainer-tools.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
