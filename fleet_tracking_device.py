# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FleetTrackingDevice(models.Model):
    _name = 'fleet.tracking.device'
    _description = 'Fleet Tracking Device'
    _rec_name = 'identifier'
    
    name = fields.Char('Name', required=True)
    identifier = fields.Char('Device ID', required=True, help='Unique identifier in Traccar system')
    active = fields.Boolean(default=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    last_position_id = fields.Many2one('fleet.tracking.position', string='Last Position', readonly=True)
    traccar_uniqueid = fields.Char('Traccar Unique ID')
    device_model = fields.Char('Device Model')
    phone = fields.Char('Phone Number')
    category = fields.Selection([
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('motorcycle', 'Motorcycle'),
    ], string='Category', default='car')
    status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('unknown', 'Unknown'),
    ], string='Status', default='unknown')
    last_update = fields.Datetime('Last Update')
    
    _sql_constraints = [
        ('identifier_uniq', 'unique(identifier)', 'Device identifier must be unique!')
    ]
    
    @api.constrains('vehicle_id')
    def _check_vehicle_id(self):
        for record in self:
            if record.vehicle_id and self.search_count([
                ('vehicle_id', '=', record.vehicle_id.id),
                ('id', '!=', record.id)
            ]):
                raise ValidationError(_('A vehicle can only be linked to one tracking device.'))