from odoo import fields, models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    # Allow more than 3 characters
    name = fields.Char(size=None)

    # Overriding the rounding to support up to 12 decimal numbers
    # Default is (12, 6)
    # We recommend not allowing more than 12 decimal places, as beyond that, the rounding gets weird
    rounding = fields.Float(digits=(24, 12))

    is_crypto = fields.Boolean(string="Cryptocurrency?")
