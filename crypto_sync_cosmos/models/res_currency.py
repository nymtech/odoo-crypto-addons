from odoo import fields, models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    cosmos_api_code = fields.Char("Cosmos API Code")
