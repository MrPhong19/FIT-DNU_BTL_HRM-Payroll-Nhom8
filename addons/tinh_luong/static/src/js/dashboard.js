odoo.define('tinh_luong.dashboard', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');

    var TinhLuongDashboard = AbstractAction.extend({

        start: function () {
            var self = this;
            return rpc.query({
                route: '/tinh_luong/dashboard_data',
            }).then(function (data) {
                self._renderDashboard(data);
            });
        },

        _renderDashboard: function (data) {
            var html = `
                <div style="padding:20px; font-family:sans-serif; background:#f8f8f8; min-height:100vh;">

                    <!-- Tiêu đề -->
                    <div style="margin-bottom:20px;">
                        <h2 style="color:#875A7B; margin:0; font-size:22px;">
                            <i class="fa fa-money"></i> Dashboard Tính lương
                        </h2>
                        <p style="color:#999; margin:4px 0 0; font-size:13px;">Tháng ${data.thang_hien_tai}</p>
                    </div>

                    <!-- KPI Cards hàng 1 -->
                    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:12px;">
                        ${this._kpiCard('fa-pencil', data.nhap, 'Nháp', '#888888')}
                        ${this._kpiCard('fa-clock-o', data.cho_duyet, 'Chờ duyệt', '#BA7517')}
                        ${this._kpiCard('fa-check', data.da_duyet, 'Đã duyệt', '#378ADD')}
                        ${this._kpiCard('fa-check-circle', data.da_thanh_toan, 'Đã thanh toán', '#639922')}
                    </div>

                    <!-- KPI Cards hàng 2 - Quỹ lương -->
                    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:20px;">
                        ${this._kpiCard('fa-money', data.tong_quy_luong + ' ₫', 'Tổng quỹ lương', '#534AB7')}
                        ${this._kpiCard('fa-arrow-up', data.luong_cao_nhat + ' ₫', 'Lương cao nhất', '#1D9E75')}
                        ${this._kpiCard('fa-arrow-down', data.luong_thap_nhat + ' ₫', 'Lương thấp nhất', '#E24B4A')}
                    </div>

                    <!-- Chart theo phòng ban + Bảng 6 tháng -->
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">

                        <!-- Chart quỹ lương theo phòng ban -->
                        <div style="background:white; border-radius:8px; padding:16px;
                                    border:0.5px solid #e0e0e0;">
                            <h5 style="margin:0 0 14px; color:#555; font-size:14px; font-weight:500;">
                                <i class="fa fa-bar-chart" style="color:#875A7B;"></i>
                                Quỹ lương theo phòng ban (VNĐ)
                            </h5>
                            <div id="chartPhongBan"></div>
                        </div>

                        <!-- Bảng lương 6 tháng -->
                        <div style="background:white; border-radius:8px; padding:16px;
                                    border:0.5px solid #e0e0e0;">
                            <h5 style="margin:0 0 14px; color:#555; font-size:14px; font-weight:500;">
                                <i class="fa fa-table" style="color:#875A7B;"></i>
                                Quỹ lương 6 tháng gần nhất
                            </h5>
                            <div id="chartTheoThang"></div>
                        </div>

                    </div>
                </div>
            `;
            this.$el.html(html);
            this._renderChartPhongBan(data.pb_labels, data.pb_values);
            this._renderChartTheoThang(data.theo_thang_labels, data.theo_thang_values);
        },

        _kpiCard: function (icon, value, label, borderColor) {
            return `
                <div style="background:white; border-radius:8px; padding:16px;
                            border:0.5px solid #e0e0e0;
                            border-left:3px solid ${borderColor};">
                    <div style="font-size:22px; font-weight:500; color:#333;">${value}</div>
                    <div style="font-size:12px; color:#888; margin-top:4px;">
                        <i class="fa ${icon}" style="margin-right:4px; color:${borderColor};"></i>
                        ${label}
                    </div>
                </div>
            `;
        },

        _renderChartPhongBan: function (labels, values) {
            var container = this.$el.find('#chartPhongBan')[0];
            if (!container) return;
            if (!labels || labels.length === 0) {
                container.innerHTML = '<p style="color:#aaa;text-align:center;padding:20px;">Chưa có dữ liệu</p>';
                return;
            }
            var max = Math.max.apply(null, values);
            var colors = ['#378ADD','#534AB7','#1D9E75','#BA7517','#E24B4A','#639922'];
            var bars = labels.map(function(label, i) {
                var pct = max > 0 ? (values[i] / max * 100) : 0;
                var formatted = values[i].toLocaleString('vi-VN');
                return `
                    <div style="margin-bottom:14px;">
                        <div style="font-size:12px; color:#666; margin-bottom:4px;">${label}</div>
                        <div style="flex:1; background:#f5f5f5; border-radius:4px; height:24px;">
                            <div style="width:${pct}%; background:${colors[i % colors.length]};
                                        height:100%; border-radius:4px; min-width:40px;
                                        display:flex; align-items:center; justify-content:flex-end;
                                        padding-right:8px;">
                                <span style="color:white; font-size:11px; font-weight:500;">${formatted}</span>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            container.innerHTML = bars;
        },

        _renderChartTheoThang: function (labels, values) {
            var container = this.$el.find('#chartTheoThang')[0];
            if (!container) return;
            if (!labels || labels.length === 0) {
                container.innerHTML = '<p style="color:#aaa;text-align:center;padding:20px;">Chưa có dữ liệu</p>';
                return;
            }
            var max = Math.max.apply(null, values);
            var rows = labels.map(function(label, i) {
                var pct = max > 0 ? (values[i] / max * 100) : 0;
                var formatted = values[i].toLocaleString('vi-VN');
                var isCurrentMonth = (i === labels.length - 1);
                return `
                    <div style="margin-bottom:10px; display:flex; align-items:center; gap:8px;">
                        <span style="min-width:50px; font-size:12px; color:#666;">T${label}</span>
                        <div style="flex:1; background:#f5f5f5; border-radius:4px; height:22px;">
                            <div style="width:${pct}%;
                                        background:${isCurrentMonth ? '#534AB7' : '#B5D4F4'};
                                        height:100%; border-radius:4px; min-width:10px;">
                            </div>
                        </div>
                        <span style="min-width:80px; font-size:11px; color:#666; text-align:right;">${formatted} ₫</span>
                    </div>
                `;
            }).join('');
            container.innerHTML = rows;
        },
    });

    core.action_registry.add('tinh_luong_dashboard', TinhLuongDashboard);
    return TinhLuongDashboard;
});