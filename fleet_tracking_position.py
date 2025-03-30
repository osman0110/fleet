# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class FleetTrackingPosition(models.Model):
    _name = 'fleet.tracking.position'
    _description = 'Fleet Vehicle Position'
    _order = 'timestamp DESC'
    
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True, ondelete='cascade')
    device_id = fields.Many2one('fleet.tracking.device', string='Device', ondelete='cascade')
    timestamp = fields.Datetime('Timestamp', required=True)
    latitude = fields.Float('Latitude', digits=(16, 6), required=True)
    longitude = fields.Float('Longitude', digits=(16, 6), required=True)
    altitude = fields.Float('Altitude')
    speed = fields.Float('Speed (km/h)')
    course = fields.Float('Course')
    address = fields.Char('Address')
    attributes = fields.Text('Attributes')
    
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.vehicle_id.name} ({record.timestamp})"
            result.append((record.id, name))
        return result
    
    @api.model
    def create(self, vals):
        res = super(FleetTrackingPosition, self).create(vals)
        # Update vehicle with latest position information
        if res.vehicle_id:
            res.vehicle_id.write({
                'current_latitude': res.latitude,
                'current_longitude': res.longitude,
                'current_speed': res.speed,
                'last_position_update': res.timestamp,
                'vehicle_status': 'moving' if res.speed > 5 else 'stopped',
            })
        # Update device with latest position
        if res.device_id:
            res.device_id.write({
                'last_position_id': res.id,
                'last_update': res.timestamp,
                'status': 'online',
            })
        return res