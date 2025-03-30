# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    traccar_url = fields.Char(string='Traccar Server URL', config_parameter='fleet_traccar_tracking.traccar_url')
    traccar_api_key = fields.Char(string='Traccar API Key', config_parameter='fleet_traccar_tracking.traccar_api_key')
    traccar_username = fields.Char(string='Traccar Username', config_parameter='fleet_traccar_tracking.traccar_username')
    traccar_password = fields.Char(string='Traccar Password', config_parameter='fleet_traccar_tracking.traccar_password')
    track_interval = fields.Integer(string='Tracking Interval (minutes)', config_parameter='fleet_traccar_tracking.track_interval', default=15)
    history_period = fields.Integer(string='History Period (days)', config_parameter='fleet_traccar_tracking.history_period', default=7)