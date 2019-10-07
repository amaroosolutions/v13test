{
    'name': 'Auto Maintenance Request Generator',
    'version': '12.0.3.17.06.2019',
    'category': 'Maintenance',
    'sequence': 1,
    'summary': 'Auto Maintenance Request Generator',
    'author': 'Kiran Kantesariya',
    'support': 'kiran.backup0412@gmail.com',
    'depends': ['maintenance', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/maintenance_cron.xml',
        'wizard/make_po_views.xml',
        'views/maintenance_views.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
