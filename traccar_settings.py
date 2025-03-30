from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class TraccarSettings(models.Model):
    _name = 'traccar.settings'
    _description = 'Traccar Integration Settings'
    
    name = fields.Char(string='Name', default='Traccar Settings', readonly=True)
    server_url = fields.Char(string='Traccar Server URL', 
                              help='e.g. https://traccar.example.com', required=True)
    api_key = fields.Char(string='API Key/Token', required=True)
    polling_interval = fields.Integer(string='Polling Interval (minutes)', default=5,
                                      help='Interval for fetching device data from Traccar')
    auto_create_devices = fields.Boolean(string='Auto-Create Devices', default=False,
                                         help='Automatically create devices from Traccar')
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    
    @api.model
    def get_settings(self):
        """Get or create Traccar settings"""
        settings = self.search([('company_id', '=', self.env.company.id)], limit=1)
        if not settings:
            settings = self.create({
                'name': 'Traccar Settings',
                'server_url': 'https://traccar.example.com',
                'api_key': 'demo_key',
                'company_id': self.env.company.id,
            })
        return settings
    
    def test_connection(self):
        """Test connection to Traccar server"""
        self.ensure_one()
        if not self.server_url or not self.api_key:
            raise UserError(_('Server URL and API Key must be configured'))
        
        try:
            url = f"{self.server_url}/api/server"
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                server_info = json.loads(response.text)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Successful'),
                