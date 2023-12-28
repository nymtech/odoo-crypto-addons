# -*- coding: utf-8 -*-
{
    "name": "CryptoSync: Kraken",
    "version": "14.0.0.2.0",
    "description": """
Sync transactions from a [Kraken](https://www.kraken.com/) account
""",
    "author": "Yannis Burkhalter",
    "website": "https://github.com/nymtech-odoo/crypto_kit/tree/14.0/crypto_sync_kraken",
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": ["crypto_sync"],
    "data": [
        "views/res_currency.xml",
        "views/res_partner_bank.xml",
    ],
}
