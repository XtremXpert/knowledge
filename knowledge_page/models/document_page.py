from odoo import api, fields, models
from odoo.tools import html2plaintext


class DocumentPage(models.Model):
    _inherit = "document.page"

    # Not stored: becomes the summary of the next revision.
    revision_note = fields.Char(
        compute="_compute_revision_note",
        readonly=False,
        help="Optional: what changed. The revision name is set automatically.",
    )

    content_excerpt = fields.Char(string="Excerpt", compute="_compute_content_excerpt")
    # Card color: the page's own color, otherwise its category color.
    cover_color = fields.Integer(compute="_compute_cover_color")
    page_count = fields.Integer(compute="_compute_page_count")

    def _compute_revision_note(self):
        self.revision_note = False

    @api.depends("history_head")
    def _compute_content_excerpt(self):
        for rec in self:
            text = " ".join(
                html2plaintext(rec.history_head.content or "", include_references=False).split()
            )
            rec.content_excerpt = text[:157] + "…" if len(text) > 160 else text

    @api.depends("color", "parent_id.color")
    def _compute_cover_color(self):
        for rec in self:
            rec.cover_color = rec.color or rec.parent_id.color

    @api.depends("child_ids.type")
    def _compute_page_count(self):
        for rec in self:
            rec.page_count = len(rec.child_ids.filtered(lambda p: p.type == "content"))

    @api.model_create_multi
    def create(self, vals_list):
        notes = [vals.pop("revision_note", False) for vals in vals_list]
        if not any(notes):
            return super().create(vals_list)
        pages = self.browse()
        for vals, note in zip(vals_list, notes, strict=True):
            pages |= super(
                DocumentPage, self.with_context(maison_revision_note=note)
            ).create([vals])
        return pages

    def write(self, vals):
        note = vals.pop("revision_note", False)
        if note:
            return super(
                DocumentPage, self.with_context(maison_revision_note=note)
            ).write(vals)
        return super().write(vals)

    def _create_history(self, vals):
        head = self.history_head
        if not vals.get("name") or vals["name"] == head.name:
            vals["name"] = self.env._("Rev. %s", len(self.history_ids) + 1)
        note = self.env.context.get("maison_revision_note")
        if note:
            vals["summary"] = note
        elif not vals.get("summary") or vals["summary"] == head.summary:
            vals["summary"] = self.env._("Edited") if head else self.env._("Created")
        return super()._create_history(vals)
