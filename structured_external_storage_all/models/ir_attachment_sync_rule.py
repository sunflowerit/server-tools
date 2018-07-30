# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class AttachmentSyncRule(models.Model):
    _name = 'ir.attachment.sync.rule'
    _description = 'Define Specific Rules for Cloud Sync'

    @api.model
    def _get_model_selection(self):
        """Get models and their names."""
        model_objs = self.env["res.request.link"].search([
            ("ext_attachment_sync", "=", True)], order="name")
        return [(m.object, m.name) for m in model_objs]

    name = fields.Char('Name', required=True)
    source_model = fields.Many2one(
        'res.request.link', 'Source Model', required=True,
        domain=[('ext_attachment_sync', '=', True)])
    sync_type = fields.Selection(
        string='Sync Type', related='location_id.protocol', readonly=True)
    frequency = fields.Integer('Frequency in Days', required=True)
    sync_old_attachments = fields.Boolean(
        'Sync Pre-existing Records',
        help="Only useful if you want to Upload existing attachments before "
        "the installation of this module")
    last_sync_date = fields.Datetime('Last Sync Date')
    location_id = fields.Many2one(
        'external.file.location', 'Sync Name', required=True)
    domain = fields.Char(
        'Domain', default=[(1,'=',1)],
        help='Conditions that will apply to the '
        'select model. E.g [(amount, '>', 500, )]')
    task_ids = fields.One2many(
        'external.file.task', related='location_id.task_ids')

    @api.one
    @api.constrains('domain')
    def _check_domain(self):
        model_obj = self.env[self.source_model.object]
        domain = safe_eval(self.domain)
        for leaf in domain:
            if not isinstance(leaf, tuple) or not len(leaf) == 3:
                raise ValidationError(_("Domain should have the format "
                    "'[('field_name', 'condition', value), ...]'"))
        model_obj.search(domain)  # Testing if domain works

    @api.multi
    def run_sync_now(self):
        for this in self:
            # Check if we need to sync old attachments
            if this.sync_old_attachments:
                model = this.source_model.object
                if this.domain:
                    domain = safe_eval(this.domain)
                rec_ids = self.env[model].search(domain).ids
                old_attachments = self.env['ir.attachment'].search([
                    ('res_model', '=', model), ('res_id', 'in', rec_ids)])
                old_attachments.create_metadata()
        self.env.cr.commit()  # syncer creates a new cursor
        self.sync_created_metadata()

    @api.multi
    def sync_created_metadata(self):
        # Proceed to sync the created metadata
        meta_data = self.env['ir.attachment.metadata'].search([
            ('location_id', '=', self.location_id.id),
            ('state', 'in', ('pending', 'failed'))
        ])
        # Call the respective sync type and location to run
        for this in meta_data:
            this.run()

        self.write({
            'last_sync_date': fields.datetime.now(),
        })
