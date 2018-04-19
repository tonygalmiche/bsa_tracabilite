# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _

class product_product(osv.osv):
    _inherit = 'product.template'
    
    _columns = {
        'is_trace_reception': fields.boolean(u'Traçabilité en réception'),
        'is_gestion_lot': fields.boolean(u'Gestion par lots'),
    }

    _defaults = {
        'is_gestion_lot': False,
    }

