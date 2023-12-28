from odoo import fields, models


class CryptoGenerateStatementsWizard(models.TransientModel):
    _name = "crypto.generate.statements.wizard"
    _description = "Generate Cryptocurrency Statements Wizard"

    bank_account_ids = fields.Many2many("res.partner.bank", string="Wallets")
    date_from = fields.Date("From")
    date_to = fields.Date("To")
    group_by = fields.Selection(
        [("week", "By week"), ("month", "By month"), ("year", "By year")],
        string="Group",
    )

    def generate_statements(self):
        domain = [("state", "=", "ready")]
        if self.date_from:
            domain.append(("date", ">=", self.date_from))
        if self.date_to:
            domain.append(("date", "<=", self.date_to))
        if self.bank_account_ids:
            domain.append(("transaction_id.bank_account_id", "in", self.bank_account_ids.ids))
        return self.env["crypto.transaction.detail"].search(domain).generate_statements(self.group_by)
