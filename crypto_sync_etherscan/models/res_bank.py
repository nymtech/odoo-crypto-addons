from odoo import fields, models


class ResBank(models.Model):
    _inherit = "res.bank"

    crypto_provider = fields.Selection(selection_add=[("etherscan", "Etherscan")])
    etherscan_api_key = fields.Char("Etherscan API Key")
