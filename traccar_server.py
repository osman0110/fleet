from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import logging
import json
import base64

_logger = logging.getLogger(__name__)

class TraccarServer(models.Model):
    _name = 'traccar.server'
    _description = 'Traccar Server'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Name', required=True)
    url = fields.Char('URL', required=True, help="Traccar server URL, e.g. http://traccar.example.com:8082")
    api_url = fields.Char('API URL', compute='_compute_api_url', store=True)
    username = fields.Char('Username', required=True)
    password = fields.Char('Password', required=True)
    active = fields.Boolean('Active', default=True)
    connection_status = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error')
    ], string='Connection Status', default='disconnected', tracking=True)
    last_sync_date = fields.Datetime('Last Synchronization', tracking=True)
    sync_interval = fields.Integer('Sync Interval (minutes)', default=5, 
        help="Interval in minutes for synchronizing data with Traccar")
    device_count = fields.Integer('Devices', compute='_compute_device_count')
    
    @api.depends('url')
    def _compute_api_url(self):
        for server in self:
            if server.url:
                if server.url.endswith('/'):
                    server.api_url = f"{server.url}api"
                else:
                    server.api_url = f"{server.url}/api"
            else:
                server.api_url = False
    
    def _compute_device_count(self):
        for server in self:
            server.device_count = self.env['traccar.device'].search_count([
                ('server_id', '=', server.id)
            ])
            
    @api.constrains('url')
    def _check_url_format(self):
        for server in self:
            if server.url and not (server.url.startswith('http://') or server.url.startswith('https://')):
                raise ValidationError(_("Server URL must start with 'http://' or 'https://'"))
                
    def action_test_connection(self):
        self.ensure_one()
        try:
            response = self._make_api_request('session')
            if response.status_code == 200:
                self.connection_status = 'connected'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _("Connection successful!"),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                self.connection_status = 'error'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _("Connection failed: %s") % response.text,
                        'type': 'danger',
                        'sticky': False,
                    }
                }
        except Exception as e:
            self.connection_status = 'error'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("Connection failed: %s") % str(e),
                    'type': 'danger',
                    'sticky': False,
                }
            }
            
    def _make_api_request(self, endpoint, method='GET', data=None, params=None):
        self.ensure_one()
        
        if not endpoint:
            raise ValidationError(_("API endpoint is required"))
            
        url = f"{self.api_url}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        auth = (self.username, self.password)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, auth=auth, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, auth=auth, data=json.dumps(data) if data else None)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, auth=auth, data=json.dumps(data) if data else None)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, auth=auth)
            else:
                raise ValidationError(_("Unsupported method: %s") % method)
                
            return response
        except Exception as e:
            _logger.error("Error making API request to Traccar: %s", str(e))
            raise
            
    def action_sync_devices(self):
        self.ensure_one()
        try:
            response = self._make_api_request('devices')
            if response.status_code == 200:
                devices = response.json()
                created = 0
                updated = 0
                
                for device_data in devices:
                    existing_device = self.env['traccar.device'].search([
                        ('server_id', '=', self.id),
                        ('device_id', '=', device_data['id'])
                    ], limit=1)
                    
                    vals = {
                        'server_id': self.id,
                        'device_id': device_data['id'],
                        'name': device_data['name'],
                        'unique_id': device_data['uniqueId'],
                        'status': device_data.get('status'),
                        'last_update': fields.Datetime.now(),
                        'attributes': json.dumps(device_data.get('attributes', {})),
                    }
                    
                    if existing_device:
                        existing_device.write(vals)
                        updated += 1
                    else:
                        self.env['traccar.device'].create(vals)
                        created += 1
                
                self.last_sync_date = fields.Datetime.now()
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _("Synchronized %s devices (%s created, %s updated)") % (len(devices), created, updated),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _("Failed to sync devices: %s") % response.text,
                        'type': 'danger',
                        'sticky': False,
                    }
                }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("Failed to sync devices: %s") % str(e),
                    'type': 'danger',
                    'sticky': False,
                }
            }