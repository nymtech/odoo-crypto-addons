from odoo import _, fields, models
from odoo.exceptions import UserError


class ResCurrency(models.Model):
    _inherit = "res.currency"

    crypto_rate_provider = fields.Selection([], string="Crypto Rate Provider")

    def get_crypto_currency_rate(self, rate_date=False):
        rate_date = rate_date or fields.Date.today()
        if rate_date > fields.Date.today():
            raise UserError(_("No rates for future dates."))

        for currency in self.filtered("crypto_rate_provider"):
            if self.env["res.currency.rate"].search(
                [
                    ("name", "=", rate_date),
                    ("currency_id", "=", currency.id),
                ],
                limit=1,
                count=True,
            ):
                raise UserError(
                    _("A rate already exists for {ccy} on {date}.").format(
                        ccy=currency.name, date=rate_date
                    )
                )

    def action_crypto_currency_rate_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Get rates"),
            "res_model": "crypto.currency.rate.wizard",
            "target": "new",
            "context": {
                "default_currency_id": self.id,
            },
            "view_mode": "form",
            "view_id": self.env.ref("crypto_rate.view_crypto_currency_rate_wizard").id,
        }

    def _cron_crypto_rate(self):
        currencies = self.search([("crypto_rate_provider", "!=", False)])
        for currency in currencies:
            try:
                currency.get_crypto_currency_rate()
            except Exception:
                pass
