import json
from datetime import datetime

from odoo import _, models

COSMOS_VALUE_FACTOR = 1e-06


class CryptoTransaction(models.Model):
    _inherit = "crypto.transaction"

    def process(self):
        super().process()
        transactions = self.filtered(lambda x: x.bank_account_id.bank_id.crypto_provider == "cosmos")
        if not transactions:
            return

        currencies = {
            cur.cosmos_api_code: cur
            for cur in self.env["res.currency"].search(
                [
                    ("cosmos_api_code", "!=", False),
                ]
            )
        }

        for transaction in transactions:
            try:
                error = False
                address = transaction.bank_account_id.acc_number.lower()
                fee_done = False

                for tx in transaction.input_ids:
                    data = json.loads(tx.raw)

                    if not data.get("transaction", {}).get("success"):
                        continue

                    value = data.get("value", {})

                    from_address = value.get("sender") or value.get("from_address")
                    to_address = value.get("msg", {}).get("create_account", {}).get("owner_address") or value.get(
                        "to_address"
                    )

                    multiplier = -1 if address == from_address else 1

                    base_out = {
                        "transaction_id": transaction.id,
                        "name": transaction.name,
                        "date": datetime.fromisoformat(data["block"]["timestamp"].ljust(26, "0")),
                        "address": to_address if multiplier == -1 else from_address,
                        "description": data.get("type"),
                    }

                    amounts = value.get("amount") or value.get("funds") or value.get("token")
                    if not isinstance(amounts, list):
                        amounts = [amounts]

                    if not fee_done and (multiplier == -1 or len(data.get("involved_accounts_addresses", [])) == 1):
                        fee = data.get("transaction", {}).get("fee", {}).get("amount")
                        if not isinstance(fee, list):
                            fee = [fee]
                        amounts += [{"fee": True, **f} for f in fee]

                    raw_log = json.loads(data.get("transaction", {}).get("raw_log", "{}"))
                    if raw_log:
                        for event in raw_log[0].get("events", []):
                            if event.get("type") != "wasm-v2_withdraw_delegator_reward":
                                continue
                            for attribute in event.get("attributes", []):
                                if attribute.get("key") != "amount":
                                    continue
                                amounts.append(
                                    {
                                        "amount": "-" + attribute["value"][:-4],
                                        "denom": attribute["value"][-4:],
                                        "description": "withdraw_delegator_reward",
                                    }
                                )

                    msg = value.get("msg", {})
                    ignore = any(x in msg for x in ("delegate_to_mixnode", "undelegate_from_mixnode"))

                    errors = []
                    for amount in amounts:
                        if not amount:
                            continue
                        out = base_out.copy()
                        code = amount.get("denom")

                        if code not in currencies:
                            errors.append(
                                _("No currency found with Cosmos API code: {cosmos_api_code}").format(
                                    cosmos_api_code=code
                                )
                            )
                            continue
                        currency = currencies[code]

                        out["currency_id"] = currency.id
                        out["value"] = multiplier * float(amount.get("amount", 0)) * COSMOS_VALUE_FACTOR
                        if "description" in amount:
                            out["description"] += " ; " + amount.get("description")

                        if "fee" in amount:
                            out["name"] = "Fee: " + out["name"]
                            out["value"] = -abs(out["value"])
                            fee_done = True

                        if not ignore or "fee" in amount:
                            self.env["crypto.transaction.detail"].create(out)

                    if errors:
                        error = True
                        tx.error = "\n".join(errors)

                transaction.state = "error" if error else "ready"
            except Exception as e:
                transaction.state = "error"
                transaction.error = str(e)

    def _compute_explorer_link(self):
        super()._compute_explorer_link()
        for tx in self.filtered(lambda x: x.bank_account_id.bank_id.crypto_provider == "cosmos"):
            tx.explorer_link = "https://www.mintscan.io/nyx/tx/" + tx.name
