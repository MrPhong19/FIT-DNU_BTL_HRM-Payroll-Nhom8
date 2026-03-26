# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import date


class DashboardNhanSu(http.Controller):

    @http.route('/nhan_su/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self):
        today = date.today()
        thang = str(today.month)
        nam = str(today.year)
        ngay_hom_nay = today.strftime('%Y-%m-%d')

        tong_nv = request.env['nhan_vien'].search_count([
            ('trang_thai_lam_viec', '=', 'dang_lam')
        ])
        thu_viec = request.env['nhan_vien'].search_count([
            ('trang_thai_lam_viec', '=', 'thu_viec')
        ])
        nghi_viec = request.env['nhan_vien'].search_count([
            ('trang_thai_lam_viec', '=', 'nghi_viec')
        ])
        sap_het_han = request.env['hop_dong_lao_dong'].search_count([
            ('trang_thai', '=', 'sap_het_han')
        ])
        khen_thuong = request.env['khen_thuong_ky_luat'].search_count([
            ('loai', '=', 'khen_thuong'),
            ('thang_ap_dung', '=', thang),
            ('nam_ap_dung', '=', nam),
            ('trang_thai', '=', 'da_duyet'),
        ])
        ky_luat = request.env['khen_thuong_ky_luat'].search_count([
            ('loai', '=', 'ky_luat'),
            ('thang_ap_dung', '=', thang),
            ('nam_ap_dung', '=', nam),
            ('trang_thai', '=', 'da_duyet'),
        ])

        # Nhân viên theo phòng ban
        phong_ban_list = request.env['phong_ban'].search([])
        labels = []
        values = []
        for pb in phong_ban_list:
            count = request.env['nhan_vien'].search_count([
                ('phong_ban_id', '=', pb.id),
                ('trang_thai_lam_viec', '=', 'dang_lam')
            ])
            if count > 0:
                labels.append(pb.ten_phong_ban)
                values.append(count)

        # Chấm công hôm nay
        cc_hom_nay = request.env['bang_cham_cong'].search([
            ('ngay_cham_cong', '=', ngay_hom_nay)
        ])
        hom_nay_di_lam = len(cc_hom_nay.filtered(lambda x: x.trang_thai == 'di_lam'))
        hom_nay_di_muon = len(cc_hom_nay.filtered(lambda x: x.trang_thai in ['di_muon', 'di_muon_ve_som']))
        hom_nay_vang_mat = len(cc_hom_nay.filtered(lambda x: x.trang_thai == 'vang_mat'))
        hom_nay_co_phep = len(cc_hom_nay.filtered(lambda x: x.trang_thai == 'vang_mat_co_phep'))

        # Tổng kết tháng
        tong_hop = request.env['tong_hop_cham_cong'].search([
            ('thang', '=', thang),
            ('nam', '=', nam),
        ])
        nv_di_muon = len(tong_hop.filtered(lambda x: x.ngay_di_muon > 0))
        nv_vang_mat = len(tong_hop.filtered(lambda x: x.ngay_vang_mat > 0))
        nv_chua_chot = len(tong_hop.filtered(lambda x: x.trang_thai == 'nhap'))
        tong_phut_muon = sum(tong_hop.mapped('tong_phut_di_muon'))
        tb_phut_muon = round(tong_phut_muon / len(tong_hop), 1) if tong_hop else 0

        return {
            'tong_nv': tong_nv,
            'thu_viec': thu_viec,
            'nghi_viec': nghi_viec,
            'sap_het_han': sap_het_han,
            'khen_thuong': khen_thuong,
            'ky_luat': ky_luat,
            'chart_labels': labels,
            'chart_values': values,
            'thang_hien_tai': f'{thang}/{nam}',
            'ngay_hom_nay': today.strftime('%d/%m/%Y'),
            'hom_nay_di_lam': hom_nay_di_lam,
            'hom_nay_di_muon': hom_nay_di_muon,
            'hom_nay_vang_mat': hom_nay_vang_mat,
            'hom_nay_co_phep': hom_nay_co_phep,
            'nv_di_muon': nv_di_muon,
            'nv_vang_mat': nv_vang_mat,
            'nv_chua_chot': nv_chua_chot,
            'tb_phut_muon': tb_phut_muon,
            'tong_nv_cham_cong': len(tong_hop),
        }