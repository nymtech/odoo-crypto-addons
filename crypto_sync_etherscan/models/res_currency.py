from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCurrency(models.Model):
    _inherit = "res.currency"

    ethereum_smart_contract = fields.Char(
        "Ethereum Smart Contract", help='For Ether itself, set to "ETH".'
    )

    @api.constrains("ethereum_smart_contract")
    def _check_ethereum_smart_contract(self):
        for cur in self.filtered(lambda x: x.ethereum_smart_contract):
            if cur.ethereum_smart_contract == "ETH":
                continue
            if not cur.ethereum_smart_contract.startswith("0x"):
                raise ValidationError(
                    _('The Ethereum smart contract must start with "0x".')
                )
            if len(cur.ethereum_smart_contract) != 42:
                raise ValidationError(
                    _(
                        'The Ethereum smart contract must be 42 characters long including "0x".'
                    )
                )

    def open_etherscan(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "https://etherscan.io/token/" + self.ethereum_smart_contract,
            "target": "new",
        }
