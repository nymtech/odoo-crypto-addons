from odoo import fields, models


class CryptoTransactionSource(models.Model):
    _name = "crypto.transaction.source"
    _description = "Cryptocurrency Transaction Source"

    transaction_id = fields.Many2one("crypto.transaction", string="Master Transaction", readonly=True)
    name = fields.Char("Transaction Identifier", related="transaction_id.name", store=True)
    provider_source = fields.Selection([], string="Source", readonly=True)
    from_csv = fields.Boolean("From CSV", readonly=True)
    raw = fields.Text("JSON", readonly=True)
    error = fields.Text("Error Description", readonly=True)
