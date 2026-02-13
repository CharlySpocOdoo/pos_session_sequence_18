import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = "pos.session"

    # Guardamos el nombre correcto que generamos (para poder restaurarlo si alguien lo pisa)
    forced_session_name = fields.Char(copy=False, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        seq_id = self.env.context.get("force_pos_session_sequence_id")

        _logger.warning(
            "POS_SEQ DEBUG create: ctx force_pos_session_sequence_id=%s vals_count=%s first_vals_name=%s config_id=%s",
            seq_id,
            len(vals_list),
            (vals_list[0] or {}).get("name") if vals_list else None,
            (vals_list[0] or {}).get("config_id") if vals_list else None,
        )

        forced_names = None
        if seq_id:
            seq = self.env["ir.sequence"].browse(seq_id)
            _logger.warning(
                "POS_SEQ DEBUG create: using seq id=%s name=%s code=%s prefix=%s next=%s",
                seq.id,
                seq.name,
                seq.code,
                seq.prefix,
                seq.number_next_actual,
            )
            forced_names = [seq.next_by_id() for _ in vals_list]
            _logger.warning("POS_SEQ DEBUG create: forced_names=%s", forced_names)

        sessions = super().create(vals_list)

        _logger.warning(
            "POS_SEQ DEBUG create: after super() ids=%s names=%s",
            sessions.ids,
            sessions.mapped("name"),
        )

        if forced_names:
            for session, forced_name in zip(sessions, forced_names):
                old_name = session.name
                session.sudo().write({"name": forced_name, "forced_session_name": forced_name})
                _logger.warning(
                    "POS_SEQ DEBUG create: POST-WRITE name %s -> %s (session_id=%s)",
                    old_name,
                    forced_name,
                    session.id,
                )

            _logger.warning(
                "POS_SEQ DEBUG create: final names=%s",
                sessions.mapped("name"),
            )

        return sessions

    def write(self, vals):
        # LOG: detectar quién pisa el name
        if "name" in vals:
            for s in self:
                _logger.error(
                    "POS_SEQ DEBUG WRITE: session_id=%s config_id=%s old_name=%s -> new_name=%s forced_session_name=%s",
                    s.id,
                    s.config_id.id if s.config_id else None,
                    s.name,
                    vals.get("name"),
                    s.forced_session_name,
                )

        res = super().write(vals)

        # PROTECCIÓN: si alguien lo pisó, lo restauramos
        for s in self:
            if s.forced_session_name and s.name != s.forced_session_name:
                _logger.error(
                    "POS_SEQ DEBUG RESTORE: session_id=%s name was overwritten (%s). Restoring to %s",
                    s.id,
                    s.name,
                    s.forced_session_name,
                )
                super(PosSession, s.sudo()).write({"name": s.forced_session_name})

        return res
