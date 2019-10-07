# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    maintenance_id = fields.Many2one('maintenance.request', string="Maintenance")


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    maintenance_id = fields.Many2one('maintenance.request', string="Maintenance")