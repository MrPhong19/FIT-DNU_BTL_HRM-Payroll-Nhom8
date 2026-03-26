# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import date


class DashboardTinhLuong(http.Controller):

    @http.route('/tinh_luong/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self):
        today = date.today()
        thang = str(today.month)
        nam = str(today.year)

        # Thống kê bảng lương tháng này
        cho_duyet = request.env['bang_luong'].search_count([
            ('thang', '=', thang), ('nam', '=', nam),
            ('trang_thai', '=', 'cho_duyet'),
        ])
        da_duyet = request.env['bang_luong'].search_count([
            ('thang', '=', thang), ('nam', '=', nam),
            ('trang_thai', '=', 'da_duyet'),
        ])
        da_thanh_toan = request.env['bang_luong'].search_count([
            ('thang', '=', thang), ('nam', '=', nam),
            ('trang_thai', '=', 'da_thanh_toan'),
        ])
        nhap = request.env['bang_luong'].search_count([
            ('thang', '=', thang), ('nam', '=', nam),
            ('trang_thai', '=', 'nhap'),
        ])

        # Tổng quỹ lương tháng này
        bang_luong_thang = request.env['bang_luong'].search([
            ('thang', '=', thang), ('nam', '=', nam),
            ('trang_thai', 'in', ['da_duyet', 'da_thanh_toan']),
        ])
        tong_quy_luong = sum(bang_luong_thang.mapped('luong_thuc_lanh'))
        luong_cao_nhat = max(bang_luong_thang.mapped('luong_thuc_lanh'), default=0)
        luong_thap_nhat = min(
            [x for x in bang_luong_thang.mapped('luong_thuc_lanh') if x > 0], default=0
        )

        # Lương theo phòng ban
        phong_ban_list = request.env['phong_ban'].search([])
        pb_labels = []
        pb_values = []
        for pb in phong_ban_list:
            bl = request.env['bang_luong'].search([
                ('thang', '=', thang), ('nam', '=', nam),
                ('phong_ban_id', '=', pb.id),
                ('trang_thai', 'in', ['da_duyet', 'da_thanh_toan']),
            ])
            if bl:
                pb_labels.append(pb.ten_phong_ban)
                pb_values.append(round(sum(bl.mapped('luong_thuc_lanh'))))

        # Lương 6 tháng gần nhất
        theo_thang_labels = []
        theo_thang_values = []
        for i in range(5, -1, -1):
            t = today.month - i
            y = today.year
            if t <= 0:
                t += 12
                y -= 1
            bl = request.env['bang_luong'].search([
                ('thang', '=', str(t)), ('nam', '=', str(y)),
                ('trang_thai', 'in', ['da_duyet', 'da_thanh_toan']),
            ])
            theo_thang_labels.append(f'{t}/{y}')
            theo_thang_values.append(round(sum(bl.mapped('luong_thuc_lanh'))))

        return {
            'thang_hien_tai': f'{thang}/{nam}',
            'cho_duyet': cho_duyet,
            'da_duyet': da_duyet,
            'da_thanh_toan': da_thanh_toan,
            'nhap': nhap,
            'tong_quy_luong': f"{tong_quy_luong:,.0f}",
            'luong_cao_nhat': f"{luong_cao_nhat:,.0f}",
            'luong_thap_nhat': f"{luong_thap_nhat:,.0f}",
            'pb_labels': pb_labels,
            'pb_values': pb_values,
            'theo_thang_labels': theo_thang_labels,
            'theo_thang_values': theo_thang_values,
        }