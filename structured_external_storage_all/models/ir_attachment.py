# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval


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
        for attachment in self:
            # check if res_model is in the define rules.
            all_matching_rules = sync_rule_obj.search([
                ('source_model.object', '=', attachment.res_model)
            ], order='sequence asc')
            selected_matching_rules = []
            for rule in all_matching_rules:
                if rule.domain:
                    domain = safe_eval(rule.domain)
                    domain.append(('id', '=', attachment.res_id))
                    if not self.env[attachment.res_model].search(domain):
                        continue
                previous_rules_with_same_loc_and_lower_seq = [
                    previous_rule for previous_rule in selected_matching_rules
                    if previous_rule.sync_type == rule.sync_type
                       and previous_rule.sequence < rule.sequence
                ]
                if not previous_rules_with_same_loc_and_lower_seq:
                    selected_matching_rules.append(rule)
            for rule in selected_matching_rules:
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

