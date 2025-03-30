from odoo import api, fields, models, _
import requests
import logging
import json

_logger = logging.getLogger(__name__)

class FleetTrackingSettings(models.Model):
    _name = 'fleet.tracking.settings'
    _description = 'Fleet Tracking Settings'
    _rec_name = 'name'

    name = fields.Char('Name', default='Tracking Configuration')
    server_url = fields.Char('Server URL', required=True, 
                            help='URL of the tracking server (e.g. http://traccar.example.com:8082)')
    api_path = fields.Char('API Path', default='/api', 
                          help='Path to the REST API (default: /api)')
    username = fields.Char('Username', required=True)
    password = fields.Char('Password', required=True)
    auto_sync_interval = fields.Integer('Auto Sync Interval (minutes)', default=5,
                                      help='Interval in minutes for automatic synchronization')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    
    def test_connection(self):
        """Test the connection to the tracking server"""
        self.ensure_one()
        
        try:
            response = requests.get(
                self.server_url + self.api_path + '/session',
                auth=(self.username, self.password),
                timeout=10
            )
            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Test'),
                        'message': _('Connection successful!'),
                        'sticky': False,
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Test'),
                        'message': _('Connection failed: %s') % response.text,
                        'sticky': False,
                        'type': 'danger',
                    }
                }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Test'),
                    'message': _('Connection error: %s') % str(e),
                    'sticky': False,
                    'type': 'danger',
                }
            }
    
    def sync_devices(self):
        """Synchronize devices from the tracking server"""
        self.ensure_one()
        
        try:
            response = requests.get(
                self.server_url + self.api_path + '/devices',
                auth=(self.username, self.password),
                timeout=10
            )
            
            if response.status_code != 200:
                _logger.error("Failed to sync devices: %s", response.text)
                return False
                
            devices = response.json()
            device_obj = self.env['fleet.tracking.device']
            
            for device_data in devices:
                external_id = str(device_data.get('id'))
                existing_device = device_obj.search([('external_id', '=', external_id)])
                
                vals = {
                    'name': device_data.get('name'),
                    'unique_id': device_data.get('uniqueId'),
                    'model': device_data.get('model', ''),
                    'category': device_data.get('category', ''),
                    'phone': device_data.get('phone', ''),
                    'last_update': fields.Datetime.now(),
                }
                
                if existing_device:
                    existing_device.write(vals)
                else:
                    vals.update({
                        'external_id': external_id,
                        'config_id': self.id,
                    })
                    device_obj.create(vals)
                    
            return True
            
        except Exception as e:
            _logger.error("Error syncing devices: %s", str(e))
            return False
    
    def sync_positions(self):
        """Synchronize positions from the tracking server"""
        self.ensure_one()
        
        try:
            # Get all devices with valid external_id
            devices = self.env['fleet.tracking.device'].search([
                ('external_id', '!=', False),
                ('config_id', '=', self.id)
            ])
            
            if not devices:
                _logger.warning("No devices found for synchronization")
                return False
                
            device_ids = [device.external_id for device in devices]
            
            # Get positions for devices
            response = requests.get(
                self.server_url + self.api_path + '/positions',
                params={'deviceId': ','.join(device_ids)},
                auth=(self.username, self.password),
                timeout=10
            )
            
            if response.status_code != 200:
                _logger.error("Failed to sync positions: %s", response.text)
                return False
                
            positions = response.json()
            position_obj = self.env['fleet.tracking.position']
            
            for position_data in positions:
                device_id = str(position_data.get('deviceId'))
                device = self.env['fleet.tracking.device'].search([('external_id', '=', device_id)], limit=1)
                
                if not device:
                    continue
                    
                # Check if position already exists
                external_id = str(position_data.get('id'))
                existing_position = position_obj.search([('external_id', '=', external_id)], limit=1)
                
                if existing_position:
                    continue
                    
                # Create new position
                vals = {
                    'external_id': external_id,
                    'device_id': device.id,
                    'latitude': position_data.get('latitude'),
                    'longitude': position_data.get('longitude'),
                    'altitude': position_data.get('altitude'),
                    'speed': position_data.get('speed'),
                    'direction': position_data.get('course'),
                    'timestamp': fields.Datetime.from_string(position_data.get('fixTime')),
                    'attributes': json.dumps(position_data.get('attributes', {})),
                }
                
                position = position_obj.create(vals)
                
                # Update vehicle with last position
                if device.vehicle_id:
                    device.vehicle_id.write({
                        'last_position_id': position.id,
                        'last_update': position.timestamp,
                    })
                    
            return True
            
        except Exception as e:
            _logger.error("Error syncing positions: %s", str(e))
            return False