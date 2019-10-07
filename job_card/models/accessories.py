from odoo import models, fields


class Accessories(models.Model):
    _name = 'accessories.accessories'
    _description = "Accessories"

    name = fields.Char("Name", required=True)
