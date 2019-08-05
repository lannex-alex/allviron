from odoo import models,fields,api,_

class QualityCheck(models.Model):

    _inherit = 'quality.point'

    operation_id = fields.Many2many('mrp.routing.workcenter')