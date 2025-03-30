# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    device_id = fields.Many2one('fleet.tracking.device', string='Tracking Device', 
                               help='Traccar tracking device assigned to this vehicle')
    current_latitude = fields.Float('Current Latitude', digits=(16, 6), readonly=True)
    current_longitude = fields.Float('Current Longitude', digits=(16, 6), readonly=True)
    current_speed = fields.Float('Current Speed (km/h)', readonly=True)
    vehicle_status = fields.Selection([
        ('moving', 'Moving'),
        ('stopped', 'Stopped'),
        ('idle', 'Idle'),
        ('unknown', 'Unknown')
    ], string='Status', default='unknown', readonly=True)
    last_position_update = fields.Datetime('Last Position Update', readonly=True)
    position_history_ids = fields.One2many('fleet.tracking.position', 'vehicle_id', string='Position History')
    
    def action_view_map(self):
        self.ensure_one()
        return {
            'name': _('Vehicle Location'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle',
            'view_mode': 'map',
            'res_id': self.id,
        }
    
    def action_view_position_history(self):
        self.ensure_one()
        return {
            'name': _('Position History'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.tracking.position',
            'view_mode': 'tree,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }
    
    @api.model
    def update_vehicle_positions(self):
        """Cron job method to update vehicle positions from Traccar"""
        # This will be implemented to fetch data from Traccar API
        return True