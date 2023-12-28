import json
import logging

from odoo import _, models
from odoo.addons.crypto_sync_cosmos.utils.graphql import graphql_request
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

COSMOS_VALUE_FACTOR = 1e-06

GET_BALANCE = """
{{
  action_account_balance(
    address: "{address}"
    height: {height}
  ) {{
    coins
  }}
}}
"""


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def recompute_balance(self):
        super().recompute_balance()

        for statement in self:
            bank_id = statement.journal_id.bank_account_id.bank_id
            if bank_id.crypto_provider != "cosmos":
                continue

            min_h = max_h = -1
            for tx in statement.line_ids.crypto_transaction_id.transaction_id.input_ids:
                data = json.loads(tx.raw)
                height = int(data.get("height", 0))
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
                payload = GET_BALANCE.format(
                    address=statement.journal_id.bank_account_id.acc_number.lower(),
                    height=min_h if bal == "balance_start" else max_h,
                )

                _logger.info("POST " + bank_id.cosmos_graphql_url)
                try:
                    data = graphql_request(bank_id.cosmos_graphql_url, payload)
                except Exception:
                    if self.env.context.get("called_from_interface"):
                        raise UserError(
                            _("An error occured during the Cosmos API query. Please try later or contact us.")
                        )
                    continue

                if "errors" in data:
                    if self.env.context.get("called_from_interface"):
                        raise UserError(_("An error was returned by the Cosmos API:\n{errors}").format(**data))
                    continue

                for coin in data["action_account_balance"]["coins"]:
                    if coin["denom"] == self.currency_id.cosmos_api_code:
                        bals[bal] = float(coin["amount"]) * COSMOS_VALUE_FACTOR

            statement.write({**bals})
