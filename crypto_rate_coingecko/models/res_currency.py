import logging

import requests
from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResCurrency(models.Model):
    _inherit = "res.currency"

    crypto_rate_provider = fields.Selection(selection_add=[("coingecko", "CoinGecko")])
    coingecko_api_code = fields.Char("CoinGecko API ID")

    def get_crypto_currency_rate(self, rate_date=False):
        super().get_crypto_currency_rate(rate_date)

        rate_date = rate_date or fields.Date.today()

        for currency in self.filtered(lambda x: x.crypto_rate_provider == "coingecko"):
            if not currency.coingecko_api_code:
                raise UserError(
                    _(
                        "Unable to get rates without the CoinGecko API ID. Please fill it."
                    )
                )

            url = "https://api.coingecko.com/api/v3/coins/{}/history?date={}".format(
                currency.coingecko_api_code, rate_date.strftime("%d-%m-%Y")
            )
            _logger.info("GET " + url)
            data = requests.get(url).json()

            if "status" in data:
                raise UserError(
                    _(
                        "An error {error_code} was returned by the CoinGecko API:\n{error_message}"
                    ).format(**data["status"])
                )

            all_rates = data["market_data"]["current_price"]
            code = self.env.company.currency_id.name.lower()
            if code not in all_rates:
                raise UserError(
                    _("CoinGecko does not provide value in {ccy}. Please contact us."
                     ).format(ccy=code.upper())
                )
            inverse_rate = all_rates[code]
            if inverse_rate == 0:
                raise UserError(
                    _("The rate provided by CoinGecko is 0. Please contact us.")
                )
            rate = 1 / inverse_rate

            self.env["res.currency.rate"].create({
                "name": rate_date,
                "currency_id": currency.id,
                "company_rate": rate,
            })

    def open_on_coingecko(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "https://www.coingecko.com/coins/" + self.coingecko_api_code,
            "target": "new",
        }
