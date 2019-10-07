from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    job_card_billing = fields.Selection([('total_hours', 'Total Hours'),
                                         ('workshop_hours', 'Workshop Hours'),
                                         ], string='Job Card Billing', default='total_hours')
