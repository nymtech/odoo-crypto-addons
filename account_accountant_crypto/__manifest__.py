# -*- coding: utf-8 -*-
{
    "name": "Crypto × Accounting",
    "version": "14.0.1.0.0",
    "description":
        """
Glue module to update crypto menu when account_accountant is installed.
""",
    "author": "Yannis Burkhalter",
    "website":
        "https://github.com/nymtech-odoo/crypto_kit/tree/14.0/account_accountant_crypto",
    "license": "AGPL-3",
    "category": "Hidden",
    "depends": ["account_accountant", "crypto_kit"],
    "data": ["data/menu.xml"],
    "auto_install": True,
}
