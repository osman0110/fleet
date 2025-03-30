from odoo import models, fields, api, _
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class TraccarPosition(models.Model):
    _name = 'traccar.position'
    _description = 'Traccar Position'
    _order = 'fix_time DESC, id DESC'
    
    device_id = fields.Many2one('traccar.device', string='Device', required=True, ondelete='cascade')
    position_id = fields.Integer('Position ID', required=True)
    
    # Position information
    protocol = fields.Char('Protocol')
    server_time = fields.Datetime('Server Time')
    device_time = fields.Datetime('Device Time')
    fix_time = fields.Datetime('Fix Time')
    
    # Geographic coordinates
    latitude = fields.Float('Latitude', digits=(16, 8 