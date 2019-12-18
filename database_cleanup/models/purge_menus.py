# -*- coding: utf-8 -*-
# © 2014-2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class CleanupPurgeLineMenu(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.menu'

    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.menu', 'Purge Wizard', readonly=True)
    menu_id = fields.Many2one('ir.ui.menu', 'Menu entry')

    @api.multi
    def purge(self):
        self.mapped('menu_id').unlink()
        return self.write({'purged': True})


class CleanupPurgeWizardMenu(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.menu'
    _description = 'Purge menus'

    @api.model
    def find(self):
        """
        Search for models that cannot be instantiated.
        """
        def model_deleted(model_name):
            """Check wether model has been deleted."""
            if model_name and model_name not in self.env.registry:
                return True
            return False

        res = []
        for menu in self.env['ir.ui.menu'].with_context(active_test=False)\
                .search([('action', '!=', False)]):
            if not menu.action:
                continue
            if menu.action.type != 'ir.actions.act_window':
                continue
            if model_deleted(menu.action.src_model) or \
                    model_deleted(menu.action.res_model):
                res.append((0, 0, {
                    'name': menu.complete_name,
                    'menu_id': menu.id,
                }))
        if not res:
            raise UserError(_('No dangling menu entries found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.menu', 'wizard_id', 'Menus to purge')
