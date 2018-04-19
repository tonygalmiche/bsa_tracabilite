# -*- coding: utf-8 -*-

import time
import datetime

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc 
    
class is_generate_livraison(osv.osv_memory):
    _name = 'is.generate.livraison'
    _description = u"Générer livraison"
    
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Commande Client', required=True),
        'etiquette_livraison_ids': fields.many2many('is.tracabilite.livraison', 'is_livraison_etiquette_livraison_rel', 'livraison_id', 'etiquette_livraison_id', 'Etiquettes Livraison', copy=False, required=True),
    }
                
    
    def get_picking_id(self, cr, uid, pick_ids, context=None):
        if pick_ids:
            return max(pick_ids)
        else:
            return False       
           
    def get_products_from_move_lines(self, cr, uid, picking, context=None):
        products = []
        if picking.move_lines:
            for move in picking.move_lines:
                if move.product_id.id in products:
                    continue
                else:
                    products.append(move.product_id.id)
        return products
    
    
    def verifier_product_etiquette(self, cr, uid, etiquettes, products, context=None):
        if etiquettes:
            for etiquette in etiquettes:
                if etiquette.production_id.product_id.id in products:
                    continue
                else:
                    return False
        return True
    
    
    def confirmer_picking(self, cr, uid, picking_id, context=None):
        picking_obj = self.pool.get('stock.picking')
        picking = picking_obj.browse(cr, uid, picking_id, context=context)
        if picking.state == 'draft':
            picking_obj.action_confirm(cr, uid, [picking_id], context=context)
        picking_obj.action_assign(cr, uid, [picking_id], context=context)
        picking.force_assign(cr, uid, [picking_id], context=context)
        return True
            
    
    def etiquette_in_list(self, cr, uid, list, product_id, context=None):
        for item in list:
            if item['product_id'] == product_id:
                return item
            else:
                continue
        return False
    
    def grouper_etiquettes_product(self, cr, uid, etiquettes, context=None):
        lst = []
        for etiquette in etiquettes:
            if not lst:
                lst.append({'product_id': etiquette.production_id.product_id.id, 'qty':etiquette.quantity})
            else:
                item = self.etiquette_in_list(cr, uid, lst, etiquette.production_id.product_id.id, context)
                if item:
                    item['qty'] += etiquette.quantity
                else:
                    lst.append({'product_id': etiquette.production_id.product_id.id, 'qty':etiquette.quantity})
        return lst
            
            
    def existe_etiquette(self, cr, uid, etiquettes, product_id, context=None):
        lst = self.grouper_etiquettes_product(cr, uid, etiquettes, context)
        for item in lst:
            if item['product_id'] == product_id:
                return item['qty']
            else:
                continue
        return False
    
    
    def livrer_produits(self, cr, uid, picking, etiquettes, context=None):
        wiz_obj = self.pool.get('stock.transfer_details')
        
        """ préparer le contenu de wizard de transfer de stock """
        items = []
        packs = []
        if not picking.pack_operation_ids:
            print 'not pack_operation_ids *****************'
            picking.do_prepare_partial()
        for op in picking.pack_operation_ids:
            print 'existe ***********'
            etiquette_qty = self.existe_etiquette(cr, uid, etiquettes, op.product_id.id, context)
            if etiquette_qty: 
                item = {
                    'packop_id': op.id,
                    'product_id': op.product_id.id,
                    'product_uom_id': op.product_uom_id.id,
                    'quantity': etiquette_qty,
                    'package_id': op.package_id.id,
                    'lot_id': op.lot_id.id,
                    'sourceloc_id': op.location_id.id,
                    'destinationloc_id': op.location_dest_id.id,
                    'result_package_id': op.result_package_id.id,
                    'date': op.date, 
                    'owner_id': op.owner_id.id,
                }
                if op.product_id:
                    items.append([0, False, item])
                elif op.package_id:
                    packs.append([0, False, item])
        print 'items *******', items
        print 'packs *******', packs        
        vals = {'picking_id': picking.id,
                'item_ids': items,
                'packop_ids': packs}
        wizard = wiz_obj.create(cr, uid, vals, context=context)
        print 'wizard ********', wizard
        return wiz_obj.do_detailed_transfer(cr, uid, [wizard], context=context)
    
    
    def lier_etiquettes_mouvement(self, cr, uid, picking, etiquette, context=None):
        etiquette_obj = self.pool.get('is.tracabilite.livraison')
        if picking.move_lines:
            for move in picking.move_lines:
                if move.product_id.id == etiquette.production_id.product_id.id:
                    etiquette_obj.write(cr, uid, etiquette.id, {'move_id':move.id}, context=context)
                else:
                    continue
        return True
                    
                
    def generate_livraison(self, cr, uid, ids, context=None):
        etiquette_obj = self.pool.get('is.tracabilite.livraison')
        picking_obj = self.pool.get('stock.picking')
        sale_obj = self.pool.get('sale.order')
        data = self.browse(cr, uid , ids[0], context=context)
        
        picking = self.get_picking_id(cr, uid, data.sale_id.picking_ids, context)
        print 'picking_ids ********', data.sale_id.picking_ids[0]
        print 'picking_id *********', picking
        if picking and data.etiquette_livraison_ids:
            picking_obj.action_assign(cr, uid, [picking.id], context=context)
            picking_obj.force_assign(cr, uid, [picking.id], context=context)
            products = self.get_products_from_move_lines(cr, uid, picking, context)
            print 'products *******', products
            if self.verifier_product_etiquette(cr, uid, data.etiquette_livraison_ids, products, context):
                print 'etiquettes ********', data.etiquette_livraison_ids
                self.livrer_produits(cr, uid, picking, data.etiquette_livraison_ids, context)
                for etiquette in data.etiquette_livraison_ids:
                    self.lier_etiquettes_mouvement(cr, uid, picking, etiquette, context)
                    etiquette_obj.write(cr, uid, etiquette.id, {'sale_id': data.sale_id.id})
                etiquette_ids = [etiquette.id for etiquette in data.etiquette_livraison_ids]
                picking_obj.write(cr, uid, picking.id, {'etiquette_livraison_ids': [(6, 0, etiquette_ids)]})
                return sale_obj.action_view_delivery(cr, uid, [data.sale_id.id], context=context)
            else:
                raise osv.except_osv(_("Avertissement"), _("Les etiquettes sélectionnées ne correspondent pas aux produits de Bon de commande choisi, Veuillez vérifier votre saisie!"))
                
        

    def test(self, cr, uid, sale_id, context=None):
        sale_obj      = self.pool.get('sale.order')
        picking_obj   = self.pool.get('stock.picking')
        etiquette_obj = self.pool.get('is.tracabilite.livraison')

        sale = sale_obj.browse(cr, uid , sale_id, context=context)

        picking = self.get_picking_id(cr, uid, sale.picking_ids, context)

        print "picking="+str(picking)

        #if picking and data.etiquette_livraison_ids:
        if picking:
            picking_obj.action_assign(cr, uid, [picking.id], context=context)
            picking_obj.force_assign(cr, uid, [picking.id], context=context)
            products = self.get_products_from_move_lines(cr, uid, picking, context)
            print 'products *******', products

            ids=[77,78]
            etiquettes=[]
            for id in ids:
                etiquette = etiquette_obj.browse(cr, uid , id, context=context)
                etiquettes.append(etiquette)


            if self.verifier_product_etiquette(cr, uid, etiquettes, products, context):
                print etiquettes
                self.livrer_produits(cr, uid, picking, etiquettes, context)
                for etiquette in etiquettes:
                    self.lier_etiquettes_mouvement(cr, uid, picking, etiquette, context)
                    etiquette_obj.write(cr, uid, etiquette.id, {'sale_id': sale_id})
                etiquette_ids = [etiquette.id for etiquette in etiquettes]
                picking_obj.write(cr, uid, picking.id, {'etiquette_livraison_ids': [(6, 0, etiquette_ids)]})
                #sale_obj.action_view_delivery(cr, uid, [sale_id], context=context)
                #print r
            else:
                raise osv.except_osv(_("Avertissement"), _("Les etiquettes sélectionnées ne correspondent pas aux produits de Bon de commande choisi, Veuillez vérifier votre saisie!"))





        #picking = self.get_picking_id(cr, uid, data.sale_id.picking_ids, context)


        return "ok\n"




         
    
                    
