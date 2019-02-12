# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Mass Duplicate Records',
    'version': '12.0.0.0',
    'author':'BrowseInfo',
    'category': 'Extra Tools',
    'sequence': 15,
    'summary': 'This apps Allows to duplicate multiple records from tree/list view in single records.',
    'description': """Allows you to duplicate multiple records from tree/list view.
    Mass Duplicate Records
    mass duplicate orders
    easy to duplicate records
    DUplicate mass orders
    duplicate mass records
    easy to duplicate mass records
    sales order mass duplicate sales order
    customer invoice mass duplicate invoice
    customer invoice mass duplicate customer invoice
    Supplier invoice mass duplicate supplier invoice
    vendor bills mass duplicate vendor bills
    purchase order mass duplicate purchase order
    manufacutring mass duplicate manufacturing order
    picking mass duplicate picking

Allows you to copy multiple records from tree/list view.
    Mass copy Records
    mass copy orders
    easy to copy records
    copy mass orders
    copy mass records
    easy to copy mass records
    sales order mass copy sales order
    customer invoice mass copy invoice
    customer invoice mass copy customer invoice
    Supplier invoice mass copy supplier invoice
    vendor bills mass copy vendor bills
    purchase order mass copy purchase order
    manufacutring mass copy manufacturing order
    picking mass copy picking


    """,
    'website': 'http://www.browseinfo.in',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/web_duplicate_views.xml',
        ],
   
    'css': [],
    "price": 25,
    "currency": 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
    "images":['static/description/Banner.png'],
}
