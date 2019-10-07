
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    product_id = fields.Many2one('product.product',  string='Product For Job Card Hours')
