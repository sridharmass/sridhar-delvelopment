# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Pandas Report',
    'version': '1.0',
    'category': 'report',
    'sequence': 15,
    'summary': 'Simple report in Pandas',
    'website': 'https://www.ajaxmediatech.com/',
    'depends': ['base'],
    'data': [
        'views/cane_management_report_view.xml',
    ],
    'description':'Simple Report developing using pandas report',
    'installable': True,
    'auto_install': False,
    'application': True,
}
