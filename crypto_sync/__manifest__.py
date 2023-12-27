# -*- coding: utf-8 -*-
{
    "name": "CryptoSync",
    "version": "14.0.0.2.0",
    "description": """
Base module for syncing cryptocurrency transactions in Odoo

""",
    "author": "Yannis Burkhalter",
    "website": "https://github.com/nymtech-odoo/crypto_kit/tree/14.0/crypto_sync",
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": ["crypto_kit"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_bank_statement.xml",
        "views/account_bank_statement_line.xml",
        "views/crypto_transaction.xml",
        "views/crypto_transaction_detail.xml",
        "views/res_partner_bank.xml",
        "wizards/crypto_generate_statements_wizard.xml",
        "wizards/crypto_import_transactions_wizard.xml",
        "data/actions.xml",
        "data/config_parameter.xml",
        "data/cron.xml",
        "data/menu.xml",
    ],
}
