# -*- coding: utf-8 -*-
{
    "name": "CryptoRate",
    "version": "14.0.0.2.0",
    "description": """
Base module for getting cryptocurrency rates in Odoo
""",
    "author": "Yannis Burkhalter",
    "website": "https://github.com/nymtech-odoo/crypto_kit/tree/14.0/crypto_rate",
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
