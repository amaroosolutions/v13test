from odoo import models, fields


class DeviceModel(models.Model):
    _name = 'device.model'
    _description = 'These model is store the devices'

    name = fields.Char("Name")
    description = fields.Char("Description")
    partner_id = fields.Many2one('res.partner', string='OEM')
    is_nxstage_device = fields.Boolean(string='Is Nxstage Device')
    is_philips_device = fields.Boolean(string='Is Philips Device')


    _sql_constraints = [
        ('model_uniq', 'unique (name)', 'The name of the model number must be unique !')
    ]
