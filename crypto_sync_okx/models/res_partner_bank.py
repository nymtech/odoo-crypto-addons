import json

from odoo import fields, models
from okx import Funding

FLAG = "0"


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    okx_api_key = fields.Char("OKX API Key")
    okx_api_sec = fields.Char("OKX Secret Key")
    okx_api_passphrase = fields.Char("OKX Passphrase")

    okx_trade_after = fields.Char("OKX Trade After", readonly=True)

    def get_transactions_from_api(self):
        all_transactions = super().get_transactions_from_api()
        bank_accounts = self.filtered(lambda x: x.bank_id.crypto_provider == "okx")

        all_transactions |= bank_accounts._okx_get_transactions_from_api_deposit()
        all_transactions |= bank_accounts._okx_get_transactions_from_api_withdrawal()

        return all_transactions

    def _okx_get_transactions_from_api_deposit(self):
        all_transactions = self.env["crypto.transaction"]

        for bank_account in self.filtered(lambda x: x.bank_id.crypto_provider == "okx"):
            transactions = self.env["crypto.transaction"]

            fundingAPI = Funding.FundingAPI(
                bank_account.okx_api_key,
                bank_account.okx_api_sec,
                bank_account.okx_api_passphrase,
                False,
                FLAG,
            )
            result = fundingAPI.get_deposit_history()

            if not result["data"]:
                continue

            for deposit in result["data"]:
                transaction = transactions.filtered(lambda x: x.name == deposit["depId"])
                if not transaction:
                    exists = self.env["crypto.transaction"].search(
                        [
                            ("name", "=", deposit["depId"]),
                            ("bank_account_id", "=", bank_account.id),
                        ],
                        limit=1,
                        count=True,
                    )
                    if exists:
                        continue
                    transaction = self.env["crypto.transaction"].create(
                        {
                            "name": deposit["depId"],
                            "bank_account_id": bank_account.id,
                        }
                    )
                    transactions |= transaction
                self.env["crypto.transaction.source"].create(
                    {
                        "transaction_id": transaction[0].id,
                        "provider_source": "deposit",
                        "raw": json.dumps(deposit),
                    }
                )

            all_transactions |= transactions
        return all_transactions

    def _okx_get_transactions_from_api_withdrawal(self):
        all_transactions = self.env["crypto.transaction"]

        for bank_account in self.filtered(lambda x: x.bank_id.crypto_provider == "okx"):
            transactions = self.env["crypto.transaction"]

            fundingAPI = Funding.FundingAPI(
                bank_account.okx_api_key,
                bank_account.okx_api_sec,
                bank_account.okx_api_passphrase,
                False,
                FLAG,
            )
            result = fundingAPI.get_withdrawal_history()

            if not result["data"]:
                continue

            for withdrawal in result["data"]:
                transaction = transactions.filtered(lambda x: x.name == withdrawal["wdId"])
                if not transaction:
                    exists = self.env["crypto.transaction"].search(
                        [
                            ("name", "=", withdrawal["wdId"]),
                            ("bank_account_id", "=", bank_account.id),
                        ],
                        limit=1,
                        count=True,
                    )
                    if exists:
                        continue
                    transaction = self.env["crypto.transaction"].create(
                        {
                            "name": withdrawal["wdId"],
                            "bank_account_id": bank_account.id,
                        }
                    )
                    transactions |= transaction
                self.env["crypto.transaction.source"].create(
                    {
                        "transaction_id": transaction[0].id,
                        "provider_source": "withdrawal",
                        "raw": json.dumps(withdrawal),
                    }
                )

            all_transactions |= transactions
        return all_transactions
