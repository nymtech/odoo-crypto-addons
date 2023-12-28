from odoo import _, fields, models
from odoo.exceptions import UserError


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    crypto_provider = fields.Selection(string="Crypto Provider", related="bank_id.crypto_provider")
    crypto_auto_sync = fields.Boolean("Synchronize automatically")
    crypto_sync_done = fields.Boolean("Synched for today")
    crypto_sync_counter = fields.Integer("Sync Counter")

    explorer_link = fields.Char("Wallet Explorer Link", compute="_compute_explorer_link")

    def get_transactions_from_api(self):
        return self.env["crypto.transaction"]

    def get_transactions_from_csv(self, csv_file):
        raise UserError(_("CSV import not implemented yet! Sorry, please contact us."))

    def _cron_crypto_sync(self):
        bank_account = self.search(
            [("crypto_auto_sync", "=", True), ("crypto_sync_done", "=", False)],
            limit=1,
            order="crypto_sync_counter",
        )
        if not bank_account:
            return

        tx = bank_account.get_transactions_from_api()

        bank_account.crypto_sync_counter += 1
        if not tx:
            bank_account.crypto_sync_done = True

    def _cron_crypto_sync_reset_states(self):
        if not self.search(
            [("crypto_auto_sync", "=", True), ("crypto_sync_done", "=", False)],
            limit=1,
            count=True,
        ):
            self.search([("crypto_auto_sync", "=", True)]).write(
                {
                    "crypto_sync_done": False,
                    "crypto_sync_counter": 0,
                }
            )

    def _compute_explorer_link(self):
        self.filtered(lambda x: not x.explorer_link).explorer_link = False

    def open_on_explorer(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.explorer_link,
            "target": "new",
        }
