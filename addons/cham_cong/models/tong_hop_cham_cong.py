from odoo import models, fields, api
from datetime import date
import calendar
from odoo.exceptions import ValidationError

class TongHopChamCong(models.Model):
    _name = 'tong_hop_cham_cong'
    _description = 'Tổng hợp chấm công theo tháng'
    _rec_name = 'ten_tong_hop'
    _order = 'nam desc, thang desc, nhan_vien_id asc'

    #Thông tin cơ bản
    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string="Nhân viên",
        required=True
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
        required=True
    )
    nam = fields.Char("Năm", required=True)
    ten_tong_hop = fields.Char(
        "Tên tổng hợp",
        compute="_compute_ten_tong_hop",
        store=True
    )

    #Thống kê ngày công
    tong_ngay_cong = fields.Float("Tổng ngày công", compute="_compute_thong_ke", store=True)
    ngay_di_lam = fields.Integer("Ngày đi làm đúng giờ", compute="_compute_thong_ke", store=True)
    ngay_di_muon = fields.Integer("Ngày đi muộn", compute="_compute_thong_ke", store=True)
    ngay_ve_som = fields.Integer("Ngày về sớm", compute="_compute_thong_ke", store=True)
    ngay_di_muon_ve_som = fields.Integer("Ngày đi muộn và về sớm", compute="_compute_thong_ke", store=True)
    ngay_vang_mat = fields.Integer("Ngày vắng mặt", compute="_compute_thong_ke", store=True)
    ngay_vang_mat_co_phep = fields.Integer("Ngày vắng có phép", compute="_compute_thong_ke", store=True)

    #Thống kê vi phạm
    tong_phut_di_muon = fields.Float("Tổng phút đi muộn", compute="_compute_thong_ke", store=True)
    tong_phut_ve_som = fields.Float("Tổng phút về sớm", compute="_compute_thong_ke", store=True)

    #Trạng thái
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('da_chot', 'Đã chốt'),
    ], string="Trạng thái", default='nhap', required=True)

    #COMPUTE
    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_ten_tong_hop(self):
        for record in self:
            if record.nhan_vien_id and record.thang and record.nam:
                record.ten_tong_hop = f"{record.nhan_vien_id.ho_va_ten} - Tháng {record.thang}/{record.nam}"
            else:
                record.ten_tong_hop = ""

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_thong_ke(self):
        for record in self:
            if not record.nhan_vien_id or not record.thang or not record.nam:
                record.tong_ngay_cong = 0
                record.ngay_di_lam = 0
                record.ngay_di_muon = 0
                record.ngay_ve_som = 0
                record.ngay_di_muon_ve_som = 0
                record.ngay_vang_mat = 0
                record.ngay_vang_mat_co_phep = 0
                record.tong_phut_di_muon = 0
                record.tong_phut_ve_som = 0
                continue

            thang = int(record.thang)
            nam = int(record.nam)
            ngay_dau = date(nam, thang, 1)
            ngay_cuoi = date(nam, thang, calendar.monthrange(nam, thang)[1])

            #Lấy tất cả bản ghi chấm công trong tháng
            cham_cong_ids = self.env['bang_cham_cong'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('ngay_cham_cong', '>=', ngay_dau),
                ('ngay_cham_cong', '<=', ngay_cuoi),
            ])

            #Đếm theo trạng thái
            record.ngay_di_lam = len(cham_cong_ids.filtered(lambda x: x.trang_thai == 'di_lam'))
            record.ngay_di_muon = len(cham_cong_ids.filtered(lambda x: x.trang_thai == 'di_muon'))
            record.ngay_ve_som = len(cham_cong_ids.filtered(lambda x: x.trang_thai == 've_som'))
            record.ngay_di_muon_ve_som = len(cham_cong_ids.filtered(lambda x: x.trang_thai == 'di_muon_ve_som'))
            record.ngay_vang_mat = len(cham_cong_ids.filtered(lambda x: x.trang_thai == 'vang_mat'))
            record.ngay_vang_mat_co_phep = len(cham_cong_ids.filtered(lambda x: x.trang_thai == 'vang_mat_co_phep'))

            # Tổng ngày công (không tính vắng mặt không phép)
            record.tong_ngay_cong = len(cham_cong_ids.filtered(
                lambda x: x.trang_thai not in ['vang_mat']
            ))

            # Tổng phút vi phạm
            record.tong_phut_di_muon = sum(cham_cong_ids.mapped('phut_di_muon'))
            record.tong_phut_ve_som = sum(cham_cong_ids.mapped('phut_ve_som'))

    #VALIDATION
    @api.constrains('nhan_vien_id', 'thang', 'nam')
    def _check_trung_thang(self):
        for record in self:
            duplicate = self.search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('thang', '=', record.thang),
                ('nam', '=', record.nam),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError(
                    f"Đã tồn tại tổng hợp chấm công của {record.nhan_vien_id.ho_va_ten} "
                    f"tháng {record.thang}/{record.nam}!"
                )

    @api.constrains('nam')
    def _check_nam(self):
        for record in self:
            if record.nam and not record.nam.isdigit():
                raise ValidationError("Năm phải là số!")

    #ACTIONS
    def action_chot(self):
        for record in self:
            record.trang_thai = 'da_chot'
            # Tự động tạo bảng lương nếu chưa có
            bang_luong = self.env['bang_luong'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('thang', '=', record.thang),
                ('nam', '=', record.nam),
            ], limit=1)
            if not bang_luong:
                self.env['bang_luong'].create({
                    'nhan_vien_id': record.nhan_vien_id.id,
                    'thang': record.thang,
                    'nam': record.nam,
                    'tong_hop_cham_cong_id': record.id,
                })

    def action_mo_lai(self):
        for record in self:
            record.trang_thai = 'nhap'

    def action_tinh_lai(self):
        #Tính lại toàn bộ thôngs kê
        for record in self:
            record._compute_thong_ke()

    @api.model
    def action_tu_dong_tao_tong_hop(self):
        """Scheduled Action: chạy cuối tháng, tự động tạo tổng hợp chấm công"""
        from datetime import date
        today = date.today()
        # Lấy tháng hiện tại
        thang = str(today.month)
        nam = str(today.year)
        
        # Lấy tất cả nhân viên đang làm việc
        nhan_vien_list = self.env['nhan_vien'].search([
            ('trang_thai_lam_viec', '=', 'dang_lam')
        ])
        
        for nv in nhan_vien_list:
            # Kiểm tra đã có tổng hợp chưa
            existing = self.search([
                ('nhan_vien_id', '=', nv.id),
                ('thang', '=', thang),
                ('nam', '=', nam),
            ], limit=1)
            
            if not existing:
                self.create({
                    'nhan_vien_id': nv.id,
                    'thang': thang,
                    'nam': nam,
                })