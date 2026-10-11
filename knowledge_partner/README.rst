# Knowledge Partner

Lie les pages de Connaissances aux contacts Odoo (`res.partner`), par exemple aux fournisseurs, artisans ou organismes concernés par une procédure.

## Utilisation

- Sur une page de contenu, ajouter les contacts dans la pastille **Contacts** sous le titre.
- Sur une fiche contact, le bouton **Connaissances** ouvre les pages liées; une nouvelle page créée depuis ce bouton est préassociée au contact.
- Filtrer ou regrouper les pages du wiki par contact.

Le module ajoute une relation plusieurs-à-plusieurs entre `document.page` et `res.partner`. Il ne crée pas de contacts et n'altère pas les droits d'accès des deux applications.

## Dépendance et tests

Dépend de `knowledge_page`.

```sh
ADDONS=addons tools/test-modules.sh IMAGE knowledge_partner
```
