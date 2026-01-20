from odoo import api, models


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.model
    def create(self, vals):
        session = super().create(vals)

        if session.config_id and session.config_id.session_sequence_id:
            session.name = session.config_id.session_sequence_id.next_by_id()

        return session
