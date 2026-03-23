from odoo import models, fields, api

class BangLuongLine(models.Model):
    _name = 'chi_tiet_bang_luong'
    _description = 'Chi tiết bảng lương'
    _rec_name = 'ten_khoan'

    bang_luong_id = fields.Many2one(
        'bang_luong',
        string="Bảng lương",
        required=True,
        ondelete='cascade'
    )
    ten_khoan = fields.Char("Tên khoản", required=True)
    loai = fields.Selection([
        ('cong', 'Cộng'),
        ('tru', 'Trừ'),
    ], string="Loại", required=True)
    so_tien = fields.Float("Số tiền", required=True, default=0.0)
    ghi_chu = fields.Char("Ghi chú")