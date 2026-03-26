# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import urllib.request
import urllib.error


GROQ_API_KEY = "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"   #thay bằng key groq của bạn
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class ChatbotController(http.Controller):

    @http.route('/nhan_su/chatbot', type='json', auth='user')
    def chatbot(self, message, history=None):
        context = self._get_context()

        system_prompt = f"""Bạn là trợ lý AI của hệ thống quản lý nhân sự ERP.
Nhiệm vụ của bạn là trả lời các câu hỏi của quản lý/admin về thông tin nhân sự.
Hãy trả lời ngắn gọn, chính xác bằng tiếng Việt.
Chỉ trả lời dựa trên dữ liệu được cung cấp bên dưới.
Nếu không có thông tin, hãy nói rõ là không có dữ liệu.

=== DỮ LIỆU HỆ THỐNG ===
{context}
========================
"""

        messages = [{"role": "system", "content": system_prompt}]

        if history:
            for msg in history:
                messages.append({
                    "role": msg['role'] if msg['role'] != 'model' else 'assistant',
                    "content": msg['content']
                })

        messages.append({"role": "user", "content": message})

        payload = json.dumps({
            "model": "llama-3.1-8b-instant",
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 1000,
        }).encode('utf-8')

        req = urllib.request.Request(
            GROQ_URL,
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'User-Agent': 'Mozilla/5.0',
            },
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                answer = result['choices'][0]['message']['content']
                return {'success': True, 'answer': answer}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return {'success': False, 'answer': f'Lỗi API: {error_body}'}
        except Exception as e:
            return {'success': False, 'answer': f'Lỗi: {str(e)}'}

    def _get_context(self):
        from datetime import date
        today = date.today()
        thang = str(today.month)
        nam = str(today.year)

        # Danh sách nhân viên
        nhan_vien_list = request.env['nhan_vien'].search([])
        nv_data = []
        for nv in nhan_vien_list:
            nv_data.append(
                f"- {nv.ho_va_ten} | Phòng: {nv.phong_ban_id.ten_phong_ban if nv.phong_ban_id else 'Chưa có'} "
                f"| Chức vụ: {nv.chuc_vu_id.ten_chuc_vu if nv.chuc_vu_id else 'Chưa có'} "
                f"| Lương cơ bản: {nv.luong_co_ban:,.0f} VNĐ "
                f"| Trạng thái: {nv.trang_thai_lam_viec} "
                f"| SĐT: {nv.so_dien_thoai} | Email: {nv.email}"
            )

        # Tổng hợp chấm công tháng này
        tong_hop = request.env['tong_hop_cham_cong'].search([
            ('thang', '=', thang), ('nam', '=', nam)
        ])
        cc_data = []
        for th in tong_hop:
            cc_data.append(
                f"- {th.nhan_vien_id.ho_va_ten}: "
                f"Đi làm {th.ngay_di_lam} ngày, "
                f"Đi muộn {th.ngay_di_muon} ngày, "
                f"Vắng không phép {th.ngay_vang_mat} ngày, "
                f"Vắng có phép {th.ngay_vang_mat_co_phep} ngày, "
                f"Tổng phút muộn: {th.tong_phut_di_muon:.0f} phút"
            )

        # Bảng lương tháng này
        bang_luong = request.env['bang_luong'].search([
            ('thang', '=', thang), ('nam', '=', nam)
        ])
        bl_data = []
        tong_quy_luong = 0
        for bl in bang_luong:
            bl_data.append(
                f"- {bl.nhan_vien_id.ho_va_ten}: "
                f"Lương thực lãnh {bl.luong_thuc_lanh:,.0f} VNĐ "
                f"| Trạng thái: {bl.trang_thai}"
            )
            tong_quy_luong += bl.luong_thuc_lanh

        context = f"""
NGÀY HÔM NAY: {today.strftime('%d/%m/%Y')}
THÁNG HIỆN TẠI: {thang}/{nam}

DANH SÁCH NHÂN VIÊN ({len(nhan_vien_list)} người):
{chr(10).join(nv_data) if nv_data else 'Chưa có dữ liệu'}

CHẤM CÔNG THÁNG {thang}/{nam}:
{chr(10).join(cc_data) if cc_data else 'Chưa có dữ liệu'}

BẢNG LƯƠNG THÁNG {thang}/{nam}:
{chr(10).join(bl_data) if bl_data else 'Chưa có dữ liệu'}
TỔNG QUỸ LƯƠNG: {tong_quy_luong:,.0f} VNĐ
"""
        return context