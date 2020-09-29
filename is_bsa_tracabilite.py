# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
import os
#from wizard import is_bsa_lib


# x : Position x à partir de la gauche
# y : Position y à partir du bas (entre 0 et 200)
# sizex : Taille X des caractères (1 à 9)
# sizey : Taille Y des caractères (1 à 9)
def datamax(sizex, sizey, y, x, txt):
    sizex="0"+str(sizex)
    sizex=sizex[-1:]

    sizey="0"+str(sizey)
    sizey=sizey[-1:]

    x="0000"+str(x)
    x=x[-4:]

    y="0000"+str(y)
    y=y[-4:]

    r="10"+sizex+sizey+"000"+y+x+txt+chr(10)
    return r



#class is_tracabilite():
#    _name = 'is.tracabilite'

#    def imprimer_etiquette(self, cr, uid, etiquettes):
#        #print etiquettes
#        etiquettes=unicode(etiquettes,'utf-8')
#        #print etiquettes
#        etiquettes=etiquettes.encode("windows-1252")
#        #print etiquettes
#        path="/tmp/etiquette.txt"
#        err=""
#        try:
#            fichier = open(path, "w")
#        except IOError, e:
#            err="Problème d'accès au fichier '"+path+"' => "+ str(e)
#        if err=="":
#            fichier.write(etiquettes)
#            fichier.close()


#            user       = self.pool['res.users'].browse(cr, uid, [uid])[0]
#            imprimante = user.company_id.is_nom_imprimante or 'Datamax'
#            print 'imprimante=',imprimante

#            cmd="lpr -h -P"+imprimante+" "+path
#            os.system(cmd)
#        return





class is_tracabilite_reception(osv.osv):
    _name = 'is.tracabilite.reception'
    _description = u"Traçabilité réception"
    _order = "create_date desc"
    
    _columns = {
        'name': fields.char(u'Numéro', required=True, readonly=True),
        'picking_id': fields.many2one('stock.picking', u'Réception', readonly=False),
        'product_id': fields.many2one('product.template', u'Article', readonly=False),
        'bl_fournisseur': fields.char(u'Numéro du BL fournisseur', readonly=False),
        'move_id': fields.many2one('stock.move', 'Mouvement de stock', readonly=False),
        'quantity': fields.float(u'Quantité', readonly=False),
    }
    
    _defaults = {
        'name': ' ',
    }
    
    def create(self, cr, uid, vals, context=None):
        self.update_product(cr, uid, vals, context)
        data_obj = self.pool.get('ir.model.data')
        sequence_ids = data_obj.search(cr, uid, [('name','=','is_bsa_tracabilite_seq')], context=context)
        if sequence_ids:
            sequence_id = data_obj.browse(cr, uid, sequence_ids[0], context).res_id
            vals['name'] = self.pool.get('ir.sequence').get_id(cr, uid, sequence_id, 'id', context=context)
        new_id = super(is_tracabilite_reception, self).create(cr, uid, vals, context=context)
        return new_id


    def write(self, cr, uid, ids, vals, context=None):
        self.update_product(cr, uid, vals, context)
        res = super(is_tracabilite_reception, self).write(cr, uid, ids, vals, context=context)
        return res


    def update_product(self, cr, uid, vals, context=None):
        if "move_id" in vals:
            obj = self.pool.get('stock.move')
            doc = obj.browse(cr, uid, vals["move_id"], context=context)
            #product_id=doc.product_id.id
            product_id=doc.product_id.product_tmpl_id.id
            vals.update({'product_id': product_id})
        return vals





    def imprimer_etiquette_direct(self, cr, uid, ids, context=None):
        etiquettes=self.generer_etiquette(cr, uid, ids, context=context)
        #print etiquettes
        self.pool.get('is.tracabilite.reception').imprimer_etiquette(cr, uid, etiquettes)
        return


    def generer_etiquette(self, cr, uid, ids, context=None):
        obj = self.pool.get('is.tracabilite.reception')
        eti = obj.browse(cr, uid, ids[0], context)

        txt=""
        txt=txt+chr(2)+"qC"+chr(10)
        txt=txt+chr(2)+"qC"+chr(10)
        txt=txt+chr(2)+"n"+chr(10)
        txt=txt+chr(2)+"e"+chr(10)
        txt=txt+chr(2)+"c0000"+chr(10)
        txt=txt+chr(2)+"Kf0000"+chr(10)
        txt=txt+chr(2)+"V0"+chr(10)
        txt=txt+chr(2)+"M0591"+chr(10)
        txt=txt+chr(2)+"L"+chr(10)
        txt=txt+"A2"+chr(10)
        txt=txt+"D11"+chr(10)
        txt=txt+"z"+chr(10)
        txt=txt+"PG"+chr(10)
        txt=txt+"SG"+chr(10)
        txt=txt+"pC"+chr(10)
        txt=txt+"H20"+chr(10)

        txt=txt+datamax(x=15,y=220,sizex=2,sizey=2,txt="ARTICLE:")
        if eti.product_id:
            txt=txt+datamax(x=15,y=200,sizex=3,sizey=4,txt=eti.product_id.name.encode("utf-8"))

        if eti.product_id:
            txt=txt+datamax(x=190,y=220,sizex=2,sizey=2,txt="ID:"+str(eti.product_id.id))

        txt=txt+datamax(x=15,y=180,sizex=2,sizey=2,txt="FOURNISSEUR:")
        if eti.picking_id:
            txt=txt+datamax(x=15,y=160,sizex=4,sizey=4,txt=eti.picking_id.partner_id.name.encode("utf-8"))

        txt=txt+datamax(x=15,y=140,sizex=2,sizey=2,txt="RECEPTION:")
        if eti.picking_id:
            txt=txt+datamax(x=15,y=120,sizex=4,sizey=4,txt=eti.picking_id.name.encode("utf-8"))

        txt=txt+datamax(x=190,y=140,sizex=2,sizey=2,txt="BL FOURNISSEUR:")
        if eti.bl_fournisseur:
            txt=txt+datamax(x=190,y=120,sizex=4,sizey=4,txt=eti.bl_fournisseur.encode("utf-8"))

        txt=txt+datamax(x=15,y=100 ,sizex=2,sizey=2,txt="DATE:")
        if eti.move_id:
            txt=txt+datamax(x=15,y=80  ,sizex=4,sizey=4,txt=str(eti.move_id.create_date)[0:10])

        txt=txt+datamax(x=190,y=100 ,sizex=2,sizey=2,txt="LOT:")
        txt=txt+datamax(x=190,y=80  ,sizex=4,sizey=4,txt=eti.name.encode("utf-8"))

        #t=str(eti.name)
        #sizex="4"
        #sizey="6"
        #x="025"
        #y="020"
        #txt=txt+"1E1"+sizex+"0"+sizey+"10"+y+"0"+x+"B"+t+chr(10) # Code barre
        txt=txt+"1E1406100060025B"+str(eti.name)+chr(10) # Code barre

        txt=txt+"^01"+chr(10)
        txt=txt+"Q0001"+chr(10)
        txt=txt+"E"+chr(10)
        return txt




    def imprimer_etiquette(self, cr, uid, etiquettes):
        #print etiquettes
        etiquettes=unicode(etiquettes,'utf-8')
        #print etiquettes
        etiquettes=etiquettes.encode("windows-1252")
        #print etiquettes
        path="/tmp/etiquette.txt"
        err=""
        try:
            fichier = open(path, "w")
        except IOError, e:
            err="Problème d'accès au fichier '"+path+"' => "+ str(e)
        if err=="":
            fichier.write(etiquettes)
            fichier.close()


            user       = self.pool['res.users'].browse(cr, uid, [uid])[0]
            imprimante = user.company_id.is_nom_imprimante or 'Datamax'
            print 'imprimante=',imprimante

            cmd="lpr -h -P"+imprimante+" "+path
            os.system(cmd)
        return








    
    
class is_tracabilite_livraison(osv.osv):
    _name = 'is.tracabilite.livraison'
    _description = u"Traçabilité livraison"
    _order = "name"
    #_order = "create_date desc"
    
    _columns = {
        'name': fields.char(u'Numéro de série', required=True, readonly=True),
        'production_id': fields.many2one('mrp.production', u'OF', required=False),
        'lot_fabrication': fields.integer(u'Lot de fabrication'),
        'product_id': fields.many2one('product.template', u'Article', readonly=False),
        'fabrique':fields.datetime("Produit fabriqué le"),
        'consomme':fields.datetime("Semi-fini consommé le"),

        'operateur_ids': fields.many2many('hr.employee', 'is_tracabilite_livraison_operateur_rel', 'tracabilite_livraison_id', 'employee_id', 'Opérateurs Fabrication'),

        'sale_id': fields.many2one('sale.order', 'Commande Client'),
        'move_id': fields.many2one('stock.move', 'Ligne de livraison'),
        'picking_id': fields.many2one('stock.picking', u'Réception', readonly=False),
        'quantity': fields.float(u'Quantité'),
        'livraison':fields.datetime("Produit livré le"),

        'operateur_livraison_ids': fields.many2many('hr.employee', 'is_tracabilite_livraison_operateur_livraison_rel', 'tracabilite_livraison_id', 'employee_id', 'Opérateurs Livraison'),

        'etiquette_reception_id': fields.one2many('is.tracabilite.reception.line', 'livraison_id', 'Etiquettes réception'),
        'etiquette_livraison_id': fields.one2many('is.tracabilite.livraison.line', 'livraison_id', 'Etiquettes semi-fini'),
    }



    
    _defaults = {
        'name': ' ',
        'lot_fabrication': 1,
    }




    
    def ajouter_etiquette_of(self, cr, uid, etiquette_ids, production_id, context=None):
        """ Ajouter l'etiquette à la liste des etiquettes de l'OF correspondant """
        if production_id:
            production_obj = self.pool.get('mrp.production')
            production = production_obj.read(cr, uid, production_id, [], context=context)
            if  production['etiquette_ids']:
                if 'etiquette_ids' in production:
                    etiquette_ids += production['etiquette_ids']
            production_obj.write(cr, uid, production_id, {'etiquette_ids': [(6, 0, etiquette_ids)]}, context=context)
        return True
            
        
    
    def create(self, cr, uid, vals, context=None):
        self.update_product(cr, uid, vals, context)
        data_obj = self.pool.get('ir.model.data')
        sequence_ids = data_obj.search(cr, uid, [('name','=','is_bsa_tracabilite_livraison_seq')], context=context)
        if sequence_ids:
            sequence_id = data_obj.browse(cr, uid, sequence_ids[0], context).res_id
            vals['name'] = self.pool.get('ir.sequence').get_id(cr, uid, sequence_id, 'id', context=context)
        new_id = super(is_tracabilite_livraison, self).create(cr, uid, vals, context=context)
        self.ajouter_etiquette_of(cr, uid, [new_id], vals['production_id'], context)
        return new_id


    def write(self, cr, uid, ids, vals, context=None):
        self.update_product(cr, uid, vals, context)
        res = super(is_tracabilite_livraison, self).write(cr, uid, ids, vals, context=context)
        return res


    def update_product(self, cr, uid, vals, context=None):
        if "production_id" in vals:
            obj = self.pool.get('mrp.production')
            doc = obj.browse(cr, uid, vals["production_id"], context=context)
            product_id=doc.product_id.product_tmpl_id.id
            vals.update({'product_id': product_id})
        return vals



    def imprimer_etiquette_livraison_direct(self, cr, uid, ids, context=None):
        etiquettes=self.generer_etiquette_livraison(cr, uid, ids, context=context)
        #print etiquettes
        #imprimer_etiquette(cr, uid, etiquettes)
        self.pool.get('is.tracabilite.reception').imprimer_etiquette(cr, uid, etiquettes)
        return



    def generer_etiquette_livraison(self, cr, uid, ids, context=None):
        obj = self.pool.get('is.tracabilite.livraison')
        eti = obj.browse(cr, uid, ids[0], context)

        txt=""
        txt=txt+chr(2)+"qC"+chr(10)
        txt=txt+chr(2)+"qC"+chr(10)
        txt=txt+chr(2)+"n"+chr(10)
        txt=txt+chr(2)+"e"+chr(10)
        txt=txt+chr(2)+"c0000"+chr(10)
        txt=txt+chr(2)+"Kf0000"+chr(10)
        txt=txt+chr(2)+"V0"+chr(10)
        txt=txt+chr(2)+"M0591"+chr(10)
        txt=txt+chr(2)+"L"+chr(10)
        txt=txt+"A2"+chr(10)
        txt=txt+"D11"+chr(10)
        txt=txt+"z"+chr(10)
        txt=txt+"PG"+chr(10)
        txt=txt+"SG"+chr(10)
        txt=txt+"pC"+chr(10)
        txt=txt+"H20"+chr(10)


        print "eti=",eti
        print "eti.product_id=",eti.product_id
        print "eti.product_id.default_code=",eti.product_id.default_code

        txt=txt+datamax(x=15,y=220,sizex=2,sizey=2,txt="ARTICLE:")
        txt=txt+datamax(x=15,y=200,sizex=3,sizey=4,txt=eti.product_id.name.encode("utf-8"))

        txt=txt+datamax(x=15,y=180,sizex=2,sizey=2,txt="REF")
        default_code=eti.product_id.default_code or ''
        txt=txt+datamax(x=15,y=160,sizex=4,sizey=4,txt=default_code.encode("utf-8"))


        txt=txt+datamax(x=200,y=180,sizex=2,sizey=2,txt="QT:")
        txt=txt+datamax(x=200,y=160,sizex=3,sizey=4,txt=str(eti.lot_fabrication))


        #txt=txt+datamax(x=190,y=140,sizex=2,sizey=2,txt="BL FOURNISSEUR:")
        #txt=txt+self.datamax(x=190,y=120,sizex=4,sizey=4,txt=eti.bl_fournisseur.encode("utf-8"))


        txt=txt+datamax(x=15,y=140 ,sizex=2,sizey=2,txt="DATE:")
        txt=txt+datamax(x=15,y=120  ,sizex=3,sizey=4,txt=str(eti.production_id.date_planned)[0:10])

        txt=txt+datamax(x=120,y=140 ,sizex=2,sizey=2,txt="LOT:")
        txt=txt+datamax(x=120,y=120  ,sizex=3,sizey=4,txt=eti.name.encode("utf-8"))

        txt=txt+datamax(x=200,y=140,sizex=2,sizey=2,txt="OF:")
        txt=txt+datamax(x=200,y=120,sizex=3,sizey=4,txt=eti.production_id.name.encode("utf-8"))


        #Code barre pour le client
        #t=str(eti.production_id.date_planned)[2:10]
        #t=t.replace("-", "",2)
        #t=t+"-"+str(eti.name)
        t=str(eti.name)
        sizex="3"
        sizey="7"
        x="025"
        y="020"
        #txt=txt+"1E1"+sizex+"0"+sizey+"101"+y+x+"B"+t+chr(10) # Code barre
        txt=txt+"1E1"+sizex+"0"+sizey+"10"+y+"0"+x+"B"+t+chr(10) # Code barre

        #Code barre pour BSA
        #txt=txt+"1E1406100060014B"+str(eti.name)+chr(10) # Code barre

        txt=txt+"^01"+chr(10)
        txt=txt+"Q0001"+chr(10)
        txt=txt+"E"+chr(10)
        return txt




    #def act_livraison(self, cr, uid, vals, context=None):
    #    print "test livraison"
    #    print str(vals)
    #    print vals["livraison"]
    #    print vals["etiquettes"]
    #    return {}


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
                    #products.append(move.product_id.id)
                    products.append(move.product_id.product_tmpl_id)
                    print "## TEST :"+str(move.product_id.product_tmpl_id)
        return products


    def verifier_product_etiquette(self, cr, uid, etiquettes, products, context=None):
        print etiquettes, products
        if etiquettes:
            for etiquette in etiquettes:
                #if etiquette.production_id.product_id.id in products:
                if etiquette.product_id.id in products:
                    continue
                else:
                    return False
        return True


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


    def existe_etiquette(self, cr, uid, etiquettes, product_id, context=None):
        lst = self.grouper_etiquettes_product(cr, uid, etiquettes, context)
        for item in lst:
            if item['product_id'] == product_id:
                return item['qty']
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


    def etiquette_in_list(self, cr, uid, list, product_id, context=None):
        for item in list:
            if item['product_id'] == product_id:
                return item
            else:
                continue
        return False


    def lier_etiquettes_mouvement(self, cr, uid, picking, etiquette, context=None):
        etiquette_obj = self.pool.get('is.tracabilite.livraison')
        if picking.move_lines:
            for move in picking.move_lines:
                if move.product_id.id == etiquette.production_id.product_id.id:
                    print fields.datetime.now
                    print time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime())

                    vals={
                        'move_id':move.id,
                        'livraison': time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime())
                    }
                    etiquette_obj.write(cr, uid, etiquette.id, vals, context=context)
                else:
                    continue
        return True
                    




    def act_livraison(self, cr, uid, vals, context=None):
        #print str(vals)
        sale_obj      = self.pool.get('sale.order')
        picking_obj   = self.pool.get('stock.picking')
        etiquette_obj = self.pool.get('is.tracabilite.livraison')
        err=""
        sale_id=vals["sale_id"]
        sale = sale_obj.browse(cr, uid , sale_id, context=context)
        picking = self.get_picking_id(cr, uid, sale.picking_ids, context)
        if picking:
            picking_obj.action_assign(cr, uid, [picking.id], context=context)
            picking_obj.force_assign(cr, uid, [picking.id], context=context)
            products = self.get_products_from_move_lines(cr, uid, picking, context)
            ids=vals["etiquettes"]
            etiquettes=[]
            for id in ids:
                etiquette = etiquette_obj.browse(cr, uid , id, context=context)
                etiquettes.append(etiquette)


            print etiquettes
            self.livrer_produits(cr, uid, picking, etiquettes, context)
            for etiquette in etiquettes:
                self.lier_etiquettes_mouvement(cr, uid, picking, etiquette, context)
                etiquette_obj.write(cr, uid, etiquette.id, {'sale_id': sale_id})
            etiquette_ids = [etiquette.id for etiquette in etiquettes]
            picking_obj.write(cr, uid, picking.id, {'etiquette_livraison_ids': [(6, 0, etiquette_ids)]})



            #if self.verifier_product_etiquette(cr, uid, etiquettes, products, context):
            #    print etiquettes
            #    self.livrer_produits(cr, uid, picking, etiquettes, context)
            #    for etiquette in etiquettes:
            #        self.lier_etiquettes_mouvement(cr, uid, picking, etiquette, context)
            #        etiquette_obj.write(cr, uid, etiquette.id, {'sale_id': sale_id})
            #    etiquette_ids = [etiquette.id for etiquette in etiquettes]
            #    picking_obj.write(cr, uid, picking.id, {'etiquette_livraison_ids': [(6, 0, etiquette_ids)]})
            #else:
            #    print "##### Etiquettes scannees non livrable #####"
            #    err="Etiquettes scannees non livrable"
        else:
            err="Commande non livrable"
        return {"err":err,"data":""}






    
    
class is_tracabilite_reception_line(osv.osv):
    _name = 'is.tracabilite.reception.line'
    _description = u"Traçabilité reception line"
    
    _columns = {
        'etiquette_id': fields.many2one('is.tracabilite.reception', 'Etiquettes réception', required=True),
        'quantity': fields.float(u'Quantité', required=True),
        'livraison_id': fields.many2one('is.tracabilite.livraison', 'Etiquette livraison'),
    }
    
    _defaults = {
        'quantity': 1.0,
    }



    
    
class is_tracabilite_livraison_line(osv.osv):
    _name = 'is.tracabilite.livraison.line'
    _description = u"Traçabilité livraison line"
    
    _columns = {
        'etiquette_id': fields.many2one('is.tracabilite.livraison', 'Etiquettes semi-fini', required=True),
        'quantity': fields.float(u'Quantité', required=True),
        'livraison_id': fields.many2one('is.tracabilite.livraison', 'Etiquette livraison'),
    }
    
    _defaults = {
        'quantity': 1.0,
    }








        
