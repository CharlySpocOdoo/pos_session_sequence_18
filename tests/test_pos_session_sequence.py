from odoo.tests.common import TransactionCase

class TestPosSessionSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pos_config_id = cls.env.ref("point_of_sale.pos_config_main")

    def test_session_sequence(self):
        session = self.env["pos.session"].create({
            "config_id": self.pos_config_id.id,
            "user_id": self.env.ref("base.user_admin").id,
        })
        self.assertTrue(session.name)
