from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_session_sequence_id = fields.Many2one(
        related="pos_config_id.session_sequence_id",
        string="Session IDs Sequence",
        readonly=False,
    )
