{
    'name': 'Fleet Traccar GPS Tracking',
    'version': '18.0.1.0.0',
    'category': 'Fleet',
    'summary': 'Integrate Traccar GPS tracking with Odoo Fleet Management',
    'description': """
Fleet Traccar GPS Tracking
==========================
This module integrates Traccar GPS tracking system with Odoo Fleet Management.

Features:
- Connect vehicles in Odoo with devices in Traccar
- View real-time vehicle positions on map
- Track vehicle routes, stops and trips
- Monitor fleet activity and generate reports
- Get notifications for speeding, geofence violations, etc.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'fleet',
        'base_setup',
        'mail',
        'web',
    ],
    'data': [
        'security/traccar_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/traccar_server_data.xml',
        'views/fleet_vehicle_views.xml',
        'views/traccar_device_views.xml',
        'views/traccar_server_views.xml',
        'views/traccar_event_views.xml',
        'views/traccar_position_views.xml',
        'views/traccar_geofence_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/traccar_device_wizard_views.xml',
        'menu/traccar_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fleet_traccar_tracking/static/src/js/traccar_map.js',
            'fleet_traccar_tracking/static/src/css/traccar_map.css',
        ],
        'web.assets_qweb': [
            'fleet_traccar_tracking/static/src/xml/traccar_templates.xml',
        ],
    },
    'external_dependencies': {
        'python': ['requests'],
    },
    'demo': [
        'demo/traccar_demo_data.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}