# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from itertools import groupby


class MakePOWiz(models.TransientModel):
    _name = "make.po.wiz"

    @api.model
    def default_get(self, default_fields):
        res = super(MakePOWiz, self).default_get(default_fields)
        context = dict(self.env.context)
        if context.get('active_ids') and context.get('active_model') == 'maintenance.request':
            active_ids = self.env['maintenance.request'].browse(context['active_ids'])
            res.update({
                    'maintenance_ids': [(6, 0, active_ids.filtered(lambda l: l.subcontract and (len(l.mapped('po_line_ids').mapped('order_id')) < 1)).ids)]
                })
        return res

    maintenance_ids = fields.Many2many('maintenance.request', string="Maintenances")

    @api.multi
    def make_po(self):
        context = dict(self.env.context)
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        maintenance_obj = self.env['maintenance.request']
        if context.get('active_ids') and context.get('active_model') == 'maintenance.request' and self.maintenance_ids:
            for maintenance in self.maintenance_ids.sorted(key=lambda r: r.partner_id.id):
                maintenance_obj += maintenance

            purchase_list = []
            for partner, maintenance in groupby(maintenance_obj, lambda l: l.partner_id.id):
                main = list(maintenance)
                purchase_id = purchase_obj.create({
                        'partner_id': partner,
                        'company_id': self.env.user.company_id.id,
                        'origin': 'Maintenance',
                        'date_order': fields.Datetime.now(),
                        'date_planned': fields.Datetime.now(),
                    })
                for line in main:
                    # po_line = purchase_id.mapped('order_line').filtered(lambda p: p.product_id.id == line.product_id.id)
                    # if po_line:
                    #     po_line[0].product_qty += 1.0
                    #     line.maintenance_id = line.id
                    # else:
                    purchase_line_id = purchase_line_obj.create({
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'date_planned': fields.Datetime.now(),
                        'price_unit': line.product_id.standard_price,
                        'product_qty': 1.0,
                        'product_uom': line.product_id.uom_po_id.id,
                        'maintenance_id': line.id,
                        'order_id': purchase_id.id
                    })
                purchase_list.append(purchase_id.id)
            action = self.env.ref('purchase.purchase_rfq').read()[0]
            if len(purchase_list) > 1:
                action['domain'] = [('id', 'in', purchase_list)]
            elif len(purchase_list) == 1:
                action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
                action['res_id'] = purchase_list[0]
            else:
                action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            return action

