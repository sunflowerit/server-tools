# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import io
from odoo import models, fields, api, _


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    def create(self, vals):
        res = super(Attachment, self).create(vals)
        res.create_metadata()
        return res

    @api.multi
    def create_metadata(self):
        sync_rule_obj = self.env['ir.attachment.sync.rule']
        all_rules = sync_rule_obj.search([]).mapped(
            'source_model.object')
        for attachment in self:
            # check if res_model is in the define rules.
            if attachment.res_model in all_rules:
                sync_rule = sync_rule_obj.search(
                    [('source_model.object', '=', attachment.res_model)])
                for rule in sync_rule:
                    # Gather vals for the ir.attachment.metadata from sync_rule
                    vals = {
                        'attachment_id': attachment.id,
                        'name': attachment.datas_fname[:-4],
                        'type': 'binary',
                        'task_id': rule.location_id.task_ids[0].id,  # get the first
                        'file_type': 'export_external_location',
                    }
                    self.env['ir.attachment.metadata'].create(vals)
        return True

