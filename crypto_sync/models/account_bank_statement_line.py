from odoo import fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    crypto_transaction_id = fields.Many2one("crypto.transaction.detail", string="Crypto Transaction", readonly=True)
    tx_explorer_link = fields.Char("Explorer Link", related="crypto_transaction_id.transaction_id.explorer_link")

    def unlink(self):
        self.crypto_transaction_id.state = "ready"
        return super().unlink()

    def open_tx_on_explorer(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.tx_explorer_link,
            "target": "new",
        }
