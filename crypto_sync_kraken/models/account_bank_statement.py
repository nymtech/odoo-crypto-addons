import json
from datetime import datetime

from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def recompute_balance(self):
        super().recompute_balance()

        for statement in self:
            bank_id = statement.journal_id.bank_account_id.bank_id
            if bank_id.crypto_provider != "kraken":
                continue

            bals = {"balance_start": 0, "balance_end_real": 0}
            for bal in bals.keys():
                line_id = statement.line_ids[0 if bal == "balance_start" else -1]
                ts = int(datetime.fromordinal(line_id.date.toordinal()).timestamp())

                if bal == "balance_end_real":
                    ts += 86400  # 1 day

                input_ids = line_id.crypto_transaction_id.transaction_id.input_ids
                if not input_ids:
                    continue
                data = json.loads(input_ids[0].raw)

                bals[bal] = float(data[1]["balance"])

            statement.write({**bals})
