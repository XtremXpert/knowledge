# Copyright 2019 César Fernández Domínguez <cesfernandez@outlook.com>
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import http
from odoo.http import request
from odoo.http.stream import content_disposition


class AttachmentZippedDownloadController(http.Controller):
    @http.route("/web/attachment/download_zip", type="http", auth="user")
    def download_zip(self, ids=None, debug=0):
        ids = [] if not ids else ids
        if len(ids) == 0:
            return
        list_ids = map(int, ids.split(","))
        out_file = request.env["ir.attachment"].browse(list_ids)._create_temp_zip()
        # Odoo 20 : odoo.http.Stream n'existe plus (même construction que /mail/attachment/zip)
        content = out_file.getvalue()
        headers = [
            ("Content-Type", "application/zip"),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Length", len(content)),
            ("Content-Disposition", content_disposition(request.env._("attachments.zip"))),
        ]
        return request.make_response(content, headers)
