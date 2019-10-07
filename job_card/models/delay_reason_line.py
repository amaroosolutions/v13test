# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError


class DelayReasonLine(models.Model):
    _name = 'delay.reason.line'
    _description = 'These model is used for detail of delay for any reason'

    job_number_id = fields.Many2one('job.number', string='Job Number')
    dealy_reason_id = fields.Many2one(
        'delay.reason', string='Reason For Delay', required=True)
    start_date = fields.Date(string='Start Date', default=date.today())
    end_date = fields.Date(string='End Date')
    day_waiting = fields.Integer(
        string='Day`s Waiting', compute='_compute_waiting_day', store=True)
    comments = fields.Char(string='Comments')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    _sql_constraints = [
          ('end_date_greater', 'check(end_date >= start_date)', 'Error!  The start date of the delay must be earlier than end date.')
        ]
    
   
    @api.depends('start_date', 'end_date')
    def _compute_waiting_day(self):
        for reason_rec in self:
            if reason_rec.end_date and reason_rec.start_date:
                working_days_list = []
                waiting_day_count = 0
                working_days_list = reason_rec.job_number_id.company_id.resource_calendar_id.attendance_ids.mapped(
                    'dayofweek')
                working_days_list = list(map(int, working_days_list))
                list_day = set(working_days_list)
                working_days = list(list_day)
                total_days = (reason_rec.end_date-reason_rec.start_date).days+1
                for datedelay in range(total_days):
                    current_date = (reason_rec.start_date +
                                    timedelta(days=datedelay))
                    global_leaves = self.env['resource.calendar.leaves'].search_count(
                        [('date_from', '<=', current_date), ('date_to', '>=', current_date)])
                    if not global_leaves and current_date.weekday() in working_days:
                        waiting_day_count += 1
                reason_rec.day_waiting = waiting_day_count
