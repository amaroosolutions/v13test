from odoo import models, fields


class DelayReason(models.Model):
    _name = 'delay.reason'
    _description = 'These model is used for delay for any reason'

    name = fields.Char(string='Reason', required=True)
