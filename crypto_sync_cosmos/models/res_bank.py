from odoo import fields, models


class ResBank(models.Model):
    _inherit = "res.bank"

    crypto_provider = fields.Selection(selection_add=[("cosmos", "Cosmos")])
    cosmos_graphql_url = fields.Char("Cosmos API GraphQL Endpoint")
