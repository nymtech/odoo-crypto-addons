from odoo import fields, models


class ResBank(models.Model):
    _inherit = "res.bank"

    crypto_provider = fields.Selection(selection_add=[("kraken", "Kraken")])
