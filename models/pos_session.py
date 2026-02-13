import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = "pos.session"

    # Guardamos el nombre final (solo para auditoría / debug)
    forced_session_name = fields.Char(copy=False, readonly=True)

    # Guardamos qué secuencia debe usar esta sesión (sin consumirla en create)
    forced_session_sequence_id = fields.Many2one(
        "ir.sequence",
        copy=False,
        readonly=True,
        ondelete="restrict",
    )

    @api.model_create_multi
    def create(self, vals_list):
        seq_id = self.env.context.get("force_pos_session_sequence_id")
        _logger.warning(
            "POS_SEQ DEBUG create: ctx force_pos_session_sequence_id=%s vals_count=%s",
            seq_id, len(vals_list)
        )

        # NO consumir next_by_id aquí.
        # Solo recordamos qué secuencia debe usarse en esta sesión.
        if seq_id:
            for vals in vals_list:
                # Si ya venía definida por alguna razón, respetamos.
                vals.setdefault("forced_session_sequence_id", seq_id)

        sessions = super().create(vals_list)

        _logger.warning(
            "POS_SEQ DEBUG create: after super ids=%s names=%s forced_seq=%s",
            sessions.ids,
            sessions.mapped("name"),
            sessions.mapped("forced_session_sequence_id").mapped("id"),
        )
        return sessions

    def set_opening_control(self, cashbox_value, notes):
        """
        Aquí es donde Odoo 18 suele pisar el name.
        Nosotros generamos el nombre definitivo *aquí* usando la secuencia del POS.
        Así evitamos saltos por sesiones temporales/canceladas.
        """
        self.ensure_one()

        # Si este POS no tiene secuencia personalizada, comportamiento normal
        if not self.config_id.session_sequence_id:
            return super().set_opening_control(cashbox_value, notes)

        # Si ya le asignamos nombre definitivo antes, NO volver a consumir secuencia
        if self.forced_session_name:
            _logger.warning(
                "POS_SEQ DEBUG set_opening_control: already forced name=%s session_id=%s",
                self.forced_session_name, self.id
            )
            return super().set_opening_control(cashbox_value, notes)

        # Llamamos super primero (Odoo hace sus writes de apertura)
        res = super().set_opening_control(cashbox_value, notes)

        seq = self.config_id.session_sequence_id

        new_name = seq.next_by_id()
        _logger.warning(
            "POS_SEQ DEBUG set_opening_control: assigning final name session_id=%s pos=%s seq_id=%s new_name=%s old_name=%s",
            self.id,
            self.config_id.id,
            seq.id,
            new_name,
            self.name,
        )

        # Asignamos nombre final una sola vez
        self.sudo().write({
            "name": new_name,
            "forced_session_name": new_name,
            "forced_session_sequence_id": seq.id,
        })

        return res

    def write(self, vals):
        # Deja logs para que si algo vuelve a pisar el name lo veas, pero NO restauramos aquí.
        if "name" in vals:
            for s in self:
                _logger.error(
                    "POS_SEQ DEBUG WRITE: session_id=%s pos=%s old_name=%s -> new_name=%s forced_session_name=%s forced_seq=%s",
                    s.id,
                    s.config_id.id if s.config_id else None,
                    s.name,
                    vals.get("name"),
                    s.forced_session_name,
                    s.forced_session_sequence_id.id if s.forced_session_sequence_id else None,
                )
        return super().write(vals)
