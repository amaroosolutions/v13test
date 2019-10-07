# -*- coding: utf-8 -*-

from odoo import models, fields


class PartsRequired(models.Model):
    _name = 'parts.required'
    _description = "Parts Required"

    name = fields.Char(string='Name')
