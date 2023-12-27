# -*- coding: utf-8 -*-
{
    "name": "CryptoSync: Etherscan",
    "version": "14.0.0.2.0",
    "description":
        """
Sync transactions from [Etherscan](https://etherscan.io/)

For some endpoints, a Etherscan API PRO subscription may be required.
""",
    "author": "Yannis Burkhalter",
    "website":
        "https://github.com/nymtech-odoo/crypto_kit/tree/14.0/crypto_sync_etherscan",
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": ["crypto_sync"],
    "data": [
        "views/res_bank.xml",
        "views/res_currency.xml",
    ],
}
