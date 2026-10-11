# Knowledge Links

Ajoute des liens internes entre les pages de Connaissances, la recherche de pages dans l'éditeur et une liste de liens entrants (rétroliens).

## Écrire un lien

Dans l'éditeur HTML d'une page, saisir `[[`, `@` après une espace ou `/page` pour ouvrir la recherche. Choisir une page pour insérer un lien; l'action **Créer « titre »** peut créer une nouvelle page dans la catégorie courante. La liste **Liens entrants** d'une page aide à retrouver les pages qui la citent.

Les références sont résolues à partir des liens du contenu et des pages accessibles; le module ne change pas les droits d'accès aux pages. Les éléments interactifs sont chargés dans les assets backend.

## Dépendances et tests

Dépend de `knowledge_page` et `html_editor`.

```sh
ADDONS=addons tools/test-modules.sh IMAGE knowledge_links
```
