# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def uninstall_hook(env):
    """Odoo 20 : réactiver les accès de document_page désactivés par ce module
    (security/security.xml), sinon utilisateurs et éditeurs perdent l'accès
    aux pages."""
    for xmlid in (
        "document_page.document_page_user",
        "document_page.document_page_editor",
    ):
        access = env.ref(xmlid, raise_if_not_found=False)
        if access:
            access.active = True
