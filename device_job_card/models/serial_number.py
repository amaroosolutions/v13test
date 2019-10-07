# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SerialNumber(models.Model):
    _name = 'serial.number'
    _description = 'These model is store the serial number of device'

    name = fields.Char("Name")
    model_id = fields.Many2one('device.model', 'Model')
    description = fields.Char(
        related='model_id.description', string='Description', store=True)
    partner_id = fields.Many2one(
        related='model_id.partner_id', string='OEM', store=True)
    state = fields.Selection([('in_service', 'IN SERVICE'),
                              ('withdrawn', 'WITHDRAWN')], default='in_service', string="State")
    job_count = fields.Integer(
        compute='job_compute', string='B2B Jobs')

    _sql_constraints = [
        ('serial_uniq', 'unique (name)',
         'The name of the serial number  must be unique !')
    ]


    @api.multi
    def open_jobs(self):
        return {
            'name': _('RTB JOBS'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'job.number',
            'type': 'ir.actions.act_window',
            'domain': [('serial_id', '=', self.id)],
            'context':{'default_serial_id':self.id},
        }

    @api.multi
    def job_compute(self):
        for serial_rec in self:
            job_count = self.env['job.number'].search_count(
                [('serial_id', '=', serial_rec.id)])
            serial_rec.job_count = job_count

