import json
import logging
from datetime import datetime

from odoo import _, fields, models
from odoo.addons.crypto_sync_cosmos.utils.graphql import graphql_request
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

GET_MESSAGES = """
{{
    action_messages_count(
        address: "{address}"
        executedAtStart: "{executed_at_start}"
        executedAtEnd: "{executed_at_end}"
        offset: {offset}
    ) {{
        limit
        offset
        total_count
    }}
    action_messages(
        address: "{address}"
        executedAtStart: "{executed_at_start}"
        executedAtEnd: "{executed_at_end}"
        offset: {offset}
    ) {{
        height
        index
        involved_accounts_addresses
        transaction_hash
        type
        funds
        transaction {{
            fee
            gas_used
            gas_wanted
            memo
            success
            raw_log
        }}
        block {{
            timestamp
        }}
        value
    }}
}}
"""


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    cosmos_offset = fields.Integer("Cosmos Offset", readonly=True)

    def _cosmos_date_format(self, datetime):
        return datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def get_transactions_from_api(self):
        all_transactions = super().get_transactions_from_api()
        bank_accounts = self.filtered(lambda x: x.bank_id.crypto_provider == "cosmos")

        for bank_account in bank_accounts:
            transactions = self.env["crypto.transaction"]

            payload = GET_MESSAGES.format(
                address=bank_account.acc_number.lower(),
                executed_at_start=self._cosmos_date_format(datetime.fromtimestamp(0)),
                executed_at_end=self._cosmos_date_format(datetime.now()),
                offset=bank_account.cosmos_offset,
            )

            _logger.info("POST " + bank_account.bank_id.cosmos_graphql_url)
            data = graphql_request(bank_account.bank_id.cosmos_graphql_url, payload)

            if "errors" in data:
                raise UserError(_("An error was returned by the Cosmos API:\n{errors}").format(**data))

            for tx in data["action_messages"]:
                transaction_hash = tx["transaction_hash"]
                transaction = transactions.filtered(lambda x: x.name == transaction_hash)
                if not transaction:
                    transaction = self.env["crypto.transaction"].search(
                        [
                            ("name", "=", transaction_hash),
                            ("bank_account_id", "=", bank_account.id),
                        ],
                        limit=1,
                    )
                if not transaction:
                    transaction = self.env["crypto.transaction"].create(
                        {
                            "name": transaction_hash,
                            "bank_account_id": bank_account.id,
                        }
                    )
                transactions |= transaction
                self.env["crypto.transaction.source"].create(
                    {
                        "transaction_id": transaction[0].id,
                        "raw": json.dumps(tx),
                    }
                )

            bank_account.cosmos_offset += len(data["action_messages"])
            all_transactions |= transactions
        return all_transactions

    def _compute_explorer_link(self):
        super()._compute_explorer_link()
        for wallet in self.filtered(lambda x: x.bank_id.crypto_provider == "cosmos"):
            if wallet.acc_number.startswith("gravity"):
                explorer = "gravity-bridge"
            elif wallet.acc_number.startswith("n1"):
                explorer = "nyx"

            wallet.explorer_link = "https://www.mintscan.io/{}/address/{}/".format(explorer, wallet.acc_number)
