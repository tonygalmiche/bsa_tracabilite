# -*- coding: utf-8 -*-

{
    'name': 'BSA Traçabilité',
    'version': '1.0',
    'category': 'InfoSaône',
    'description': """
BSA Traçabilité
""",
    'author': 'Tony GALMICHE',
    'maintainer': 'InfoSaône',
    'website': 'http://www.infosaone.com',
    'depends': ['base', 'product', 'stock', 'mrp', 'sale'],
    'data': ['is_bsa_tracabilite_menu.xml',
             'is_bsa_tracabilite_sequence.xml',
             'is_product_view.xml',
             'wizard/is_tracabilite_reception_view.xml',
             'wizard/is_tracabilite_livraison_view.xml',
             'is_stock_view.xml',
             'is_mrp_view.xml',
             'is_bsa_tracabilite_view.xml',
             'res_company_view.xml',
             'report/report.xml',
             'report/report_template.xml',
             'security/ir.model.access.csv',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

