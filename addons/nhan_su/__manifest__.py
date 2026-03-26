# -*- coding: utf-8 -*-
{
    'name': "nhan_su",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    'depends': ['base', 'mail'],

    'data': [
        'security/ir.model.access.csv',
        'data/scheduled_actions.xml',
        'views/nhan_vien.xml',
        'views/phong_ban.xml',
        'views/chuc_vu.xml',
        'views/lich_su_cong_tac.xml',
        'views/chung_chi_bang_cap.xml',
        'views/danh_sach_chung_chi_bang_cap.xml',
        'views/hop_dong_lao_dong.xml',
        'views/khen_thuong_ky_luat.xml',
        'views/dashboard.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'nhan_su/static/src/js/dashboard.js',
            'nhan_su/static/src/js/chatbot.js',
        ],
    },
}