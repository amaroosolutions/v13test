# -*- coding: utf-8 -*-
{
    'name': "Job Card",

    'summary': """""",

    'description': """""",

    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'category': 'Maintenance',
    'version': '12.0.1.2.30',

    # any module necessary for this one to work correctly
    'depends': ['device_job_card', 'hr', 'stock','purchase','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/delay_reason_views.xml',
        'views/job_number_views.xml',
        'data/ir_sequence_data.xml',
        'views/accessories_views.xml',
        'views/return_reason_views.xml',
        'views/sale_order_views.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'report/engineer_testing_note_template.xml',
        'report/engineer_testing_notes_view.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}