from odoo import models, fields, api, _
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    route_id = fields.Many2many(
        'mrp.routing', 'mrp_bom_route_id_rel', string='Routing',
        help="The operations for producing this BoM.  When a routing is specified, the production orders will "
             " be executed through work orders, otherwise everything is processed in the production order itself. ")

    sub_route_id = fields.Many2one('mrp.routing', string="Route for Sub-MO",
                                   help="The operations for producing this BoM in Sub MO.  When a routing is specified, the production orders will "
                                        " be executed through work orders in case of Sub MO, otherwise everything is processed in the production order itself. ")

    operation_ids = fields.Many2many(
        'mrp.routing.workcenter', 'mrp_bom_workcenter_id_rel', string='Consumed in Operations',
        help="The operations for producing this BoM.  When a routing is specified, the production orders will "
             " be executed through work orders, otherwise everything is processed in the production order itself. ")

    @api.onchange('route_id')
    def onchange_routing_id(self):
        print(":eds")
        data = []
        for route in self.route_id:
            data += route.operation_ids.ids

        self.operation_ids = [(6, 0, data)]


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    routing_id = fields.Many2one(
        'mrp.routing', related=False, string='Routing',
        help="The operations for producing this BoM.  When a routing is specified, the production orders will "
             " be executed through work orders, otherwise everything is processed in the production order itself. ")

    operation_ids = fields.Many2many(
        'mrp.routing.workcenter', 'mrp_bom_line_workcenter_id_rel', string='Consumed in Operations',
        help="The operations for producing this BoM.  When a routing is specified, the production orders will "
             " be executed through work orders, otherwise everything is processed in the production order itself. ")

    @api.onchange('operation_ids')
    def onchange_operation(self):
        if self.operation_ids:
            res = []
            for data in self.operation_ids:
                if data.routing_id.id in res:
                    raise UserError(_("You can not select multiple operations of same route"))
                res.append(data.routing_id.id)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    route_id = fields.Many2one('mrp.routing', string='Routing')

    @api.multi
    @api.depends('route_id', 'route_id.operation_ids')
    def _compute_routing(self):
        for production in self:
            if production.route_id.operation_ids:
                production.routing_id = production.route_id.id
                production.bom_id.routing_id = production.route_id.id
            else:
                production.routing_id = False

    @api.onchange('route_id')
    def onchange_route_id(self):
        if self.bom_id:
            self.bom_id.write({'routing_id': self.route_id.id})
            for data in self.bom_id.bom_line_ids:
                operation = data.operation_ids.filtered(lambda x: x.routing_id.id == self.route_id.id)
                data.write({'operation_id': operation.id})
        self.routing_id = self.route_id.id

    @api.onchange('bom_id')
    def _onchange_bom(self):

        if self.bom_id:
            domain = {'route_id': [('id', 'in', self.bom_id.route_id.ids)]}
            return {'domain': domain}

    # def _generate_raw_moves(self, exploded_lines):
    #     self.ensure_one()
    #     moves = self.env['stock.move']
    #     for bom_line, line_data in exploded_lines:
    #         if self.route_id and self.route_id == bom_line.routing_id:
    #             moves += self._generate_raw_move(bom_line, line_data)
    #         if not self.route_id:
    #             moves += self._generate_raw_move(bom_line, line_data)
    #     return moves

    @api.model
    def create(self, values):
        if not values.get('route_id'):
            bom = self.env['mrp.bom'].browse(int(values['bom_id']))
            if bom.sub_route_id:
                values['route_id'] = bom.sub_route_id.id
                values['routing_id'] = bom.sub_route_id.id
                bom.write({'routing_id': bom.sub_route_id.id})

            else:
                print(bom.route_id)
                if bom.route_id:
                    values['route_id'] = self.env['mrp.routing'].browse(bom.route_id.ids[0]).id
                    values['routing_id'] = self.env['mrp.routing'].browse(bom.route_id.ids[0]).id
                    bom.write({'routing_id': self.env['mrp.routing'].browse(bom.route_id.ids[0]).id})
        if values.get('origin'):
            parent_mo = self.env['mrp.production'].search([('name', '=', str(values.get('origin')))])
            if parent_mo:
                if 'x_studio_client' in self.env['mrp.production']._fields:
                    values['x_studio_client'] = parent_mo.x_studio_client
                if 'x_studio_po' in self.env['mrp.production']._fields:
                    values['x_studio_po'] = parent_mo.x_studio_po
        return super(MrpProduction, self).create(values)


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    @api.multi
    def name_get(self):
        result = []
        res = []

        for data in self:
            name = data.name + '(' + data.routing_id.name + ')'
            result.append((data.id, name))
            res.append((data.id, data.name))

        if self._context.get('special_display_name', False):
            return result
        else:
            return res