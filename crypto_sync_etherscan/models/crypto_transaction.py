import json
from datetime import datetime

from odoo import _, models


class CryptoTransaction(models.Model):
    _inherit = "crypto.transaction"

    def process(self):
        super().process()
        transactions = self.filtered(
            lambda x: x.bank_account_id.bank_id.crypto_provider == "etherscan"
        )
        if not transactions:
            return

        currencies = {
            cur.ethereum_smart_contract: cur
            for cur in
            self.env["res.currency"].search([("ethereum_smart_contract", "!=", False)])
        }
        if "ETH" not in currencies:
            transactions.state = "error"
            transactions.error = _(
                'ETH currency not found. Please, create the ETH currency and set the field "Ethereum Smart Contract" to "ETH".'
            )
            return
        ETH = currencies["ETH"]

        for transaction in transactions:
            try:
                error = False
                address = transaction.bank_account_id.acc_number.lower()

                for tx in transaction.input_ids:
                    data = json.loads(tx.raw)

                    if tx.provider_source == "txlistinternal":
                        if data["type"] == "call":
                            pass  # normal case
                        elif data["type"] == "create":
                            continue  # ignore
                        else:
                            error = True
                            tx.error = _(
                                "Unknown internal transaction type! Please contact us."
                            )

                    multiplier = -1 if address == data["from"] else 1
                    exp = -float(data.get("tokenDecimal", 18))
                    value = multiplier * float(data["value"]) * 10**exp
                    if value:
                        out = {
                            "transaction_id": transaction.id,
                            "name": data["hash"],
                            "date": datetime.fromtimestamp(int(data["timeStamp"])),
                            "address": data["to"] if multiplier == -1 else data["from"],
                            "value": value,
                        }
                        if tx.provider_source in ("txlist", "txlistinternal"):
                            out["currency_id"] = ETH.id
                        elif tx.provider_source == "tokentx":
                            if data["contractAddress"] not in currencies:
                                error = True
                                tx.error = _(
                                    "No currency found with smart contract: {contractAddress}\n"
                                    "Additional infos:\n"
                                    "- Token name: {tokenName}\n"
                                    "- Token symbol: {tokenSymbol}\n"
                                    "If you don't know this token, you should add its contract address on the blacklist.\n"
                                    'Otherwise, you have to create the currency and set the field "Ethereum Smart Contract" to "{contractAddress}".'
                                ).format(**data)
                                continue
                            out["currency_id"] = currencies[data["contractAddress"]].id

                        self.env["crypto.transaction.detail"].create(out)

                    if tx.provider_source == "txlist" and multiplier == -1:
                        fee = (
                            -float(data.get("gasPrice", 0)) *
                            float(data.get("gasUsed", 0)) * 10**-18
                        )
                        if fee:
                            self.env["crypto.transaction.detail"].create({
                                "transaction_id": transaction.id,
                                "name": "Fee: " + data["hash"],
                                "date": datetime.fromtimestamp(int(data["timeStamp"])),
                                "currency_id": ETH.id,
                                "value": fee,
                            })

                transaction.state = "error" if error else "ready"
            except Exception as e:
                transaction.state = "error"
                transaction.error = str(e)

    def _compute_explorer_link(self):
        super()._compute_explorer_link()
        for tx in self.filtered(
            lambda x: x.bank_account_id.bank_id.crypto_provider == "etherscan"
        ):
            tx.explorer_link = "https://etherscan.io/tx/" + tx.name
