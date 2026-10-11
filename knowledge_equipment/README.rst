# Knowledge Equipment

Lie des pages du wiki Odoo à des équipements de Maintenance. Le lien permet de retrouver les procédures, manuels et historiques utiles depuis la page ou depuis la fiche de l'équipement.

## Utilisation

- Sur une page **Connaissances** de type contenu, ajouter un ou plusieurs équipements dans la pastille **Équipements** sous le titre.
- Sur un équipement, le bouton statistique **Connaissances** ouvre les pages liées. Une nouvelle page créée depuis cette vue est liée à l'équipement.
- Dans la liste du wiki, filtrer ou regrouper les pages par équipement.

Les pages restent des `document.page`; le module ajoute une relation plusieurs-à-plusieurs et les éléments d'interface associés. Il ne crée pas d'équipement et ne modifie pas les règles d'accès de Maintenance ou de Connaissances.

## Dépendances et tests

Dépend de `knowledge_page` et `maintenance`.

```sh
ADDONS=addons tools/test-modules.sh IMAGE knowledge_equipment
```
