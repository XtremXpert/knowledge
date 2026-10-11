import secrets

from odoo import fields, models


class DocumentPage(models.Model):
    _inherit = "document.page"

    share_active = fields.Boolean(string="Shared", copy=False, tracking=True)
    share_token = fields.Char(copy=False, readonly=True, index=True)
    share_expiration = fields.Date(
        string="Link expires on",
        copy=False,
        help="Optional: after this date the link no longer works.",
    )
    share_url = fields.Char(string="Public link", compute="_compute_share_url")

    def _compute_share_url(self):
        for page in self:
            page.share_url = (
                f"{page.get_base_url()}/knowledge/share/{page.share_token}"
                if page.share_active and page.share_token
                else False
            )

    def _share_is_valid(self):
        self.ensure_one()
        return bool(
            self.share_active
            and self.share_token
            and self.type == "content"
            and (
                not self.share_expiration
                or self.share_expiration >= fields.Date.today()
            )
        )

    def _action_share_dialog(self):
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Share the page"),
            "res_model": "document.page",
            "res_id": self.id,
            "view_mode": "form",
            "views": [[self.env.ref("knowledge_share.view_share_dialog").id, "form"]],
            "target": "new",
        }

    def action_share_dialog(self):
        self.ensure_one()
        return self._action_share_dialog()

    def action_share_enable(self):
        self.ensure_one()
        self.write(
            {
                "share_active": True,
                "share_token": self.share_token or secrets.token_urlsafe(24),
            }
        )
        return self._action_share_dialog()

    def action_share_disable(self):
        self.ensure_one()
        self.share_active = False
        return self._action_share_dialog()

    def action_share_renew(self):
        """New link: the previous one stops working."""
        self.ensure_one()
        self.share_token = secrets.token_urlsafe(24)
        self.message_post(
            body=self.env._("A new public link replaces the previous one.")
        )
        return self._action_share_dialog()
