
{
    'name': 'Multi Route in BOM',
    'version': '1.0',
    'sequence': 1,
    'category': 'MRP',
    'summary': 'Ability to add multiple route in BOM',
    'author': 'Socius IGB',
    'website': 'http://www.sociusigb.com/',
    'license': 'Other proprietary',
    'description': """
This module is for used to customize BOM so that user can select multiple route for BOM.
        """,
    'depends': ['mrp'],
    'data': [
        'views/mrp.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
