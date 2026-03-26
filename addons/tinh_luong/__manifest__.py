{
    'name': "Tính lương",
    'summary': "Quản lý tính lương nhân viên",
    'description': "Module tính lương tự động dựa trên chấm công và hồ sơ nhân sự",
    'author': "Nhóm 8",
    'category': 'Human Resources',
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'nhan_su', 'cham_cong'],
    'data': [
        'security/ir.model.access.csv',
        'views/bang_luong.xml',
        'views/dashboard.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'tinh_luong/static/src/js/dashboard.js',
        ],
    },
}