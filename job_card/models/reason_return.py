from odoo import models, fields


class ReasonReturn(models.Model):
    _name = 'reason.return'
    _description = "Return Reason"

    name = fields.Char("Name", required=True)
