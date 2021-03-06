# -*- coding: utf-8 -*-
import sys
import requests
import json

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

try:
    from odoo import models, fields, api
except:
    from openerp import models, fields, api

DEFAULT_URL = 'http://auth.atknit.com/app_auth/'
DEFAULT_TOKEN = '848e6b76-36c2-42ce-8819-6bc9b7c4bf4c'

class app_config(models.Model):
    _name = 'app.config'

    name = fields.Char(string=u"授权配置", default="授权配置", required=True, readonly=True)
    url = fields.Char(string=u"授权服务器地址", default=DEFAULT_URL, required=True, readonly=False)
    token = fields.Char(string=u"授权令牌", default=DEFAULT_TOKEN, required=True, readonly=False)
    key = fields.Text(string=u"授权密钥", required=False, readonly=True)
    expired_date = fields.Datetime(string=u"过期时间", required=False, readonly=True)
    message = fields.Text(string=u"同步结果", required=False, readonly=True)

    @api.one
    def action_update_key(self):
        full_url = self.url + '/' + self.token
        if self.url.endswith('/'):
            full_url = self.url + self.token

        res = requests.get(full_url)
        try:
            res = json.loads(res.text)
            if res.get('status') == 'success':
                self.key = res['key']
                self.expired_date = res['expired_date']
            self.message = res['message']
        except:
            self.message = u'系统错误'
        return True

    @api.model
    def update_auth_keys(self):
        records = self.search([])
        for record in records:
            record.action_update_key()
        return True

    @api.one
    def action_set_default(self):
        self.url = DEFAULT_URL
        self.token = DEFAULT_TOKEN
        self.key = ''
        self.message = ''
        self.action_update_key()
        return True

    @api.model
    def create(self, vals):
        config_item = super(app_config, self).create(vals)
        config_item.action_update_key()
        return config_item