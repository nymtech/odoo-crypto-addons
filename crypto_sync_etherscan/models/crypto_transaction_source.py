from odoo import fields, models


class CryptoTransactionSource(models.Model):
    _inherit = "crypto.transaction.source"

    provider_source = fields.Selection(
        selection_add=[
            ("txlist", "Normal"),
            ("txlistinternal", "Internal"),
            ("tokentx", "Token"),
        ]
    )
