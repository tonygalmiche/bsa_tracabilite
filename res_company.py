# -*- coding: utf-8 -*-

from openerp import models,fields,api
from openerp.tools.translate import _



class res_company(models.Model):
    _inherit = 'res.company'

    is_nom_imprimante = fields.Char('Nom imprimante Etiquettes')







