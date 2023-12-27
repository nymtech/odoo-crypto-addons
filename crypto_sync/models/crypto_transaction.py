from odoo import _, fields, models


class CryptoTransaction(models.Model):
    _name = "crypto.transaction"
    _description = "Cryptocurrency Transaction"

    name = fields.Char("Transaction Identifier", readonly=True)
    bank_account_id = fields.Many2one(
        "res.partner.bank", string="Wallet", readonly=True, ondelete="restrict"
    )
    explorer_link = fields.Char("Explorer Link", compute="_compute_explorer_link")

    state = fields.Selection(
        [
            ("draft", "Draft"),  # transaction just created, needs to be processed
            ("ignored", "Ignored"),  # transaction created, but manually ignored
            ("error", "Error"),  # transaction failed to be processed
            ("ready", "Ready"),  # 1-n transaction.s available for statement generation
            ("partially", "Partially Done"),  # some transactions used in statements
            ("done", "Done"),  # all transactions imported or ignored
        ],
        string="State",
        default="draft",
        readonly=True,
    )
    error = fields.Text("Error Description", readonly=True)
    input_ids = fields.One2many(
        "crypto.transaction.source", "transaction_id", string="Input", readonly=True
    )
    output_ids = fields.One2many(
        "crypto.transaction.detail", "transaction_id", string="Output", readonly=True
    )

    def reset(self):  # output: [draft]
        self = self.filtered(lambda x: x.state in ("draft", "error", "ready"))
        self.output_ids.unlink()
        self.input_ids.error = False
        self.error = False
        self.state = "draft"
        return self

    def process(self):  # output: [ready|error]
        return self.reset()

    def ignore(self):  # output: [ignored]
        self = self.filtered(lambda x: x.state in ("draft", "error", "ready"))
        self.output_ids.unlink()
        self.input_ids.error = False
        self.error = False
        self.state = "ignored"

    def revert_ignore(self):  # output: [draft]
        self = self.filtered(lambda x: x.state == "ignored")
        self.state = "draft"

    def ignore_rest(self):  # output: [done]
        self.filtered(lambda x: x.state in ("ready", "partially")).output_ids.filtered(
            lambda x: x.state == "ready"
        ).state = "ignored"

    def revert_ignore_rest(self):  # output: [ready|partially]
        self.filtered(lambda x: x.state in ("done")).output_ids.filtered(
            lambda x: x.state == "ignored"
        ).state = "ready"

    def _recompute_state(self):  # output: [ready|partially|done]
        self = self.filtered(lambda x: x.state in ("ready", "partially", "done"))
        for tx in self:
            nb_ready = len(tx.output_ids.filtered(lambda x: x.state == "ready"))
            if nb_ready == len(tx.output_ids):
                tx.state = "ready"
            elif nb_ready == 0:
                tx.state = "done"
            else:
                tx.state = "partially"

    def unlink(self):
        self = self.filtered(lambda x: x.state in ("draft", "ignored", "error", "ready"))
        self.output_ids.unlink()
        self.input_ids.unlink()
        return super().unlink()

    def get_action_return(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Imported Transactions"),
            "res_model": "crypto.transaction",
            "domain": [("id", "in", self.ids)],
            "view_mode": "tree,form",
        }

    def _compute_explorer_link(self):
        self.filtered(lambda x: not x.explorer_link).explorer_link = False

    def open_on_explorer(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.explorer_link,
            "target": "new",
        }
