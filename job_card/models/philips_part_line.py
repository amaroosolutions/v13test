# -*- coding: utf-8 -*-

from odoo import models, fields,api


class PhilipsPartsLine(models.Model):
    _name = 'philips.parts.line'
    _description = 'These model is store the details of philips parts'

    job_number_id = fields.Many2one('job.number', string='Job Number')
    product_id = fields.Many2one('philips.parts', string='Product', required=True)
    description = fields.Char(string='Description')
    quantity = fields.Float("Quantity")
    date = fields.Date(string='Date')
    user_id = fields.Many2one('res.users', string='User')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.description or self.product_id.name
