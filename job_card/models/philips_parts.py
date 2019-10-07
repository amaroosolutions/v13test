# -*- coding: utf-8 -*-

from odoo import models, fields


class PhilipsParts(models.Model):
    _name = 'philips.parts'
    _description = 'This model is used to store philips part information'

    name = fields.Char("Name", required=True)
    description = fields.Char(string='Description')
