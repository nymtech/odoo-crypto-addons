import json
import logging
import time

import requests
from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DELAY = 5


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    def get_transactions_from_api(self):
        all_transactions = super().get_transactions_from_api()
        bank_accounts = self.filtered(lambda x: x.bank_id.crypto_provider == "etherscan")

        for bank_account in bank_accounts:
            transactions = self.env["crypto.transaction"]

            for source in ("txlist", "txlistinternal", "tokentx"):
                data = self._etherscan_request(
                    {
                        "action": source,
                        "address": bank_account.acc_number.lower(),
                        "apikey": bank_account.bank_id.etherscan_api_key or "",
                    }
                )

                for tx in data:
                    transaction = transactions.filtered(lambda x: x.name == tx["hash"])
                    if not transaction:
                        exists = self.env["crypto.transaction"].search(
                            [
                                ("name", "=", tx["hash"]),
                                ("bank_account_id", "=", bank_account.id),
                            ],
                            limit=1,
                            count=True,
                        )
                        if exists:
                            # If the main transaction already exists, we have to not create the children
                            # because all children are created in the same time, so all of them alway exist
                            continue
                        transaction = self.env["crypto.transaction"].create(
                            {
                                "name": tx["hash"],
                                "bank_account_id": bank_account.id,
                            }
                        )
                        transactions |= transaction
                    self.env["crypto.transaction.source"].create(
                        {
                            "transaction_id": transaction[0].id,
                            "provider_source": source,
                            "raw": json.dumps(tx),
                        }
                    )

            all_transactions |= transactions
        bank_accounts.crypto_sync_done = True
        return all_transactions

    @api.model
    def _etherscan_request(self, params):
        url = "https://api.etherscan.io/api?module=account&action={action}&address={address}&apikey={apikey}".format(
            **params
        )
        if not params.get("apikey"):
            last_call = float(
                self.env["ir.config_parameter"].sudo().get_param("crypto_sync_etherscan.last_call_timestamp", 0)
            )
            s = max(0, DELAY - (time.time() - last_call))
            if s:
                _logger.info("Waiting {:.1f} s".format(s))
                time.sleep(s)

        _logger.info("GET " + url)
        data = requests.get(url).json()

        self.env["ir.config_parameter"].sudo().set_param("crypto_sync_etherscan.last_call_timestamp", time.time())

        if data["status"] == "0":
            if data["message"] == "No transactions found":
                return []
            raise UserError(_("An error was returned by the Etherscan API:\n{result}").format(**data))
        return data["result"]

    def _compute_explorer_link(self):
        super()._compute_explorer_link()
        for wallet in self.filtered(lambda x: x.bank_id.crypto_provider == "etherscan"):
            wallet.explorer_link = "https://etherscan.io/address/" + wallet.acc_number
