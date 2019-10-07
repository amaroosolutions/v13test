from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    part_line_id = fields.Many2one('oem.parts.line', string="OEM Line",
                                   copy=False)


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    job_number_id = fields.Many2one('job.number', string="Job Number")
