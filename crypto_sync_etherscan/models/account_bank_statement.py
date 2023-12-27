import json
import logging

import requests
from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def recompute_balance(self):
        super().recompute_balance()

        for statement in self:
            bank_id = statement.journal_id.bank_account_id.bank_id
            if bank_id.crypto_provider != "etherscan":
                continue

            api_key = bank_id.etherscan_api_key
            if not api_key:
                if self.env.context.get("called_from_interface"):
                    raise UserError(
                        _(
                            "An Etherscan API PRO is required to get historical balance.\n"
                            "You must provide a pro API key on the bank configuration."
                        )
                    )
                continue

            min_h = max_h = -1
            for tx in statement.line_ids.crypto_transaction_id.transaction_id.input_ids:
                data = json.loads(tx.raw)
                height = int(data.get("blockNumber"), 0)
                if not height:
                    continue
                if min_h == -1:
                    min_h = max_h = height
                    continue
                min_h = min(min_h, height)
                max_h = max(max_h, height)

            min_h -= 1

            bals = {"balance_start": 0, "balance_end_real": 0}
            for bal in bals.keys():
                height = min_h if bal == "balance_start" else max_h

                if statement.currency_id.ethereum_smart_contract == "ETH":
                    decimals = 18
                    balance_url = "https://api.etherscan.io/api?module=account&action=balancehistory&address={address}&blockno={blockno}&apikey={apikey}".format(
                        address=statement.journal_id.bank_account_id.acc_number,
                        blockno=height,
                        apikey=api_key,
                    )
                else:
                    decimals = 6  # TODO: in db
                    balance_url = "https://api.etherscan.io/api?module=account&action=tokenbalancehistory&contractaddress={contractaddress}&address={address}&blockno={blockno}&apikey={apikey}".format(
                        contractaddress=statement.currency_id.ethereum_smart_contract,
                        address=statement.journal_id.bank_account_id.acc_number,
                        blockno=height,
                        apikey=api_key,
                    )

                _logger.info("GET " + balance_url)
                data = requests.get(balance_url).json()
                if data["status"] == "0":
                    # An error was returned by the Etherscan API
                    continue
                bals[bal] = int(data["result"]) * 10**-decimals

            statement.write({**bals})
