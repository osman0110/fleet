from odoo import models, fields, api, _
import json
import logging

_logger = logging.getLogger(__name__)

class TraccarDevice(models.Model):
    _name = 'traccar.device'
    _description = 'Traccar Device'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char('Name', required=True, tracking=True)
    server_id = fields.Many2one('traccar.server', string='Traccar Server', required=True, ondelete='cascade')
    device_id = fields.Integer('Device ID', required=True)
    unique_id = fields.Char('Unique ID', required=True, tracking=True, 
                          help="IMEI, serial number or other unique identifier")
    active = fields.Boolean('Active', default=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    last_update = fields.Datetime('Last Update')
    position_id = fields.Many2one('traccar.position', string='Last Position')
    status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('unknown', 'Unknown')
    ], string='Status', default='unknown', tracking=True)
    attributes = fields.Text('Attributes', help="JSON encoded attributes from Traccar")
    
    phone = fields.Char('Phone')
    model = fields.Char('Model')
    contact = fields.Char('Contact')
    category = fields.Char('Category')
    
    # Display fields for attributes
    attr_motion = fields.Boolean('In Motion', compute='_compute_attributes')
    attr_ignition = fields.Boolean('Ignition', compute='_compute_attributes')
    attr_alarm = fields.Boolean('Alarm', compute='_compute_attributes')
    
    _sql_constraints = [
        ('server_device_id_unique', 'unique(server_id, device_id)', 
         'Device must be unique per Traccar server'),
    ]
    
    @api.depends('attributes')
    def _compute_attributes(self):
        for device in self:
            attrs = {}
            if device.attributes:
                try:
                    attrs = json.loads(device.attributes)
                except Exception as e:
                    _logger.error("Error parsing device attributes: %s", str(e))
            
            device.attr_motion = bool(attrs.get('motion', False))
            device.attr_ignition = bool(attrs.get('ignition', False))
            device.attr_alarm = bool(attrs.get('alarm', False))
            
    def action_view_positions(self):
        self.ensure_one()
        return {
            'name': _('Positions'),
            'view_mode': 'tree,form',
            'res_model': 'traccar.position',
            'domain': [('device_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_device_id': self.id},
        }
    
    def action_view_events(self):
        self.ensure_one()
        return {
            'name': _('Events'),
            'view_mode': 'tree,form',
            'res_model': 'traccar.event',
            'domain': [('device_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_device_id': self.id},
        }
        
    def action_fetch_latest_position(self):
        self.ensure_one()
        try:
            response = self.server_id._make_api_request(f'positions?deviceId={self.device_id}&limit=1')
            if response.status_code == 200:
                positions = response.json()
                if positions:
                    position_data = positions[0]
                    position_vals = {
                        'device_id': self.id,
                        'position_id': position_data['id'],
                        'protocol': position_data.get('protocol'),
                        'server_time': position_data.get('serverTime'),
                        'device_time': position_data.get('deviceTime'),
                        'fix_time': position_data.get('fixTime'),
                        'latitude': position_data.get('latitude'),
                        'longitude': position_data.get('longitude'),
                        'altitude': position_data.get('altitude'),
                        'speed': position_data.get('speed'),
                        'course': position_data.get('course'),
                        'accuracy': position_data.get('accuracy'),
                        'attributes': json.dumps(position_data.get('attributes', {})),
                    }
                    
                    existing_position = self.env['traccar.position'].search([
                        ('device_id', '=', self.id),
                        ('position_id', '=', position_data['id'])
                    ], limit=1)
                    
                    if existing_position:
                        existing_position.write(position_vals)
                        self.position_id = existing_position.id
                    else:
                        new_position = self.env['traccar.position'].create(position_vals)
                        self.position_id = new_position.id
                        
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'message': _("Position updated successfully"),
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'message': _("No positions found for this device"),
                            'type': 'warning',
                            'sticky': False,
                        }
                    }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _("Failed to fetch position: %s") % response.text,
                        'type': 'danger',
                        'sticky': False,
                    }
                }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("Failed to fetch position: %s") % str(e),
                    'type': 'danger',
                    'sticky': False,
                }
            }