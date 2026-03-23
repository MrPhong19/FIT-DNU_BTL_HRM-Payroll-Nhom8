from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class KhenThuongKyLuat(models.Model):
    _name = 'khen_thuong_ky_luat'
    _description = 'Khen thưởng - Kỷ luật'
    _rec_name = 'ma_quyet_dinh'
    _order = 'ngay_quyet_dinh desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #Thông tin cơ bản
    ma_quyet_dinh = fields.Char(
        "Mã quyết định",
        required=True,
        tracking=True
    )
    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string="Nhân viên",
        required=True,
        ondelete='cascade',
        tracking=True
    )
    loai = fields.Selection([
        ('khen_thuong', 'Khen thưởng'),
        ('ky_luat', 'Kỷ luật'),
    ], string="Loại", required=True, tracking=True)

    hinh_thuc = fields.Selection([
        # Khen thưởng
        ('thuong_tien', 'Thưởng tiền'),
        ('tang_bac_luong', 'Tăng bậc lương'),
        ('bang_khen', 'Bằng khen'),
        ('giay_khen', 'Giấy khen'),
        # Kỷ luật
        ('khien_trach', 'Khiển trách'),
        ('canh_cao', 'Cảnh cáo'),
        ('ha_bac_luong', 'Hạ bậc lương'),
        ('dinh_chi', 'Đình chỉ công tác'),
        ('sa_thai', 'Sa thải'),
    ], string="Hình thức", required=True, tracking=True)

    ngay_quyet_dinh = fields.Date(
        "Ngày quyết định",
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    ngay_hieu_luc = fields.Date(
        "Ngày hiệu lực",
        required=True,
        tracking=True
    )
    thang_ap_dung = fields.Selection(
        [(str(i), f'Tháng {i}') for i in range(1, 13)],
        string="Tháng áp dụng",
        required=True,
        tracking=True
    )
    nam_ap_dung = fields.Char(
        "Năm áp dụng",
        required=True,
        tracking=True
    )

    #Số tiền
    so_tien = fields.Float(
        "Số tiền",
        default=0.0,
        tracking=True,
        help="Số tiền thưởng hoặc phạt (VNĐ)"
    )
    ly_do = fields.Text("Lý do", required=True)
    ghi_chu = fields.Text("Ghi chú")

    #Trạng thái
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('tu_choi', 'Từ chối'),
    ], string="Trạng thái",
        default='nhap',
        required=True,
        tracking=True
    )
    nguoi_duyet_id = fields.Many2one(
        'nhan_vien',
        string="Người duyệt",
        tracking=True
    )
    ngay_duyet = fields.Date("Ngày duyệt", tracking=True)
    ly_do_tu_choi = fields.Text("Lý do từ chối")

    #Compute
    @api.depends('loai', 'so_tien')
    def _compute_so_tien_thuc(self):
        for record in self:
            if record.loai == 'khen_thuong':
                record.so_tien_thuc = record.so_tien
            else:
                record.so_tien_thuc = -record.so_tien

    so_tien_thuc = fields.Float(
        "Số tiền thực tế",
        compute="_compute_so_tien_thuc",
        store=True,
        help="Dương = thưởng, Âm = phạt"
    )

    #Validation
    @api.constrains('so_tien')
    def _check_so_tien(self):
        for record in self:
            if record.so_tien < 0:
                raise ValidationError("Số tiền không được âm!")

    @api.constrains('ngay_quyet_dinh', 'ngay_hieu_luc')
    def _check_ngay(self):
        for record in self:
            if record.ngay_quyet_dinh and record.ngay_hieu_luc:
                if record.ngay_hieu_luc < record.ngay_quyet_dinh:
                    raise ValidationError(
                        "Ngày hiệu lực không được nhỏ hơn ngày quyết định!"
                    )

    @api.constrains('ma_quyet_dinh')
    def _check_ma_quyet_dinh(self):
        for record in self:
            duplicate = self.search([
                ('ma_quyet_dinh', '=', record.ma_quyet_dinh),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError(
                    f"Mã quyết định {record.ma_quyet_dinh} đã tồn tại!"
                )

    @api.constrains('nam_ap_dung')
    def _check_nam_ap_dung(self):
        for record in self:
            if record.nam_ap_dung and not record.nam_ap_dung.isdigit():
                raise ValidationError("Năm áp dụng phải là số!")

    #Actions
    def action_gui_duyet(self):
        for record in self:
            if record.trang_thai == 'nhap':
                record.trang_thai = 'cho_duyet'

    def action_duyet(self):
        for record in self:
            if record.trang_thai == 'cho_duyet':
                record.trang_thai = 'da_duyet'
                record.ngay_duyet = date.today()
                record.nguoi_duyet_id = self.env.user.id

    def action_tu_choi(self):
        for record in self:
            if record.trang_thai == 'cho_duyet':
                record.trang_thai = 'tu_choi'