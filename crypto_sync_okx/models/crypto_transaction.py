import json
from datetime import datetime

from odoo import models


class CryptoTransaction(models.Model):
    _inherit = "crypto.transaction"

    def process(self):
        super().process()
        transactions = self.filtered(lambda x: x.bank_account_id.bank_id.crypto_provider == "okx")
        if not transactions:
            return

        currencies = {cur.okx_api_code: cur for cur in self.env["res.currency"].search([("okx_api_code", "!=", False)])}

        for transaction in transactions:
            try:
                for tx in transaction.input_ids:
                    data = json.loads(tx.raw)

                    if tx.from_csv:
                        d = datetime.strptime(data["create_time"], "%Y/%m/%d %H:%M")  # "%d.%m.%Y %H:%M:%S"
                        if data["biz_line_en"] == "spot":
                            trade_name = "Trade OKX ({}, {})".format(d, data["instrument_name"])
                            self.env["crypto.transaction.detail"].create(
                                {
                                    "transaction_id": transaction.id,
                                    "name": trade_name,
                                    "date": d,
                                    "currency_id": currencies[data["currency_name"]].id,
                                    "value": float(data["amount"]) * (-1 if data["bill_type_en"] == "sell" else 1),
                                }
                            )
                            if float(data["fee"]) and data["bill_type_en"] == "buy":
                                self.env["crypto.transaction.detail"].create(
                                    {
                                        "transaction_id": transaction.id,
                                        "name": "Fee: " + trade_name,
                                        "date": d,
                                        "currency_id": currencies[data["currency_name"]].id,
                                        "value": float(data["fee"]),
                                    }
                                )
                    else:
                        d = datetime.fromtimestamp(int(data["ts"]) / 1000)

                        if tx.provider_source == "trade":
                            # TODO: Check this because I'm not sure that the currencies are ordered
                            inst_curs = data["instId"].split("-")
                            self.env["crypto.transaction.detail"].create(
                                {
                                    "transaction_id": transaction.id,
                                    "name": data["tradeId"],
                                    "date": d,
                                    "currency_id": currencies[inst_curs[0]].id,
                                    "value": float(data["sz"]) * (-1 if data["side"] == "sell" else 1),
                                }
                            )
                            self.env["crypto.transaction.detail"].create(
                                {
                                    "transaction_id": transaction.id,
                                    "name": data["tradeId"],
                                    "date": d,
                                    "currency_id": currencies[inst_curs[1]].id,
                                    "value": float(data["sz"])
                                    * float(data["px"])
                                    * (-1 if data["side"] == "buy" else 1),
                                }
                            )
                        elif tx.provider_source == "deposit":
                            self.env["crypto.transaction.detail"].create(
                                {
                                    "transaction_id": transaction.id,
                                    "name": data["depId"],
                                    "date": d,
                                    "currency_id": currencies[data["ccy"]].id,
                                    "value": float(data["amt"]),
                                }
                            )
                        elif tx.provider_source == "withdrawal":
                            out = {
                                "transaction_id": transaction.id,
                                "name": data["wdId"],
                                "date": d,
                                "currency_id": currencies[data["ccy"]].id,
                                "value": -float(data["amt"]),
                            }
                            self.env["crypto.transaction.detail"].create(out)

                            out["name"] = "Fee: " + out["name"]
                            out["currency_id"] = currencies[data["feeCcy"]].id
                            out["value"] = -float(data["fee"])
                            self.env["crypto.transaction.detail"].create(out)

                transaction.state = "ready"
            except Exception as e:
                transaction.state = "error"
                transaction.error = str(e)
