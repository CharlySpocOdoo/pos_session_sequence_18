from odoo import api, models


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.model_create_multi
    def create(self, vals_list):
        seq_id = self.env.context.get("force_pos_session_sequence_id")
        if seq_id:
            seq = self.env["ir.sequence"].browse(seq_id)
            for vals in vals_list:
                # En POS normalmente viene name='/' (placeholder), así que esto SÍ entra.
                if vals.get("name") in (False, None, "", "/"):
                    vals["name"] = seq.next_by_id()
                else:
                    # Si prefieres forzarlo siempre aunque ya venga algo, descomenta:
                    # vals["name"] = seq.next_by_id()
                    pass

        return super().create(vals_list)
