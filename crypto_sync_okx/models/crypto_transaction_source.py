from odoo import fields, models


class CryptoTransactionSource(models.Model):
    _inherit = "crypto.transaction.source"

    provider_source = fields.Selection(
        selection_add=[
            ("trade", "Trade"),
            ("deposit", "Deposit"),
            ("withdrawal", "Withdrawal"),
        ]
    )
