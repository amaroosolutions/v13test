# -*- coding: utf-8 -*-


from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class MaintenanceAuto(models.Model):
    _name = 'maintenance.auto'
    _rec_name = 'maintenance_name_id'
    _description = 'Maintenance Type'

    @api.multi
    @api.depends('last_date')
    def compute_next_due_date(self):
        for rec in self:
            if rec.period and rec.last_date:
                rec.next_due_date = rec.last_date + timedelta(days=rec.period)

    equipment_id = fields.Many2one('maintenance.equipment', string="Equipment")
    maintenance_name_id = fields.Many2one('maintenance.name', string="Name")
    period = fields.Integer('Frequency (Days)', default=10)
    maintenance_duration = fields.Float(help="Duration Hours.")
    last_date = fields.Date(string="Last Date", default=fields.Date.today())
    next_due_date = fields.Date(string="Next Due Date", compute="compute_next_due_date", store=True)
    subcontract = fields.Boolean(string="Subcontract")
    partner_id = fields.Many2one('res.partner', string="Vendor", domain="[('supplier', '=', True)]")
    product_id = fields.Many2one('product.product', string="Product")
    maintenance_team = fields.Many2one('maintenance.team', string="Responsable Team")
    responsible_user = fields.Many2one('res.users', string="Responsable User")

    @api.onchange('maintenance_name_id')
    def onchange_maintenance_name_id(self):
        if self.maintenance_name_id:
            self.period = self.maintenance_name_id.period
            self.period = self.maintenance_name_id.period
            self.maintenance_duration = self.maintenance_name_id.maintenance_duration
            self.maintenance_team = self.maintenance_name_id.maintenance_team
            self.responsible_user = self.maintenance_name_id.responsible_user
            

    @api.model
    def create_maintenance(self):
        auto_ids = self.search([])
        MT = self.env['maintenance.team']
        team = MT.sudo().search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        if not team:
            team = MT.search([], limit=1)

        for auto in auto_ids:
            current_date = fields.Date.today()
            due_date = auto.next_due_date
            if due_date and due_date >= current_date:
                diff = due_date - current_date
                if diff.days == auto.maintenance_name_id.new_request_generator_days:
                    maintenance_id = self.env['maintenance.request'].create({
                            'name': auto.maintenance_name_id.name + ' Request',
                            'equipment_id': auto.equipment_id.id,
                            'owner_user_id': SUPERUSER_ID,
                            'request_date': fields.Date.today(),
                            'maintenance_team_id': auto.maintenance_name_id.maintenance_team.id,
                            'user_id': auto.responsible_user.id,
                            'schedule_date': auto.next_due_date,
                            'duration': auto.maintenance_duration,
                            'maintenance_auto_id': auto.id,
                            
                        })
                    

class MaintenanceName(models.Model):
    _name = 'maintenance.name'

    name = fields.Char(string="Name")
    period = fields.Integer('Frequency (Days)', default=10)
    maintenance_duration = fields.Float(help="Duration Hours.")
    new_request_generator_days = fields.Integer(string="New Request Generator Days", default=30, required=True)
    maintenance_team = fields.Many2one('maintenance.team', string="Responsable Team")
    responsible_user = fields.Many2one('res.users', string="Responsable User")


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    maintenance_auto_ids = fields.One2many('maintenance.auto', 'equipment_id', string="Auto")


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    @api.multi
    def count_pos(self):
        for rec in self:
            rec.count_po = len(rec.po_line_ids.mapped('order_id'))

    maintenance_auto_id = fields.Many2one('maintenance.auto', string="Maintenance Type")
    po_ids = fields.One2many('purchase.order', 'maintenance_id', string="Purchases")
    po_line_ids = fields.One2many('purchase.order.line', 'maintenance_id', string="Purchases")
    count_po = fields.Integer(string="POS", compute="count_pos")
    subcontract = fields.Boolean(string="Subcontract", related="maintenance_auto_id.subcontract", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Vendor", related="maintenance_auto_id.partner_id", readonly=True)
    product_id = fields.Many2one('product.product', string="Product", related="maintenance_auto_id.product_id", readonly=True)

    # @api.onchange('maintenance_auto_id')
    # def onchange_maintenance_auto_id(self):
    #     if self.maintenance_auto_id and self.maintenance_auto_id.last_date:
    #         self.close_date = self.maintenance_auto_id.last_date


    @api.onchange('maintenance_auto_id')
    def onchange_maintenance_auto_id(self):
        if self.maintenance_auto_id and self.maintenance_auto_id.last_date:
            self.close_date = self.maintenance_auto_id.next_due_date

    @api.multi
    def write(self, vals):
        close_date = False
        for rec in self:
            close_date = vals.get('close_date', rec.close_date)
        if vals.get('close_date'):
            for rec in self:
                auto_id = vals.get('maintenance_auto_id', rec.maintenance_auto_id.id)
                if auto_id:
                    maintenance_auto_id = self.env['maintenance.auto'].browse(auto_id)
                    maintenance_auto_id.last_date = vals['close_date']
        res = super(MaintenanceRequest, self).write(vals)
        if 'stage_id' in vals:
            self.filtered(lambda m: m.stage_id.done).write({'close_date': close_date})
        return res

    @api.multi
    def action_create_po(self):
        po_ids = self.mapped('po_line_ids').mapped('order_id')
        if po_ids:
            raise UserError(_('Only one purchase order is allowed for each maintenance request.'))
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        auto_id = self.maintenance_auto_id
        if not auto_id or (auto_id and (not auto_id.subcontract or not auto_id.partner_id or not auto_id.product_id)):
            raise UserError(_('Make sure you have configured Sub Equipment and its is Subcontracting type.'))
        context = dict(self.env.context)
        context.update({
                'default_partner_id': auto_id.partner_id.id,
                'default_company_id': self.company_id.id,
                'default_origin': self.name + ' Maintenance',
                'default_date_order': fields.Datetime.now(),
                'default_date_planned': fields.Datetime.now(),
                'default_order_line': [(0, 0, {
                                'product_id': auto_id.product_id.id,
                                'name': auto_id.product_id.name,
                                'date_planned': fields.Datetime.now(),
                                'price_unit': auto_id.product_id.standard_price,
                                'product_qty': 1.0,
                                'product_uom': auto_id.product_id.uom_po_id.id,
                                'maintenance_id': self.id
                            })]
            })
        action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        action['context'] = context
        return action

    @api.multi
    def action_view_po(self):
        po_ids = self.mapped('po_line_ids').mapped('order_id')
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        if len(po_ids) > 1:
            action['domain'] = [('id', 'in', po_ids.ids)]
        elif len(po_ids) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = po_ids.ids[0]
        else:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        return action
