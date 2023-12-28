# -*- coding: utf-8 -*-
{
    "name": "CryptoRate",
    "version": "15.0.0.1.0",
    "description": """
Base module for getting cryptocurrency rates in Odoo
""",
    "author": "Yannis Burkhalter",
    "website": "https://github.com/nymtech-odoo/crypto_kit/tree/15.0/crypto_rate",
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": ["crypto_kit"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_currency.xml",
        "wizards/crypto_currency_rate_wizard.xml",
        "data/cron.xml",
    ],
}
