from odoo import fields, models

# Trades: https://support.kraken.com/hc/en-us/articles/360001184886-Explanation-of-Trade-Fields
# Ledger: https://support.kraken.com/hc/en-us/articles/360001169383-How-to-interpret-Ledger-history-fields


class CryptoTransactionSource(models.Model):
    _inherit = "crypto.transaction.source"

    provider_source = fields.Selection(
        selection_add=[
            ("trades", "Trades"),
            ("ledger", "Ledger"),
        ]
    )
