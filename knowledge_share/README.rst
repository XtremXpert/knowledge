# Knowledge Share

Permet aux éditeurs de publier une page de Connaissances par un lien public non devinable, en lecture seule, puis de désactiver, renouveler ou faire expirer ce lien.

## Partager une page

1. Depuis le menu **Actions** d'une page de contenu, choisir **Partager**.
2. Activer le lien et, facultativement, définir sa date d'expiration.
3. Copier l'URL publique affichée dans la fenêtre. Le visiteur peut lire la page sans compte et télécharger son PDF.
4. Désactiver le lien pour retirer l'accès, ou générer un nouveau lien pour invalider l'ancien.

Les catégories ne sont pas des pages partageables. La page publique n'affiche que la page choisie et ses propres pièces jointes/images; les images liées à d'autres enregistrements restent inchangées. La réponse est marquée `noindex, nofollow` pour demander aux moteurs de recherche de ne pas l'indexer. Cette directive ne remplace pas le caractère public du lien : toute personne qui le possède peut lire le contenu tant que le partage est actif et non expiré.

## Dépendance et tests

Dépend de `knowledge_page`. Les routes publiques et les contrôles du jeton, de l'expiration, des fichiers et du PDF sont couverts par les tests :

```sh
ADDONS=addons tools/test-modules.sh IMAGE knowledge_share
```
