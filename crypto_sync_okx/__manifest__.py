# -*- coding: utf-8 -*-
{
    "name": "CryptoSync: OKX",
    "version": "14.0.0.1.0",
    "description": """
Sync transactions from an [OKX](https://www.okx.com/) account
""",
    "author": "Yannis Burkhalter",
    "website": "https://github.com/nymtech-odoo/crypto_kit/tree/14.0/crypto_sync_okx",
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": ["crypto_sync"],
    "data": [
        "views/res_currency.xml",
        "views/res_partner_bank.xml",
    ],
    "external_dependencies": {
        "python": ["python-okx"],
    },
}
