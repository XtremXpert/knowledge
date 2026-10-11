# Knowledge Templates

Ajoute des modèles réutilisables pour créer des pages de Connaissances avec une structure et un contenu de départ cohérents.

## Utilisation

- Lors de la création d'une page, choisir une carte de modèle au-dessus de l'éditeur. Le contenu est copié dans la nouvelle page; la catégorie par défaut du modèle est utilisée si aucune catégorie n'est déjà sélectionnée.
- Les modèles initiaux comprennent procédure, fiche d'équipement, recette et compte rendu. Ils sont ajoutés comme données `noupdate` afin de ne pas écraser les personnalisations lors d'une mise à jour.
- Un éditeur peut choisir **Actions → Enregistrer comme modèle** sur une page existante.
- Les utilisateurs autorisés à modifier les pages peuvent gérer les modèles dans **Connaissances → Modèles de page** : contenu HTML, icône, description, ordre, catégorie par défaut et archivage.

Un modèle ne modifie pas une page tant qu'il n'est pas choisi lors de sa création. La page et son modèle restent des enregistrements distincts.

## Accès, dépendances et tests

Dépend de `knowledge_page`. Le modèle `knowledge.page.template` est protégé par les droits d'accès définis dans `security/ir.access.csv`; le menu et l'action de sauvegarde sont réservés aux éditeurs de pages.

```sh
ADDONS=addons tools/test-modules.sh IMAGE knowledge_templates
```
