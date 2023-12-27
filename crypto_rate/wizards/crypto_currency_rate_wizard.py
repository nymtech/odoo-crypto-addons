from odoo import fields, models


class CryptoCurrencyRateWizard(models.TransientModel):
    _name = "crypto.currency.rate.wizard"
    _description = "Get Cryptocurrency Rates Wizard"

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        domain=[("crypto_rate_provider", "!=", False)],
    )
    rate_date = fields.Date(
        "Date",
        required=True,
        default=fields.Date.today,
    )

    def get_crypto_currency_rate(self):
        self.currency_id.get_crypto_currency_rate(self.rate_date)
