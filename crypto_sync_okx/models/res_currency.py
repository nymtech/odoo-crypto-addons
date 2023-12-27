from odoo import fields, models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    okx_api_code = fields.Char("OKX API Code")
