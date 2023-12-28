# -*- coding: utf-8 -*-
{
    "name": "CryptoKit",
    "version": "15.0.0.1.0",
    "description": """
Cryptocurrency base module for Odoo
""",
    "author": "Yannis Burkhalter",
    "website": "https://github.com/nymtech-odoo/crypto_kit/tree/15.0",
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": ["account"],
    "data": [
        "security/groups.xml",
        "views/res_bank.xml",
        "views/res_currency.xml",
        "data/menu.xml",
    ],
}
