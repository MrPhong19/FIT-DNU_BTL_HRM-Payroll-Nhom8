from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import ValidationError

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_va_ten'
    _order = 'ten asc, tuoi desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Thêm chatter

    #Thông tin cơ bản
    ma_dinh_danh = fields.Char("Mã định danh", required=True, tracking=True)
    ho_ten_dem = fields.Char("Họ tên đệm", required=True, tracking=True)
    ten = fields.Char("Tên", required=True, tracking=True)
    ho_va_ten = fields.Char("Họ và tên", compute="_compute_ho_va_ten", store=True)
    ngay_sinh = fields.Date("Ngày sinh", required=True)
    tuoi = fields.Integer("Tuổi", compute="_compute_tinh_tuoi", store=True)
    gioi_tinh = fields.Selection([
        ("Nam", "Nam"),
        ("Nữ", "Nữ")
    ], string="Giới tính", required=True, tracking=True)
    que_quan = fields.Char("Quê quán", required=True)
    email = fields.Char("Email", required=True)
    so_dien_thoai = fields.Char("Số điện thoại", required=True)
    anh = fields.Binary("Ảnh")

    #CCCD
    so_cccd = fields.Char("Số CCCD", required=True)
    ngay_cap_cccd = fields.Date("Ngày cấp CCCD")
    noi_cap_cccd = fields.Char("Nơi cấp CCCD")

    #Ngân hàng
    so_tai_khoan = fields.Char("Số tài khoản", tracking=True)
    ten_ngan_hang = fields.Char("Tên ngân hàng", tracking=True)
    chi_nhanh = fields.Char("Chi nhánh", tracking=True)
    chu_tai_khoan = fields.Char("Chủ tài khoản", tracking=True)

    #Công việc
    ngay_vao_lam = fields.Date("Ngày vào làm", tracking=True)
    tham_nien = fields.Integer(
        "Thâm niên (năm)",
        compute="_compute_tham_nien",
        store=True
    )
    he_so_luong = fields.Float(
        "Hệ số lương",
        default=1.0,
        tracking=True
    )
    luong_co_ban = fields.Float(
        "Lương cơ bản",
        default=0.0,
        tracking=True
    )
    trang_thai_lam_viec = fields.Selection([
        ('dang_lam', 'Đang làm việc'),
        ('nghi_viec', 'Nghỉ việc'),
        ('thai_san', 'Thai sản'),
        ('nghi_phep', 'Nghỉ phép dài hạn'),
        ('thu_viec', 'Thử việc'),
    ], string="Trạng thái làm việc",
        default='dang_lam',
        required=True,
        tracking=True
    )

    phong_ban_id = fields.Many2one(
        "phong_ban",
        string="Phòng ban",
        tracking=True
    )
    chuc_vu_id = fields.Many2one(
        "chuc_vu",
        string="Chức vụ",
        tracking=True
    )

    #Quan hệ
    lich_su_cong_tac_ids = fields.One2many(
        "lich_su_cong_tac",
        inverse_name="nhan_vien_id",
        string="Danh sách lịch sử công tác"
    )
    danh_sach_chung_chi_bang_cap_ids = fields.One2many(
        "danh_sach_chung_chi_bang_cap",
        inverse_name="nhan_vien_id",
        string="Danh sách chứng chỉ bằng cấp"
    )

    #COMPUTE
    @api.depends("ngay_sinh")
    def _compute_tinh_tuoi(self):
        today = date.today()
        for record in self:
            if record.ngay_sinh:
                # Tính tuổi chính xác theo ngày sinh
                record.tuoi = today.year - record.ngay_sinh.year - (
                    (today.month, today.day) < (record.ngay_sinh.month, record.ngay_sinh.day)
                )
            else:
                record.tuoi = 0

    @api.depends('ho_ten_dem', 'ten')
    def _compute_ho_va_ten(self):
        for record in self:
            record.ho_va_ten = (record.ho_ten_dem or '') + ' ' + (record.ten or '')

    @api.depends('ngay_vao_lam')
    def _compute_tham_nien(self):
        today = date.today()
        for record in self:
            if record.ngay_vao_lam:
                record.tham_nien = today.year - record.ngay_vao_lam.year - (
                    (today.month, today.day) < (record.ngay_vao_lam.month, record.ngay_vao_lam.day)
                )
            else:
                record.tham_nien = 0
    
    

    #VALIDATION
    @api.constrains("ngay_sinh")
    def _check_ngay_sinh(self):
        today = date.today()
        for record in self:
            if record.ngay_sinh and record.ngay_sinh > today:
                raise ValidationError("Ngày sinh không được lớn hơn ngày hiện tại!")

    @api.constrains("tuoi")
    def _check_tuoi(self):
        for record in self:
            if record.tuoi < 18:
                raise ValidationError("Tuổi không được nhỏ hơn 18!")

    @api.constrains("ngay_vao_lam")
    def _check_ngay_vao_lam(self):
        today = date.today()
        for record in self:
            if record.ngay_vao_lam and record.ngay_vao_lam > today:
                raise ValidationError("Ngày vào làm không được lớn hơn ngày hiện tại!")

    @api.constrains('so_cccd')
    def _check_so_cccd(self):
        for record in self:
            if record.so_cccd:
                if not record.so_cccd.isdigit():
                    raise ValidationError("Số CCCD chỉ được chứa chữ số!")
                if len(record.so_cccd) != 12:
                    raise ValidationError("Số CCCD phải có đúng 12 chữ số!")
                # Kiểm tra trùng CCCD
                duplicate = self.search([
                    ('so_cccd', '=', record.so_cccd),
                    ('id', '!=', record.id)
                ])
                if duplicate:
                    raise ValidationError(f"Số CCCD {record.so_cccd} đã tồn tại!")

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError("Email không hợp lệ!")
    
    # Smart button
    cham_cong_count = fields.Integer(
        "Số ngày chấm công",
        compute="_compute_cham_cong_count"
    )
    hop_dong_count = fields.Integer(
        "Số hợp đồng",
        compute="_compute_hop_dong_count"
    )
    khen_thuong_count = fields.Integer(
        "Số khen thưởng/kỷ luật",
        compute="_compute_khen_thuong_count"
    )

    def _compute_cham_cong_count(self):
        for record in self:
            record.cham_cong_count = self.env['bang_cham_cong'].search_count([
                ('nhan_vien_id', '=', record.id)
            ])

    def _compute_hop_dong_count(self):
        for record in self:
            record.hop_dong_count = self.env['hop_dong_lao_dong'].search_count([
                ('nhan_vien_id', '=', record.id)
            ])

    def _compute_khen_thuong_count(self):
        for record in self:
            record.khen_thuong_count = self.env['khen_thuong_ky_luat'].search_count([
                ('nhan_vien_id', '=', record.id)
            ])

    def action_view_cham_cong(self):
        return {
            'name': 'Chấm công',
            'type': 'ir.actions.act_window',
            'res_model': 'bang_cham_cong',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_id', '=', self.id)],
            'context': {'default_nhan_vien_id': self.id},
        }

    def action_view_hop_dong(self):
        return {
            'name': 'Hợp đồng lao động',
            'type': 'ir.actions.act_window',
            'res_model': 'hop_dong_lao_dong',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_id', '=', self.id)],
            'context': {'default_nhan_vien_id': self.id},
        }

    def action_view_khen_thuong(self):
        return {
            'name': 'Khen thưởng - Kỷ luật',
            'type': 'ir.actions.act_window',
            'res_model': 'khen_thuong_ky_luat',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_id', '=', self.id)],
            'context': {'default_nhan_vien_id': self.id},
        }

    bang_luong_count = fields.Integer(
        "Số bảng lương",
        compute="_compute_bang_luong_count"
    )

    don_tu_count = fields.Integer(
        "Số đơn từ",
        compute="_compute_don_tu_count"
    )

    def _compute_don_tu_count(self):
        for record in self:
            record.don_tu_count = self.env['don_tu'].search_count([
                ('nhan_vien_id', '=', record.id)
            ])

    def action_view_don_tu(self):
        return {
            'name': 'Đơn từ',
            'type': 'ir.actions.act_window',
            'res_model': 'don_tu',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_id', '=', self.id)],
            'context': {'default_nhan_vien_id': self.id},
        }

    def _compute_bang_luong_count(self):
        for record in self:
            record.bang_luong_count = self.env['bang_luong'].search_count([
                ('nhan_vien_id', '=', record.id)
            ])

    def action_view_bang_luong(self):
        return {
            'name': 'Bảng lương',
            'type': 'ir.actions.act_window',
            'res_model': 'bang_luong',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_id', '=', self.id)],
            'context': {'default_nhan_vien_id': self.id},
        }

    @api.model
    def create(self, vals):
        record = super(NhanVien, self).create(vals)
        if vals.get('phong_ban_id') and vals.get('chuc_vu_id'):
            self.env['lich_su_cong_tac'].create({
                'nhan_vien_id': record.id,
                'phong_ban_id': vals['phong_ban_id'],
                'chuc_vu_id': vals['chuc_vu_id'],
                'ngay_bat_dau': vals.get('ngay_vao_lam') or fields.Date.today(),
                'loai_chuc_vu': 'Chính',
                'trang_thai': 'Đang giữ',
            })
        return record

    def write(self, vals):
        for record in self:
            if vals.get('phong_ban_id') or vals.get('chuc_vu_id'):
                # Kết thúc lịch sử cũ
                lich_su_cu = self.env['lich_su_cong_tac'].search([
                    ('nhan_vien_id', '=', record.id),
                    ('loai_chuc_vu', '=', 'Chính'),
                    ('trang_thai', '=', 'Đang giữ'),
                ], limit=1)
                if lich_su_cu:
                    lich_su_cu.ngay_ket_thuc = fields.Date.today()
                # Tạo lịch sử mới
                self.env['lich_su_cong_tac'].create({
                    'nhan_vien_id': record.id,
                    'phong_ban_id': vals.get('phong_ban_id') or record.phong_ban_id.id,
                    'chuc_vu_id': vals.get('chuc_vu_id') or record.chuc_vu_id.id,
                    'ngay_bat_dau': fields.Date.today(),
                    'loai_chuc_vu': 'Chính',
                    'trang_thai': 'Đang giữ',
                })
        return super(NhanVien, self).write(vals)