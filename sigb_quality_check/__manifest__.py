
{
    'name': 'Many2many operation in quality check',
    'version': '1.0',
    'sequence': 1,
    'category': 'MRP',
    'summary': 'Many2many operation in quality check',
    'author': 'Socius IGB',
    'website': 'http://www.sociusigb.com/',
    'license': 'Other proprietary',
    'description': """
This module is for used to customize Many2many operation in quality check.
        """,
    'depends': ['mrp_workorder'],
    'data': [
        'views/quality.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
