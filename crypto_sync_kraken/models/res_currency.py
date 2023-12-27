from odoo import fields, models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    kraken_api_code = fields.Char("Kraken API Code")
