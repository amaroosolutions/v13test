from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError
from odoo.tools import float_compare


class OemPartsLine(models.Model):
    _name = 'oem.parts.line'
    _description = 'These model is used for store the partner`s part'

    job_number_id = fields.Many2one('job.number', string='Job Number')
    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    description = fields.Char(string='Description')
    quantity = fields.Float("Quantity")
    date = fields.Date(string='Date', default=date.today())
    user_id = fields.Many2one(
        'res.users', string='User', default=lambda self: self.env.user)
    delivered_qty = fields.Float(string="Delivered Qty", copy=False,
                                 default=0.0)
    sale_line_id = fields.Many2one('sale.order.line', string="Order Line")

    def create_sale_order(self, line_rec):
        """This method is used for create the sale order"""
        sale_obj = self.env['sale.order']
        order_vals = sale_obj.new({
            'job_number_id': line_rec.job_number_id.id,
            'partner_id': line_rec.job_number_id.serial_id.partner_id.id,
            'company_id': line_rec.env.user.company_id.id,
        })
        order_vals.onchange_partner_id()
        sale_order_rec = order_vals._convert_to_write(
            {name: order_vals[name] for name in order_vals._cache})
        order_rec = self.env['sale.order'].create(sale_order_rec)
        line_rec.job_number_id.sale_order_id = order_rec.id

    @api.multi
    def create_sale_order_lines(self, line_rec=False):
        """This method is used for order line for that sale order """
        if line_rec:
            for line in line_rec:
                if not line.sale_line_id:
                    sale_order_line_vals = self.env['sale.order.line'].new({
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.quantity,
                        'order_id': line.job_number_id.sale_order_id.id,
                    })
                    sale_order_line_vals.product_id_change()
                    sale_order_line_vals.product_uom_change()
                    sale_order_line_vals_updated = sale_order_line_vals._convert_to_write(
                        {name: sale_order_line_vals[name] for name in sale_order_line_vals._cache})
                    sale_order_line_vals_updated.update({
                        'price_unit': 0,
                        'part_line_id': line_rec.id
                    })
                    sale_order_line_rec = self.env['sale.order.line'].create(
                        sale_order_line_vals_updated)
                    line.sale_line_id = sale_order_line_rec.id
        else:
            self.sale_line_id.write({'product_uom_qty': self.quantity})

    @api.multi
    def unlink(self):
        if self.filtered(lambda line: self.job_number_id.sale_order_id.state in ('sale', 'done')):
            raise UserError(
                _('You can not remove an order line once the sales order is confirmed.\nYou should rather set the quantity to 0.'))
        return super(OemPartsLine, self).unlink()

    @api.onchange('quantity')
    def _onchange_quantity(self):
        # When modifying a one2many, _origin doesn't guarantee that its values will be the ones
        # in database. Hence, we need to explicitly read them from there.
        if self._origin:
            quantity_origin = self._origin.read(["quantity"])[0]["quantity"]
        else:
            quantity_origin = 0
        if self._origin.sale_line_id.state == 'sale' and self.product_id.type in ['product', 'consu'] and self.quantity < quantity_origin:

            # Do not display this warning if the new quantity is below the delivered
            # one; the `write` will raise an `UserError` anyway.
            if self.quantity > quantity_origin:
                return {}
            warning_mess = {
                'title': _('Ordered quantity decreased!'),
                'message': _('You are decreasing the ordered quantity! Do not forget to manually update the delivery order if needed.'),
            }
            return {'warning': warning_mess}
        return {}

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.description_sale or self.product_id.name

    @api.model
    def create(self, vals):
        line_rec = super(OemPartsLine, self).create(vals)
        if not line_rec.job_number_id.sale_order_id:
            self.create_sale_order(line_rec)
        self.create_sale_order_lines(line_rec)
        # call the action_confirm method to confirm the quotation
        line_rec.sale_line_id.order_id.action_confirm()
        return line_rec

    @api.multi
    def write(self, vals):
        status = super(OemPartsLine, self).write(vals)
        if 'quantity' in vals:
            self.create_sale_order_lines()
        return status
