import json
from datetime import datetime

from odoo import models


class CryptoTransaction(models.Model):
    _inherit = "crypto.transaction"

    def process(self):
        super().process()
        transactions = self.filtered(lambda x: x.bank_account_id.bank_id.crypto_provider == "kraken")
        if not transactions:
            return

        currencies = {
            cur.kraken_api_code: cur
            for cur in self.env["res.currency"].search(
                [
                    ("kraken_api_code", "!=", False),
                ]
            )
        }

        for transaction in transactions:
            try:
                for tx in transaction.input_ids:
                    name, data = json.loads(tx.raw)

                    out = {
                        "transaction_id": transaction.id,
                        "name": name,
                        "date": datetime.fromtimestamp(float(data["time"])),
                        "currency_id": currencies[data["asset"]].id,
                        "value": float(data["amount"]),
                    }
                    self.env["crypto.transaction.detail"].create(out)

                    fee = -float(data["fee"])
                    if fee:
                        out["name"] = "Fee: " + name
                        out["value"] = fee
                        self.env["crypto.transaction.detail"].create(out)

                transaction.state = "ready"
            except Exception as e:
                transaction.state = "error"
                transaction.error = str(e)
