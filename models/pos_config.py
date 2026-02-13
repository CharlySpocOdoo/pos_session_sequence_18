
from odoo import fields, models

import logging
_logger = logging.getLogger(__name__)

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
        """Called when opening the POS register; creates the pos.session."""
        self.ensure_one()

        _logger.info(
            "POS_SEQ DEBUG open_session_cb: POS=%s name=%s session_seq_id=%s opening_details_keys=%s",
            self.id,
            self.display_name,
            self.session_sequence_id.id if self.session_sequence_id else None,
            list((opening_details or {}).keys()),
        )
        
        ctx = dict(self.env.context or {})
        if self.session_sequence_id:
            ctx["force_pos_session_sequence_id"] = self.session_sequence_id.id
            _logger.info(
                "POS_SEQ DEBUG open_session_cb: setting ctx force_pos_session_sequence_id=%s",
                self.session_sequence_id.id,
            )
        else:
            _logger.warning("POS_SEQ DEBUG open_session_cb: POS has NO session_sequence_id configured")

        result = super(PosConfig, self.with_context(ctx)).open_session_cb(opening_details)

        _logger.info("POS_SEQ DEBUG open_session_cb: super() returned=%s", result)
        return super(PosConfig, self.with_context(ctx)).open_session_cb(opening_details)
