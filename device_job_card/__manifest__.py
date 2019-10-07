# -*- coding: utf-8 -*-
{
    'name': "Devices",
    'summary': """""",
    'description': """
    """,

    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'category': 'Maintenance',
    'version': '12.0.1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/serial_number_views.xml',
        'views/device_model_views.xml',
    ],

    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}