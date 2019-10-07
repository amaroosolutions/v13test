# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta, datetime
from odoo.exceptions import Warning, ValidationError


class JobNumber(models.Model):
    _name = 'job.number'
    _description = "Job Number"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search(
            [('company_id', '=', company)], limit=1)
        return warehouse_ids

    @api.depends('inspector_name_id', 'cleaners_name_id', 'checker', 'accessories_sign_off', 'dispatcher_name_id', 'total_hours', 'job_card_billing')
    def _compute_button_visible(self):
        if self.inspector_name_id and self.cleaners_name_id and self.checker and self.accessories_sign_off and self.dispatcher_name_id and self.total_hours > 0.0 and self.job_card_billing:
            self.show_completed = True
        # if not self.total_hours > 0.0

    @api.multi
    def create_sale_order_lines(self):
        """This method is used for order line for that sale order """
        if not self.company_id.product_id:
            raise Warning("Please configure the product inside the Company")

        if self.job_card_billing == 'total_hours':
            quantity = self.total_hours
        else:
            quantity = self.hours_wh
        sale_order_rec = False
        if not self.sale_order_id:
            sale_obj = self.env['sale.order']
            order_vals = sale_obj.new({
                'job_number_id': self.id,
                'partner_id': self.serial_id.partner_id.id,
                'company_id': self.env.user.company_id.id,
            })
            order_vals.onchange_partner_id()
            sale_order_rec = order_vals._convert_to_write(
                {name: order_vals[name] for name in order_vals._cache})
            order_rec = self.env['sale.order'].create(sale_order_rec)
            self.sale_order_id = order_rec.id
            sale_order_rec = order_rec
        else:
            sale_order_rec = self.sale_order_id

        sale_order_line_vals = self.env['sale.order.line'].new({
            'product_id': self.company_id.product_id.id,
            'product_uom_qty': quantity,
            'order_id': sale_order_rec.id,
        })
        sale_order_line_vals.product_id_change()
        sale_order_line_vals.product_uom_change()
        sale_order_line_vals_updated = sale_order_line_vals._convert_to_write(
            {name: sale_order_line_vals[name] for name in sale_order_line_vals._cache})
        sale_order_line_rec = self.env['sale.order.line'].create(
            sale_order_line_vals_updated)

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state_progress.selection]

    @api.depends('delay_reason_line_ids.day_waiting')
    def _total_day_waiting_all(self):
        """
        Compute the total waiting day of the dealy reason.
        """
        for delay in self:
            delay.total_waiting_day = sum(
                delay.delay_reason_line_ids.mapped('day_waiting'))

    @api.multi
    def button_set_job_complete(self):
        for rec in self:
            rec.write({'state': 'done'})
            rec.write({'state_progress': 'complete'})
        self.create_sale_order_lines()

    name = fields.Char(string='Job Number', default='New')
    date_of_receipt = fields.Date(default=date.today())
    employee_id = fields.Many2one(
        'hr.employee', string='Booked In By', track_visibility='onchange')
    other_ref_1 = fields.Char(string='Other Ref 1')
    other_ref_2 = fields.Char(string='Other Ref 2')
    nxstage_case_no = fields.Char(string='Nxstage Case No')
    serial_id = fields.Many2one(
        'serial.number', string='Serial Number', track_visibility='onchange')
    model_id = fields.Many2one(
        'device.model', string='Model', related='serial_id.model_id', store=True)
    model_type = fields.Char(
        string='Model Type', related='serial_id.description', store=True)
    partner_id = fields.Many2one(
        'res.partner', string='OEM', related='serial_id.partner_id', store=True)
    reason_id = fields.Many2one('reason.return', string='Reason for Return')
    service_sheet = fields.Binary(string='Service Sheet')
    further_details = fields.Text(string='Further Details')
    inspector_name_id = fields.Many2one(
        'res.users', string='Inspector Name', track_visibility='onchange')
    date_goods_in_inspection = fields.Date(
        string='Date Of Inspection', track_visibility='onchange')
    time = fields.Float(string='Time Taken For Inspection',
                        track_visibility='onchange')
    comments = fields.Text(string='Comments')
    cleaners_name_id = fields.Many2one(
        'res.users', string='Cleaners Name', track_visibility='onchange')
    date_of_cleaning = fields.Date(
        string='Date Of Cleaning', track_visibility='onchange')
    time_taken = fields.Float(string='Time Taken', track_visibility='onchange')
    device_clean_and_free_from_visible_damage_ = fields.Boolean(
        string="Device Clean And Free from visible Damage")
    all_required_accessories_paperwork_present = fields.Boolean(
        string="All Required Accessories & Paperwork Present")
    correct_device_serial_number_on_service_sheet = fields.Boolean(
        string="Correct Device Serial Number On Service Sheet")
    engineer_name_date_on_service_sheet = fields.Boolean(
        string="Engineer Name & Date on Service Sheet")
    ifs_quality_assurance = fields.Boolean(string="IFS Quality Assurance")
    checker = fields.Many2one(
        'res.users', string='Checker', track_visibility='onchange')
    checker_2 = fields.Many2one(
        'res.users', string='Checker 2', track_visibility='onchange')
    date = fields.Date(string='Date', track_visibility='onchange')
    qc_time_taken = fields.Float(
        string='QC Time Taken', track_visibility='onchange')
    accessories_sign_off = fields.Many2one(
        'res.users', string='Accessories Sign Off', track_visibility='onchange')
    accessories_ids = fields.One2many(
        'accessories.line', 'job_number_id', string='Accessories')
    dispatcher_name_id = fields.Many2one(
        'res.users', string='Dispatcher Name', track_visibility='onchange')
    dispatch_date = fields.Date(
        string='Dispatch Date', track_visibility='onchange')
    time_taken_to_pack = fields.Float(
        string='Time Taken To Pack', track_visibility='onchange')
    rohs_device = fields.Selection(
        [('Yes', 'Yes'), ('No', 'No')], string='ROHS Device')
    out_of_box_falure = fields.Selection(
        [('Yes', 'Yes'), ('No', 'No')], string='Out Of Box Falure')
    reason_for_return_id = fields.Many2one(
        'reason.return', string='Reason for Return For Pre-Flight')
    swap_summery = fields.Text(string='SWAP Summery')
    alleged_fault_code = fields.Char(string='Alleged Fault Code')
    actual_fault_code = fields.Char(string='Actual Fault Code')
    alleged_quality_code = fields.Char(string='Alleged Quality Code')
    actual_quality_code = fields.Char(string='Actual Quality Code')
    return_reason_upheld = fields.Selection(
        [('Yes', 'Yes'), ('No', 'No')], string='Return Reason Upheld')
    supporting_details = fields.Text(string='Supporting Details')
    date_2 = fields.Date(string='Date For Return Reason ')
    additional_testing = fields.Text(string='Additional Testing')
    date_3 = fields.Date(string='Date For Testing')
    name_id = fields.Many2one('res.users', string='Name')
    engineer_id = fields.Many2one(
        'res.users', string='Engineer', track_visibility='onchange')
    date_1 = fields.Date(string='Date For Testing Complete',
                         track_visibility='onchange')
    result = fields.Selection(
        [('Pass', 'Pass'), ('Fail', 'Fail')], string='Result')
    return_reason_upheld = fields.Selection(
        [('Yes', 'Yes'), ('No', 'No')], string='Return Reason Upheld')
    supporting_details = fields.Text(string='Supporting Details')
    hours = fields.Float(string='Workshop Hours')
    hours_wh = fields.Float(
        string='Warehouse Hours', compute='compute_warehouse_hours', store=True)
    planned_hours = fields.Float(string='Planned Hours')
    total_hours = fields.Float(
        string='Total Hours', compute='compute_actual_hour', store=True)
    total_no_days = fields.Integer(
        string='Total No Days', compute='_compute_total_days', store=True)
    actual_days = fields.Integer(
        string='Actual Days', compute='_compute_actual_days', store=True)
    parts_required_ids = fields.Many2many(
        'parts.required', string='Parts Required')
    previous_jobs_id = fields.Many2one('job.number', string='Previous Jobs')
    philips_parts_line_ids = fields.One2many(
        'philips.parts.line', 'job_number_id', string='Parts Added Into Device#')
    oem_parts_line_ids = fields.One2many(
        'oem.parts.line', 'job_number_id', string='Parts Added Into Device*')
    delay_reason_line_ids = fields.One2many(
        'delay.reason.line', 'job_number_id', string='Delay Reason')
    is_nxstage_device = fields.Boolean(
        string='Is Nxstage Device', related='model_id.is_nxstage_device', store=True)
    is_philips_device = fields.Boolean(
        string='Is Philips Device', related='model_id.is_philips_device', store=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', default=_default_warehouse_id)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    sale_order_count = fields.Integer(
        string='Sale order',  compute='compute_sale_order')
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.user.company_id)
    state = fields.Selection(
        [('progress', 'WIP'), ('done', 'COMPLETED')], default='progress')
    state_progress = fields.Selection([('goods in inspection', 'GOODS IN'), ('decontamination', 'DECON'), ('qc checks', 'QC CHECKS'), (
        'pre-flight', 'PRE FLIGHT'), ('workshop', 'WORKSHOP'), ('dispatch', 'Dispatch'), ('complete', 'COMPLETED')], default='goods in inspection', track_visibility='onchange', group_expand='_expand_states',)
    job_card_billing = fields.Selection([('total_hours', 'Total Hours'),
                                         ('workshop_hours', 'Workshop Hours'),
                                         ], string='Job Card Billing')
    show_completed = fields.Boolean(
        string='Show Completed', compute='_compute_button_visible')
    total_waiting_day = fields.Integer(
        string='Total Day Waiting', store=True, readonly=True, compute='_total_day_waiting_all')
    _sql_constraints = [
          ('dispatch_date_greater', 'check(dispatch_date >= date_of_receipt)', 'Error!  Date of Receipt must be lower than Dispatch Date.')
        ]

    @api.depends('dispatch_date', 'date_of_receipt')
    def _compute_total_days(self):
        if self.dispatch_date:
            for job_rec in self:
                dispatch_date = fields.Date.from_string(job_rec.dispatch_date)
                date_of_receipt = fields.Date.from_string(job_rec.date_of_receipt)
                # if dispatch_date and date_of_receipt:
                    # Working Days
                working_days_list = []
                waiting_day_count = 0
                working_days_list = job_rec.company_id.resource_calendar_id.attendance_ids.mapped(
                    'dayofweek')
                working_days_list = list(map(int, working_days_list))
                list_day_set = set(working_days_list)
                working_days = list(list_day_set)

                # Days logic
                total_days = (dispatch_date - date_of_receipt).days+1
                for datedelay in range(total_days):
                    current_date = (date_of_receipt +
                                    timedelta(days=datedelay))
                    global_leaves = self.env['resource.calendar.leaves'].search_count(
                        [('date_from', '<=', current_date), ('date_to', '>=', current_date)])
                    if not global_leaves and current_date.weekday() in working_days:
                        waiting_day_count += 1
                job_rec.total_no_days = waiting_day_count

    @api.depends('total_no_days', 'delay_reason_line_ids.start_date', 'delay_reason_line_ids.end_date')
    def _compute_actual_days(self):
        for job_rec in self:
            job_rec.actual_days = job_rec.total_no_days - \
                sum(job_rec.delay_reason_line_ids.mapped('day_waiting'))

    @api.onchange('partner_id')
    def hour_job_billing(self):
        self.job_card_billing = self.partner_id.job_card_billing

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'job.number') or _('New')
        return super(JobNumber, self).create(vals)

    @api.depends('time', 'time_taken', 'qc_time_taken', 'time_taken_to_pack')
    def compute_warehouse_hours(self):
        for compute_time in self:
            compute_time.hours_wh = compute_time.time+compute_time.time_taken + \
                compute_time.qc_time_taken+compute_time.qc_time_taken

    @api.depends('hours', 'hours_wh')
    def compute_actual_hour(self):
        for compute_hours in self:
            compute_hours.total_hours = compute_hours.hours + compute_hours.hours_wh

    @api.multi
    def compute_sale_order(self):
        for sale_order_rec in self:
            sale_order_count = self.env['sale.order'].search_count(
                [('job_number_id', '=', sale_order_rec.id)])
            sale_order_rec.sale_order_count = sale_order_count


class AccessoriesLine(models.Model):
    _name = 'accessories.line'
    _description = "Accessories Line"

    accessories_id = fields.Many2one(
        'accessories.accessories', string='Product', required=True)
    quantity = fields.Float("Quantity")
    job_number_id = fields.Many2one('job.number', 'Job Number')
    received = fields.Boolean("Received", default=True)
    returned = fields.Boolean("Returned")
    comments = fields.Char("Comments")
