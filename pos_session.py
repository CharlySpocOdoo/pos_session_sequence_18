from odoo import api, models


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.model_create_multi
    def create(self, vals_list):
        seq_id = self.env.context.get("force_pos_session_sequence_id")
        if seq_id:
            seq = self.env["ir.sequence"].browse(seq_id)
            for vals in vals_list:
                # En POS el name suele venir como '/' (placeholder). Lo forzamos.
                if vals.get("name") in (False, None, "", "/"):
                    vals["name"] = seq.next_by_id()
                else:
                    # Incluso si ya viene algo, lo puedes forzar igual si quieres:
                    # vals["name"] = seq.next_by_id()
                    pass

        return super().create(vals_list)
