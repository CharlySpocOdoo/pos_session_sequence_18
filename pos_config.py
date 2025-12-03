from odoo import fields, models

class PosConfig(models.Model):
    _inherit = "pos.config"

    def _default_session_sequence_id(self):
        return self.env.ref("point_of_sale.seq_pos_session").id

    session_sequence_id = fields.Many2one(
        "ir.sequence",
        string="Session IDs Sequence",
        help="Custom sequence for POS session references.",
        copy=False,
        ondelete="restrict",
        default=_default_session_sequence_id,
    )
