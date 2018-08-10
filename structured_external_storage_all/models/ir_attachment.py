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
        """Use sequence to obtain the rule with high priority"""
        sync_rule_obj = self.env['ir.attachment.sync.rule']
        all_rules = sync_rule_obj.search([]).mapped(
            'source_model.object')
        for attachment in self:
            # check if res_model is in the define rules.
            if attachment.res_model in all_rules:
                sync_rule = sync_rule_obj.search(
                    [('source_model.object', '=', attachment.res_model),
                     ('sequence', '<', 10)],
                    order='sequence asc')
                if not sync_rule:
                    sync_rule = sync_rule_obj.search(
                        [('source_model.object', '=', attachment.res_model)],
                        order='sequence asc', limit=1)

                for rule in sync_rule:
                    # Check if attachment already exists in the metas
                    metadata_obj = self.env['ir.attachment.metadata']
                    existing_metas = metadata_obj.search(
                        [('attachment_id', '=', attachment.id)])
                    locations = existing_metas.mapped('location_id').ids
                    if not existing_metas or rule.location_id.id not in \
                            locations:
                        # Gather vals from sync_rule
                        vals = {
                            'attachment_id': attachment.id,
                            'name': attachment.datas_fname[:-4],
                            'type': 'binary',
                            'task_id': rule.location_id.task_ids[0].id,  # get the first
                            'file_type': 'export_external_location',
                        }
                        metadata_obj.create(vals)
        return True

