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

    def open_session_cb(self, opening_details):
        """Called when opening a POS register (creating a pos.session)."""
        self.ensure_one()
        ctx = dict(self.env.context or {})
        if self.session_sequence_id:
            ctx["force_pos_session_sequence_id"] = self.session_sequence_id.id
        return super(PosConfig, self.with_context(ctx)).open_session_cb(opening_details)
