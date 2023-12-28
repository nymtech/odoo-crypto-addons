import json

from odoo import fields, models
from odoo.addons.crypto_sync_kraken.utils.kraken import kraken_request


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    kraken_api_key = fields.Char("Kraken API Key")
    kraken_api_sec = fields.Char("Kraken Private Key")

    kraken_ledger_start = fields.Char("Kraken Ledger Start", readonly=True)
    kraken_ledger_end = fields.Char("Kraken Ledger End", readonly=True)
    kraken_ledger_ofs = fields.Integer("Kraken Ledger Offset", readonly=True)

    def get_transactions_from_api(self):
        all_transactions = super().get_transactions_from_api()
        bank_accounts = self.filtered(lambda x: x.bank_id.crypto_provider == "kraken")

        for bank_account in bank_accounts:
            transactions = self.env["crypto.transaction"]

            params = {
                "ofs": bank_account.kraken_ledger_ofs,
            }
            if bank_account.kraken_ledger_start:
                params["start"] = bank_account.kraken_ledger_start
            if bank_account.kraken_ledger_end:
                params["end"] = bank_account.kraken_ledger_end

            data = kraken_request(
                "/0/private/Ledgers",
                params,
                bank_account.kraken_api_key,
                bank_account.kraken_api_sec,
            ).json()
            ledger = list(data["result"]["ledger"].items())

            if not ledger:
                continue

            for ledger_id, ledger_entry in ledger:
                transaction = transactions.filtered(lambda x: x.name == ledger_id)
                if not transaction:
                    exists = self.env["crypto.transaction"].search(
                        [
                            ("name", "=", ledger_id),
                            ("bank_account_id", "=", bank_account.id),
                        ],
                        limit=1,
                        count=True,
                    )
                    if exists:
                        continue
                    transaction = self.env["crypto.transaction"].create(
                        {
                            "name": ledger_id,
                            "bank_account_id": bank_account.id,
                        }
                    )
                    transactions |= transaction
                self.env["crypto.transaction.source"].create(
                    {
                        "transaction_id": transaction[0].id,
                        "provider_source": "ledger",
                        "raw": json.dumps((ledger_id, ledger_entry)),
                    }
                )

            if bank_account.kraken_ledger_ofs == 0:
                bank_account.kraken_ledger_end = ledger[0][0]

            bank_account.kraken_ledger_ofs += len(ledger)
            if bank_account.kraken_ledger_ofs >= data["result"]["count"]:
                bank_account.kraken_ledger_start = bank_account.kraken_ledger_end
                bank_account.kraken_ledger_end = False
                bank_account.kraken_ledger_ofs = 0

            all_transactions |= transactions
        return all_transactions

    def kraken_reset(self):
        self.kraken_ledger_start = False
        self.kraken_ledger_end = False
        self.kraken_ledger_ofs = 0
