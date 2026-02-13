import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = "pos.session"

    forced_session_name = fields.Char(copy=False, readonly=True)
    forced_session_sequence_id = fields.Many2one(
        "ir.sequence",
        copy=False,
        readonly=True,
        ondelete="restrict",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Odoo core consume la secuencia global 'pos.session' si 'name' viene vacío.
        Para POS con secuencia propia, evitamos ese consumo mandando name='/'.
        """
        seq_id_ctx = self.env.context.get("force_pos_session_sequence_id")

        # Detectar config_id (cuando el create viene desde open_ui)
        config_ids = [v.get("config_id") for v in vals_list if v.get("config_id")]
        configs = self.env["pos.config"].browse(list(set(config_ids))) if config_ids else self.env["pos.config"]
        config_map = {c.id: c for c in configs}

        for vals in vals_list:
            config = config_map.get(vals.get("config_id"))
            seq = None

            # Prioridad: contexto -> config.session_sequence_id
            if seq_id_ctx:
                seq = self.env["ir.sequence"].browse(seq_id_ctx)
            elif config and config.session_sequence_id:
                seq = config.session_sequence_id

            if seq:
                # Evitar que el core consuma la secuencia global
                vals.setdefault("name", "/")
                vals.setdefault("forced_session_sequence_id", seq.id)

        sessions = super().create(vals_list)

        _logger.warning(
            "POS_SEQ DEBUG create: created ids=%s names=%s forced_seq=%s",
            sessions.ids,
            sessions.mapped("name"),
            sessions.mapped("forced_session_sequence_id").mapped("id"),
        )
        return sessions

    def set_opening_control(self, cashbox_value, notes):
        """
        Consumimos la secuencia DEL POS una sola vez, al confirmar apertura.
        """
        self.ensure_one()
        res = super().set_opening_control(cashbox_value, notes)

        # Determinar secuencia final (forzada o por config)
        seq = self.forced_session_sequence_id or self.config_id.session_sequence_id
        if not seq:
            return res

        # Si ya quedó asignado, no consumir de nuevo
        if self.forced_session_name:
            return res

        new_name = seq.next_by_id()
        _logger.warning(
            "POS_SEQ DEBUG set_opening_control: session_id=%s pos=%s seq_id=%s new_name=%s old_name=%s",
            self.id,
            self.config_id.id if self.config_id else None,
            seq.id,
            new_name,
            self.name,
        )

        self.sudo().write({
            "name": new_name,
            "forced_session_name": new_name,
            "forced_session_sequence_id": seq.id,
        })
        return res

    def write(self, vals):
        if "name" in vals:
            for s in self:
                _logger.error(
                    "POS_SEQ DEBUG WRITE: session_id=%s pos=%s old_name=%s -> new_name=%s forced_name=%s forced_seq=%s",
                    s.id,
                    s.config_id.id if s.config_id else None,
                    s.name,
                    vals.get("name"),
                    s.forced_session_name,
                    s.forced_session_sequence_id.id if s.forced_session_sequence_id else None,
                )
        return super().write(vals)
