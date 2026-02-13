import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.model_create_multi
    def create(self, vals_list):
        seq_id = self.env.context.get("force_pos_session_sequence_id")

        _logger.warning(
            "POS_SEQ DEBUG pos.session.create: ctx force_pos_session_sequence_id=%s vals_count=%s first_vals_name=%s config_id=%s",
            seq_id,
            len(vals_list),
            (vals_list[0] or {}).get("name") if vals_list else None,
            (vals_list[0] or {}).get("config_id") if vals_list else None,
        )

        forced_names = None
        if seq_id:
            seq = self.env["ir.sequence"].browse(seq_id)
            _logger.warning(
                "POS_SEQ DEBUG pos.session.create: using seq id=%s name=%s code=%s prefix=%s next=%s",
                seq.id,
                seq.name,
                seq.code,
                seq.prefix,
                seq.number_next_actual,
            )

            # Genera nombres (uno por registro) antes del create
            forced_names = [seq.next_by_id() for _ in vals_list]
            _logger.warning("POS_SEQ DEBUG pos.session.create: forced_names=%s", forced_names)

        # Crea con core (aquí Odoo te lo sobreescribe)
        sessions = super().create(vals_list)

        _logger.warning(
            "POS_SEQ DEBUG pos.session.create: after super() ids=%s names=%s",
            sessions.ids,
            sessions.mapped("name"),
        )

        # ✅ Fix: reescribir name después
        if forced_names:
            for session, forced_name in zip(sessions, forced_names):
                old_name = session.name
                session.sudo().write({"name": forced_name})
                _logger.warning(
                    "POS_SEQ DEBUG pos.session.create: POST-WRITE name %s -> %s (session_id=%s)",
                    old_name,
                    forced_name,
                    session.id,
                )

            _logger.warning(
                "POS_SEQ DEBUG pos.session.create: final names=%s",
                sessions.mapped("name"),
            )

        return sessions
