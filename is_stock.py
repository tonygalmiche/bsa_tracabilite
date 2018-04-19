# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
#===============================================================================
#     def _get_default_code_picking(self, cr, uid, context=None):
#         """ Gives default code picking by checking if present in the context """
#         code = self._resolve_type_id_from_context(cr, uid, context=context) or False
#         if code:
#             code = self.pool.get('stock.picking.type').browse(cr, uid, code, context).code or False
#             return code
#         return None
# 
#     
#     def _resolve_type_id_from_context(self, cr, uid, context=None):
#         if context is None:
#             context = {}
#         if type(context.get('default_picking_type_id')) in (int, long):
#             return context.get('default_picking_type_id')
#         if isinstance(context.get('default_picking_type_id'), basestring):
#             type_ids = self.pool.get('stock.picking.type').name_search(cr, uid, name=context['default_picking_type_id'], context=context)
#             if len(type_ids) == 1:
#                 return int(type_ids[0][0])
#         return None
#===============================================================================
    
    _columns = {
        #'is_picking_type_code': fields.char(u'Code opération'),
        'etiquette_reception_ids': fields.many2many('is.tracabilite.reception', 'stock_picking_tacabilite_reception_rel', 'picking_id', 'etiquette_id', 'Etiquettes', readonly=True, copy=False),
        'etiquette_livraison_ids': fields.many2many('is.tracabilite.livraison', 'stock_picking_tacabilite_livraison_rel', 'picking_id', 'etiquette_id', 'Etiquettes', readonly=True, copy=False),
    }
    
    #===========================================================================
    # _defaults = {
    #     'is_picking_type_code': _get_default_code_picking,
    # }
    #===========================================================================
    
            
        