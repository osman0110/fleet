from odoo import http
from odoo.http import request

class TestController(http.Controller):
    
    @http.route('/testr/info', type='http', auth='user', website=True)
    def test_info(self, **kw):
        # Use models from here, not the reverse direction to avoid circular imports
        records = request.env['testr.test'].sudo().search([])
        return request.render('testr.test_template', {
            'records': records,
        })