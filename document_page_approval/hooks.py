# Copyright 2018 Ivan Todorovich (<ivan.todorovich@gmail.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):  # pragma: no cover
    # Set all pre-existing pages history to approved
    _logger.info("Setting history to approved.")
    env.cr.execute(
        """
        UPDATE document_page_history
        SET state='approved',
            approved_uid=create_uid,
            approved_date=create_date
        WHERE state IS NULL OR state = 'draft'
    """
    )


def uninstall_hook(env):  # pragma: no cover
    # Remove unapproved pages
    _logger.info("Deleting unapproved Change Requests.")
    env.cr.execute("DELETE FROM document_page_history WHERE state != 'approved'")
    # Odoo 20 : réactiver les accès de document_page désactivés par ce module
    # (security/document_page_security.xml), sinon utilisateurs et éditeurs
    # perdent l'accès à l'historique.
    for xmlid in (
        "document_page.document_page_history_user",
        "document_page.document_page_history_editor",
    ):
        access = env.ref(xmlid, raise_if_not_found=False)
        if access:
            access.active = True
