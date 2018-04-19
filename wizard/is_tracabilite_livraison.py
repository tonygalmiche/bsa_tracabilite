# -*- coding: utf-8 -*-

import time
import datetime

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc 
import os
#import is_bsa_lib


##TODO : J'ai doupliqué cette fonction, mais il serait plus propre de créer un module
#def imprimer_etiquette(cr, uid, etiquettes):
#    #print etiquettes
#    etiquettes=unicode(etiquettes,'utf-8')
#    #print etiquettes
#    etiquettes=etiquettes.encode("windows-1252")
#    #print etiquettes
#    path="/tmp/etiquette.txt"
#    err=""
#    try:
#        fichier = open(path, "w")
#    except IOError, e:
#        err="Problème d'accès au fichier '"+path+"' => "+ str(e)
#    if err=="":
#        fichier.write(etiquettes)
#        fichier.close()
#        cmd="lpr -h -PDatamax "+path
#        os.system(cmd)
#    return



    
class is_imprimer_etiquette_mrp(osv.osv_memory):
    _name = 'is.imprimer.etiquette.mrp'
    _description = u"Imprimer Etiquette livraison"
    
    
    def create_etiquette_livraison(self, cr, uid, production_order, context=None):
        tracab_obj = self.pool.get('is.tracabilite.livraison')
        res = []
        
        etiquettes=""
        if production_order.product_qty:
            qty = production_order.product_qty
            lot=1
            if production_order.product_id.is_gestion_lot:
                lot=qty
            while ( qty >= 1):
                vals = {
                    'production_id': production_order.id,
                    'quantity': 1.0,
                    'lot_fabrication': lot,
                }
                new_id = tracab_obj.create(cr, uid, vals, context=context)
                res.append(new_id)
                qty = qty - lot
                etiquettes=etiquettes+tracab_obj.generer_etiquette_livraison(cr, uid, [new_id], context=context)
        #imprimer_etiquette(cr, uid,etiquettes)
        self.pool.get('is.tracabilite.reception').imprimer_etiquette(cr, uid, etiquettes)

        return res

    
    def imprimer_etiquette_livraison(self, cr, uid, ids, context=None):
        production_obj = self.pool.get('mrp.production')
        
        production = production_obj.browse(cr, uid, context.get(('active_ids'), []), context=context)
        data = self.browse(cr, uid , ids[0], context=context)
        
        """ Créer Etiquettes en livraison """
        etiquettes = self.create_etiquette_livraison(cr, uid, production, context)
        print 'etiquettes ******', etiquettes

        vals={
            'generer_etiquette': True,
            'is_gestion_lot': production.product_id.is_gestion_lot,
        }


        production_obj.write(cr, uid, production.id,vals, context=context)
        return True
                    
