from odoo import api, models


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.model
    def create(self, vals):
        if not vals.get("name") and vals.get("config_id"):
            config = self.env["pos.config"].browse(vals["config_id"])

            if config.session_sequence_id:
                # 1️⃣ Generamos el nombre SOLO una vez
                vals["name"] = config.session_sequence_id.next_by_id()

                # 2️⃣ Evitamos que el core consuma la secuencia global
                vals["sequence_number"] = False

        return super().create(vals)
