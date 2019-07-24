from odoo import models,fields,api,_
from odoo.tools import float_compare, float_round




class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    route_id = fields.Many2many(
        'mrp.routing','mrp_bom_route_id_rel', string='Routing',
        help="The operations for producing this BoM.  When a routing is specified, the production orders will "
             " be executed through work orders, otherwise everything is processed in the production order itself. ")

    sub_route_id = fields.Many2one('mrp.routing',string="Route for Sub-MO",help="The operations for producing this BoM in Sub MO.  When a routing is specified, the production orders will "
             " be executed through work orders in case of Sub MO, otherwise everything is processed in the production order itself. ")




class MrpBomLine(models.Model):

    _inherit='mrp.bom.line'

    routing_id = fields.Many2one(
        'mrp.routing', related=False,string='Routing',
        help="The operations for producing this BoM.  When a routing is specified, the production orders will "
             " be executed through work orders, otherwise everything is processed in the production order itself. ")

    @api.onchange('routing_id')
    def onchange_routing_id(self):
        if self.routing_id:
            domain = {'operation_id': [('id', 'in', self.routing_id.operation_ids.ids)]}

            return {'domain': domain}


class MrpProduction(models.Model):

    _inherit='mrp.production'


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
            self.bom_id.write({'routing_id':self.route_id.id})
        print("bom route",self.bom_id.routing_id)
        print("main route",self.route_id)
        self.routing_id = self.route_id.id


    @api.onchange('bom_id')
    def _onchange_bom(self):

        if self.bom_id:
            domain = {'route_id': [('id', 'in', self.bom_id.route_id.ids)]}
            return {'domain':domain}


    def _generate_raw_moves(self, exploded_lines):
        self.ensure_one()
        moves = self.env['stock.move']
        for bom_line, line_data in exploded_lines:
            if self.route_id and self.route_id == bom_line.routing_id:
                moves += self._generate_raw_move(bom_line, line_data)
        return moves

    @api.model
    def create(self, values):
        if not values.get('route_id'):
            bom = self.env['mrp.bom'].browse(int(values['bom_id']))
            if bom.sub_route_id:
                values['route_id'] = bom.sub_route_id.id
                values['routing_id'] = bom.sub_route_id.id
                bom.write({'routing_id': bom.sub_route_id.id})
                
            else:
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
       
        # if not production.routing_id:
        #     if production.bom_id.sub_route_id:
        #         production.routing_id = production.bom_id.sub_route_id.id
        #         production.route_id = production.bom_id.sub_route_id.id
        #     else:
        #         production.routing_id = self.env['mrp.routing'].browse(production.bom_id.route_id.ids[0]).id
        #         production.route_id = self.env['mrp.routing'].browse(production.bom_id.route_id.ids[0]).id
        # return production


    #
    # @api.multi
    # def _generate_workorders(self, exploded_boms):
    #     workorders = self.env['mrp.workorder']
    #     original_one = False
    #     for bom, bom_data in exploded_boms:
    #         # If the routing of the parent BoM and phantom BoM are the same, don't recreate work orders, but use one master routing
    #         if self.routing_id.id and (
    #                 not bom_data['parent_line'] or bom_data['parent_line'].routing_id.id != self.routing_id.id):
    #             temp_workorders = self._workorders_create(bom, bom_data)
    #             workorders += temp_workorders
    #             if temp_workorders:  # In order to avoid two "ending work orders"
    #                 if original_one:
    #                     temp_workorders[-1].next_work_order_id = original_one
    #                 original_one = temp_workorders[0]
    #     return workorders
    #
    #
    # def _workorders_create(self, bom, bom_data):
    #     """
    #     :param bom: in case of recursive boms: we could create work orders for child
    #                 BoMs
    #     """
    #     workorders = self.env['mrp.workorder']
    #     bom_qty = bom_data['qty']
    #     print("creating work order",self.routing_id)
    #     # Initial qty producing
    #     if self.product_id.tracking == 'serial':
    #         quantity = 1.0
    #     else:
    #         quantity = self.product_qty - sum(self.move_finished_ids.mapped('quantity_done'))
    #         quantity = quantity if (quantity > 0) else 0
    #
    #     for operation in self.routing_id.operation_ids:
    #         # create workorder
    #         cycle_number = float_round(bom_qty / operation.workcenter_id.capacity, precision_digits=0, rounding_method='UP')
    #         duration_expected = (operation.workcenter_id.time_start +
    #                              operation.workcenter_id.time_stop +
    #                              cycle_number * operation.time_cycle * 100.0 / operation.workcenter_id.time_efficiency)
    #         workorder = workorders.create({
    #             'name': operation.name,
    #             'production_id': self.id,
    #             'workcenter_id': operation.workcenter_id.id,
    #             'operation_id': operation.id,
    #             'duration_expected': duration_expected,
    #             'state': len(workorders) == 0 and 'ready' or 'pending',
    #             'qty_producing': quantity,
    #             'capacity': operation.workcenter_id.capacity,
    #         })
    #         if workorders:
    #             workorders[-1].next_work_order_id = workorder.id
    #         workorders += workorder
    #
    #         # assign moves; last operation receive all unassigned moves (which case ?)
    #         moves_raw = self.move_raw_ids.filtered(lambda move: move.operation_id == operation)
    #         if len(workorders) == len(bom.routing_id.operation_ids):
    #             moves_raw |= self.move_raw_ids.filtered(lambda move: not move.operation_id)
    #         moves_finished = self.move_finished_ids.filtered(lambda move: move.operation_id == operation) #TODO: code does nothing, unless maybe by_products?
    #         moves_raw.mapped('move_line_ids').write({'workorder_id': workorder.id})
    #         (moves_finished + moves_raw).write({'workorder_id': workorder.id})
    #
    #         workorder._generate_lot_ids()
    #     return workorders