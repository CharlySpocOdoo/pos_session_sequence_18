import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.model_create_multi
    def create(self, vals_list):
        seq_id = self.env.context.get("force_pos_session_sequence_id")

        _logger.info(
            "POS_SEQ DEBUG pos.session.create: ctx force_pos_session_sequence_id=%s vals_count=%s first_vals_name=%s config_id=%s",
            seq_id,
            len(vals_list),
            (vals_list[0] or {}).get("name") if vals_list else None,
            (vals_list[0] or {}).get("config_id") if vals_list else None,
        )

        if seq_id:
            seq = self.env["ir.sequence"].browse(seq_id)
            _logger.info(
                "POS_SEQ DEBUG pos.session.create: using seq id=%s name=%s code=%s prefix=%s next=%s",
                seq.id,
                seq.name,
                seq.code,
                seq.prefix,
                seq.number_next_actual,
            )

            for vals in vals_list:
                if vals.get("name") in (False, None, "", "/"):
                    new_name = seq.next_by_id()
                    _logger.info(
                        "POS_SEQ DEBUG pos.session.create: forcing name from %s to %s",
                        vals.get("name"),
                        new_name,
                    )
                    vals["name"] = new_name
                else:
                    _logger.info(
                        "POS_SEQ DEBUG pos.session.create: name already present (%s), not forcing",
                        vals.get("name"),
                    )
        else:
            _logger.warning("POS_SEQ DEBUG pos.session.create: NO ctx force_pos_session_sequence_id")

        session = super().create(vals_list)

        _logger.info(
            "POS_SEQ DEBUG pos.session.create: created session ids=%s names=%s",
            session.ids,
            session.mapped("name"),
        )
        return session
