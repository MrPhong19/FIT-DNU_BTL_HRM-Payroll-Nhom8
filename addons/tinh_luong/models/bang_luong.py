from odoo import models, fields, api
from datetime import date
import calendar
from odoo.exceptions import ValidationError

class BangLuong(models.Model):
    _name = 'bang_luong'
    _description = 'Bảng lương'
    _rec_name = 'ten_bang_luong'
    _order = 'nam desc, thang desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #Thông tin cơ bản
    ten_bang_luong = fields.Char(
        "Tên bảng lương",
        compute="_compute_ten_bang_luong",
        store=True
    )
    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string="Nhân viên",
        required=True,
        tracking=True
    )
    phong_ban_id = fields.Many2one(
        'phong_ban',
        string="Phòng ban",
        related='nhan_vien_id.phong_ban_id',
        store=True
    )
    thang = fields.Selection(
        [(str(i), f'Tháng {i}') for i in range(1, 13)],
        string="Tháng",
        required=True,
        tracking=True
    )
    nam = fields.Char("Năm", required=True, tracking=True)

    #Dữ liệu từ nhân sự
    luong_co_ban = fields.Float(
        "Lương cơ bản",
        related='nhan_vien_id.luong_co_ban',
        store=True
    )
    he_so_luong = fields.Float(
        "Hệ số lương",
        related='nhan_vien_id.he_so_luong',
        store=True
    )
    tham_nien = fields.Integer(
        "Thâm niên (năm)",
        related='nhan_vien_id.tham_nien',
        store=True
    )

    #Dữ liệu chấm công
    tong_hop_cham_cong_id = fields.Many2one(
        'tong_hop_cham_cong',
        string="Tổng hợp chấm công",
        tracking=True
    )
    tong_ngay_cong = fields.Float(
        "Tổng ngày công",
        related='tong_hop_cham_cong_id.tong_ngay_cong',
        store=True
    )
    tong_phut_di_muon = fields.Float(
        "Tổng phút đi muộn",
        related='tong_hop_cham_cong_id.tong_phut_di_muon',
        store=True
    )
    tong_phut_ve_som = fields.Float(
        "Tổng phút về sớm",
        related='tong_hop_cham_cong_id.tong_phut_ve_som',
        store=True
    )

    #Khen thưởng/kỹ luật
    tong_thuong = fields.Float(
        "Tổng thưởng",
        compute="_compute_khen_thuong_ky_luat",
        store=True
    )
    tong_phat = fields.Float(
        "Tổng phạt",
        compute="_compute_khen_thuong_ky_luat",
        store=True
    )

    #Chi tiết lương
    line_ids = fields.One2many(
        'chi_tiet_bang_luong',
        'bang_luong_id',
        string="Chi tiết lương"
    )

    #Tính toán
    tien_phat_di_muon = fields.Float(
        "Tiền phạt đi muộn/về sớm",
        compute="_compute_tien_phat",
        store=True
    )
    thuong_tham_nien = fields.Float(
        "Thưởng thâm niên",
        compute="_compute_thuong_tham_nien",
        store=True
    )
    luong_thuc_lanh = fields.Float(
        "Lương thực lãnh",
        compute="_compute_luong_thuc_lanh",
        store=True,
        tracking=True
    )

    #Trạng thái
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('da_thanh_toan', 'Đã thanh toán'),
    ], string="Trạng thái",
        default='nhap',
        required=True,
        tracking=True
    )
    nguoi_duyet_id = fields.Many2one('nhan_vien', string="Người duyệt", tracking=True)
    ngay_duyet = fields.Date("Ngày duyệt", tracking=True)

    #Thông tin ngân hàng
    so_tai_khoan = fields.Char(
        "Số tài khoản",
        related='nhan_vien_id.so_tai_khoan',
        store=True
    )
    ten_ngan_hang = fields.Char(
        "Ngân hàng",
        related='nhan_vien_id.ten_ngan_hang',
        store=True
    )
    chi_nhanh = fields.Char(
        "Chi nhánh",
        related='nhan_vien_id.chi_nhanh',
        store=True
    )
    chu_tai_khoan = fields.Char(
        "Chủ tài khoản",
        related='nhan_vien_id.chu_tai_khoan',
        store=True
    )

    #COMPUTE
    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_ten_bang_luong(self):
        for record in self:
            if record.nhan_vien_id and record.thang and record.nam:
                record.ten_bang_luong = f"{record.nhan_vien_id.ho_va_ten} - Tháng {record.thang}/{record.nam}"
            else:
                record.ten_bang_luong = ""

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_khen_thuong_ky_luat(self):
        for record in self:
            if not record.nhan_vien_id or not record.thang or not record.nam:
                record.tong_thuong = 0
                record.tong_phat = 0
                continue
            ktk = self.env['khen_thuong_ky_luat'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('thang_ap_dung', '=', record.thang),
                ('nam_ap_dung', '=', record.nam),
                ('trang_thai', '=', 'da_duyet'),
            ])
            record.tong_thuong = sum(
                ktk.filtered(lambda x: x.loai == 'khen_thuong').mapped('so_tien')
            )
            record.tong_phat = sum(
                ktk.filtered(lambda x: x.loai == 'ky_luat').mapped('so_tien')
            )

    @api.depends('tong_phut_di_muon', 'tong_phut_ve_som', 'luong_co_ban')
    def _compute_tien_phat(self):
        for record in self:
            #Quy đổi: 1 phút muộn/về sớm = lương cơ bản / (26 ngày * 8 giờ * 60 phút)
            if record.luong_co_ban > 0:
                luong_moi_phut = record.luong_co_ban / (26 * 8 * 60)
                tong_phut = record.tong_phut_di_muon + record.tong_phut_ve_som
                record.tien_phat_di_muon = luong_moi_phut * tong_phut
            else:
                record.tien_phat_di_muon = 0

    @api.depends('tham_nien', 'luong_co_ban')
    def _compute_thuong_tham_nien(self):
        for record in self:
            #Thưởng thâm niên: mỗi năm thêm 1% lương cơ bản, tối đa 20%
            if record.tham_nien > 0 and record.luong_co_ban > 0:
                phan_tram = min(record.tham_nien * 1, 20)
                record.thuong_tham_nien = record.luong_co_ban * phan_tram / 100
            else:
                record.thuong_tham_nien = 0

    @api.depends('line_ids', 'line_ids.loai', 'line_ids.so_tien',
             'luong_co_ban', 'he_so_luong', 'tien_phat_di_muon',
             'tong_thuong', 'tong_phat', 'thuong_tham_nien',
             'tong_ngay_cong')
    def _compute_luong_thuc_lanh(self):
        SO_NGAY_CONG_CHUAN = 26  # Số ngày công chuẩn trong tháng
        for record in self:
            # Nếu chưa có chấm công thì lương = 0
            if not record.tong_hop_cham_cong_id or record.tong_ngay_cong <= 0:
                record.luong_thuc_lanh = 0
                continue

            # Lương theo ngày công thực tế
            luong_theo_ngay = (record.luong_co_ban * record.he_so_luong / SO_NGAY_CONG_CHUAN) * record.tong_ngay_cong

            # Cộng từ line_ids
            tong_cong = sum(record.line_ids.filtered(
                lambda x: x.loai == 'cong').mapped('so_tien'))
            tong_tru = sum(record.line_ids.filtered(
                lambda x: x.loai == 'tru').mapped('so_tien'))

            record.luong_thuc_lanh = (
                luong_theo_ngay
                + record.thuong_tham_nien
                + record.tong_thuong
                + tong_cong
                - record.tien_phat_di_muon
                - record.tong_phat
                - tong_tru
            )

    #VALIDATION
    _sql_constraints = [
        ('unique_nhan_vien_thang_nam',
         'UNIQUE(nhan_vien_id, thang, nam)',
         'Đã tồn tại bảng lương cho nhân viên này trong tháng!')
    ]

    @api.constrains('nam')
    def _check_nam(self):
        for record in self:
            if record.nam and not record.nam.isdigit():
                raise ValidationError("Năm phải là số!")

    #ACTIONS
    def action_tinh_luong(self):
        """Tự động tính lương từ chấm công và nhân sự"""
        for record in self:
            if record.trang_thai != 'nhap':
                raise ValidationError("Chỉ có thể tính lại khi ở trạng thái Nháp!")

            #Tìm tổng hợp chấm công
            tong_hop = self.env['tong_hop_cham_cong'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('thang', '=', record.thang),
                ('nam', '=', record.nam),
            ], limit=1)
            if tong_hop:
                record.tong_hop_cham_cong_id = tong_hop.id

            #Xóa line cũ và tạo lại
            record.line_ids.unlink()

            lines = []
            #Lương cơ bản
            lines.append({
                'ten_khoan': 'Lương cơ bản',
                'loai': 'cong',
                'so_tien': record.luong_co_ban * record.he_so_luong,
                'ghi_chu': f'Lương cơ bản x Hệ số {record.he_so_luong}'
            })
            #Thưởng thâm niên
            if record.thuong_tham_nien > 0:
                lines.append({
                    'ten_khoan': 'Thưởng thâm niên',
                    'loai': 'cong',
                    'so_tien': record.thuong_tham_nien,
                    'ghi_chu': f'Thâm niên {record.tham_nien} năm'
                })
            #Khen thưởng
            if record.tong_thuong > 0:
                lines.append({
                    'ten_khoan': 'Khen thưởng',
                    'loai': 'cong',
                    'so_tien': record.tong_thuong,
                    'ghi_chu': 'Từ quyết định khen thưởng'
                })
            #Phạt đi muộn/về sớm
            if record.tien_phat_di_muon > 0:
                lines.append({
                    'ten_khoan': 'Phạt đi muộn/về sớm',
                    'loai': 'tru',
                    'so_tien': record.tien_phat_di_muon,
                    'ghi_chu': f'{record.tong_phut_di_muon + record.tong_phut_ve_som:.0f} phút'
                })
            #Kỷ luật
            if record.tong_phat > 0:
                lines.append({
                    'ten_khoan': 'Kỷ luật',
                    'loai': 'tru',
                    'so_tien': record.tong_phat,
                    'ghi_chu': 'Từ quyết định kỷ luật'
                })

            for line in lines:
                line['bang_luong_id'] = record.id
                self.env['chi_tiet_bang_luong'].create(line)

    def action_gui_duyet(self):
        for record in self:
            if record.trang_thai == 'nhap':
                record.trang_thai = 'cho_duyet'

    def action_duyet(self):
        for record in self:
            if record.trang_thai == 'cho_duyet':
                record.trang_thai = 'da_duyet'
                record.ngay_duyet = date.today()

    def action_thanh_toan(self):
        for record in self:
            if record.trang_thai == 'da_duyet':
                record.trang_thai = 'da_thanh_toan'

    def action_huy(self):
        for record in self:
            if record.trang_thai in ['nhap', 'cho_duyet']:
                record.trang_thai = 'nhap'