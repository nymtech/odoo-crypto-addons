import base64
import csv
import io
import json

from odoo import api, fields, models


class CryptoImportTransactionsWizard(models.TransientModel):
    _name = "crypto.import.transactions.wizard"
    _description = "Import Cryptocurrency Transactions Wizard"

    bank_account_ids = fields.Many2many(
        "res.partner.bank",
        string="Wallets",
        domain=[("bank_id.crypto_provider", "!=", False)],
    )
    bank_account_id = fields.Many2one(
        "res.partner.bank",
        string="Wallet",
        domain=[("bank_id.crypto_provider", "!=", False)],
        compute="_compute_bank_account_id",
        readonly=False,
    )
    use_csv = fields.Boolean("Import from a CSV file")
    csv_file = fields.Binary("CSV File")
    csv_filename = fields.Char("CSV Filename")

    @api.depends("bank_account_ids")
    def _compute_bank_account_id(self):
        for wizard in self:
            wizard.bank_account_id = wizard.bank_account_ids and wizard.bank_account_ids[
                0]

    def get_transactions_from_api(self):
        return self.bank_account_ids.get_transactions_from_api().get_action_return()

    def get_transactions_from_csv(self):
        csv_reader = csv.DictReader(
            io.StringIO(base64.b64decode(self.csv_file).decode())
        )
        transactions = self.env["crypto.transaction"]

        i = 0
        for row in csv_reader:
            i += 1
            transactions |= self.env["crypto.transaction"].create({
                "name": self.csv_filename + ":" + str(i),
                "bank_account_id": self.bank_account_id.id,
                "input_ids": [(0, 0, {
                    "from_csv": True,
                    "raw": json.dumps(row),
                })],
            })
        return transactions.get_action_return()
