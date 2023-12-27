# -*- coding: utf-8 -*-
{
    "name": "CryptoSync: Cosmos",
    "version": "14.0.0.2.0",
    "description":
        """
Sync transactions from the Cosmos blockchain.

The GraphQL API used is provided by Nym Technologies and is expected to change.
""",
    "author": "Yannis Burkhalter",
    "website": "https://github.com/nymtech-odoo/crypto_kit/tree/14.0/crypto_sync_cosmos",
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": ["crypto_sync"],
    "data": [
        "views/res_bank.xml",
        "views/res_currency.xml",
        "views/res_partner_bank.xml",
    ],
    "external_dependencies": {
        "python": ["gql", "aiohttp"],
    },
}
