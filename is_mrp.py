# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    
    _columns = {
        'generer_etiquette': fields.boolean('Etiquettes générées'),
        'etiquette_ids': fields.many2many('is.tracabilite.livraison', 'mrp_production_tacabilite_livraison_rel', 'production_id', 'etiquette_id', 'Etiquettes', readonly=True, copy=False),
        'is_gestion_lot': fields.boolean(u'Gestion par lots'),
    }
    
    _defaults = {
        'generer_etiquette': False,
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update(generer_etiquette=False)
        return super(mrp_production, self).copy(cr, uid, id, default, context)
    
    
    def get_consume_lines(self, cr, uid, production_id, product_qty, context=None):
        prod_obj = self.pool.get("mrp.production")
        uom_obj = self.pool.get("product.uom")
        production = prod_obj.browse(cr, uid, production_id, context=context)
        consume_lines = []
        new_consume_lines = []
        if product_qty > 0.0:
            product_uom_qty = uom_obj._compute_qty(cr, uid, production.product_uom.id, product_qty, production.product_id.uom_id.id)
            consume_lines = prod_obj._calculate_qty(cr, uid, production, product_qty=product_uom_qty, context=context)
        
        for consume in consume_lines:
            new_consume_lines.append([0, False, consume])
        return new_consume_lines
    
    
    def get_track(self, cr, uid, product_id, context=None):
        prod_obj = self.pool.get("product.product")
        return product_id and prod_obj.browse(cr, uid, product_id, context=context).track_production or False
    
    
    def get_wizard(self, cr, uid, production, context=None):
        wiz_obj = self.pool.get('mrp.product.produce')
        
        vals = {
            'product_id': production.product_id.id,
            'product_qty': 1.0,
            'mode': 'consume_produce',
            'lot_id': False,
            'consume_lines': self.get_consume_lines(cr, uid, production.id, 1.0, context),
            'track_production': self.get_track(cr, uid, production.product_id.id, context)
        }
        new_id = wiz_obj.create(cr, uid, vals, context=context)
        wiz = wiz_obj.browse(cr, uid, new_id, context=context)
        return wiz
    
    def is_act_mrp_declarer_produit(self, cr, uid, ids, context=None):
        print str(ids)


        production = self.browse(cr, uid, ids[0], context=context)
        if production.state == 'confirmed':
            self.force_production(cr, uid, ids, {})
        
        wiz = self.get_wizard(cr, uid, production, context)


        qt=1
        if production.is_gestion_lot:
            qt=production.product_qty

        self.action_produce(cr, uid, ids[0], qt, 'consume_produce', wiz, context=context)
        return {}
    
