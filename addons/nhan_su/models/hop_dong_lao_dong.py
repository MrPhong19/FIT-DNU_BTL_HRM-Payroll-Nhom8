from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError
import urllib.request
import urllib.error
import json

TELEGRAM_TOKEN = "8749957174:AAHP6B8f1DwaP-1RRiqEkkUHDMRtXnAqf74" #thay bằng token bot của bạn
TELEGRAM_CHAT_ID = "7059709523" #thay bằng chat id của bạn

class HopDongLaoDong(models.Model):
    _name = 'hop_dong_lao_dong'
    _description = 'Hợp đồng lao động'
    _rec_name = 'ma_hop_dong'
    _order = 'ngay_ky desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #Thông tin cơ bản
    ma_hop_dong = fields.Char("Mã hợp đồng", required=True, tracking=True)
    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string="Nhân viên",
        required=True,
        ondelete='cascade',
        tracking=True
    )
    loai_hop_dong = fields.Selection([
        ('thu_viec', 'Thử việc'),
        ('chinh_thuc', 'Chính thức'),
        ('thoi_vu', 'Thời vụ'),
        ('part_time', 'Bán thời gian'),
    ], string="Loại hợp đồng", required=True, tracking=True)

    ngay_ky = fields.Date("Ngày ký", required=True, tracking=True)
    ngay_bat_dau = fields.Date("Ngày bắt đầu", required=True, tracking=True)
    ngay_ket_thuc = fields.Date("Ngày kết thúc", tracking=True)
    
    #Lương trong HĐ
    luong_co_ban = fields.Float("Lương cơ bản", required=True, tracking=True)
    he_so_luong = fields.Float("Hệ số lương", default=1.0, tracking=True)
    phu_cap = fields.Float("Phụ cấp", default=0.0)
    
    #Trạng thái
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('hieu_luc', 'Có hiệu lực'),
        ('sap_het_han', 'Sắp hết hạn'),
        ('het_han', 'Hết hạn'),
        ('huy', 'Đã hủy'),
    ], string="Trạng thái",
        compute="_compute_trang_thai",
        store=True,
        tracking=True
    )
    
    so_ngay_canh_bao = fields.Integer(
        "Cảnh báo trước (ngày)",
        default=30,
        help="Số ngày trước khi hết hạn sẽ cảnh báo"
    )
    ghi_chu = fields.Text("Ghi chú")

    #COMPUTE
    @api.depends('ngay_bat_dau', 'ngay_ket_thuc', 'so_ngay_canh_bao')
    def _compute_trang_thai(self):
        today = date.today()
        for record in self:
            if not record.ngay_bat_dau:
                record.trang_thai = 'nhap'
                continue
            if today < record.ngay_bat_dau:
                record.trang_thai = 'nhap'
            elif not record.ngay_ket_thuc:
                # Hợp đồng không thời hạn
                record.trang_thai = 'hieu_luc'
            else:
                days_left = (record.ngay_ket_thuc - today).days
                if days_left < 0:
                    record.trang_thai = 'het_han'
                elif days_left <= record.so_ngay_canh_bao:
                    record.trang_thai = 'sap_het_han'
                else:
                    record.trang_thai = 'hieu_luc'

    @api.depends('ngay_ket_thuc')
    def _compute_so_ngay_con_lai(self):
        today = date.today()
        for record in self:
            if record.ngay_ket_thuc:
                delta = (record.ngay_ket_thuc - today).days
                record.so_ngay_con_lai = max(0, delta)
            else:
                record.so_ngay_con_lai = 0

    so_ngay_con_lai = fields.Integer(
        "Số ngày còn lại",
        compute="_compute_so_ngay_con_lai",
        store=True
    )

    #Validation
    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc')
    def _check_ngay(self):
        for record in self:
            if record.ngay_ket_thuc and record.ngay_bat_dau:
                if record.ngay_ket_thuc < record.ngay_bat_dau:
                    raise ValidationError(
                        "Ngày kết thúc không được nhỏ hơn ngày bắt đầu!"
                    )

    @api.constrains('ngay_ky', 'ngay_bat_dau')
    def _check_ngay_ky(self):
        for record in self:
            if record.ngay_ky and record.ngay_bat_dau:
                if record.ngay_ky > record.ngay_bat_dau:
                    raise ValidationError(
                        "Ngày ký không được lớn hơn ngày bắt đầu hợp đồng!"
                    )

    @api.constrains('luong_co_ban')
    def _check_luong(self):
        for record in self:
            if record.luong_co_ban < 0:
                raise ValidationError("Lương cơ bản không được âm!")

    @api.constrains('ma_hop_dong')
    def _check_ma_hop_dong(self):
        for record in self:
            duplicate = self.search([
                ('ma_hop_dong', '=', record.ma_hop_dong),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError(
                    f"Mã hợp đồng {record.ma_hop_dong} đã tồn tại!"
                )

    #Actions
    def action_huy_hop_dong(self):
        for record in self:
            record.trang_thai = 'huy'

    def action_gia_han(self):
        """Mở wizard gia hạn hợp đồng"""
        return {
            'name': 'Gia hạn hợp đồng',
            'type': 'ir.actions.act_window',
            'res_model': 'hop_dong_lao_dong',
            'view_mode': 'form',
            'target': 'new',
        }
    

    def _gui_telegram(self, message):
        try:
            import urllib.request
            import json
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = json.dumps({
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }).encode('utf-8')
            req = urllib.request.Request(
                url, data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200
        except Exception:
            return False

    @api.model
    def action_cap_nhat_trang_thai_tat_ca(self):
        hop_dong_list = self.search([('trang_thai', 'not in', ['huy'])])
        hop_dong_list._compute_trang_thai()

        # Gửi thông báo hợp đồng sắp hết hạn
        sap_het_han = self.search([('trang_thai', '=', 'sap_het_han')])
        if sap_het_han:
            lines = []
            for hd in sap_het_han:
                lines.append(
                    f"👤 <b>{hd.nhan_vien_id.ho_va_ten}</b>\n"
                    f"   📋 HĐ: {hd.ma_hop_dong} | Loại: {hd.loai_hop_dong}\n"
                    f"   ⏰ Hết hạn: {hd.ngay_ket_thuc.strftime('%d/%m/%Y')} "
                    f"(còn {hd.so_ngay_con_lai} ngày)"
                )
            message = (
                f"⚠️ <b>CẢNH BÁO HỢP ĐỒNG SẮP HẾT HẠN</b>\n"
                f"📅 Ngày: {date.today().strftime('%d/%m/%Y')}\n"
                f"📊 Số hợp đồng: {len(sap_het_han)}\n\n"
                + "\n\n".join(lines)
            )
            self._gui_telegram(message)