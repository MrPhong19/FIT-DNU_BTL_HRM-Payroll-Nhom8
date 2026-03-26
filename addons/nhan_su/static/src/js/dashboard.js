odoo.define('nhan_su.dashboard', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');

    var NhanSuDashboard = AbstractAction.extend({

        start: function () {
            var self = this;
            return rpc.query({
                route: '/nhan_su/dashboard_data',
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
                            <i class="fa fa-users"></i> Dashboard Nhân sự
                        </h2>
                        <p style="color:#999; margin:4px 0 0; font-size:13px;">Tháng ${data.thang_hien_tai}</p>
                    </div>

                    <!-- KPI Cards hàng 1 -->
                    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:12px;">
                        ${this._kpiCard('fa-users', data.tong_nv, 'Đang làm việc', '#378ADD')}
                        ${this._kpiCard('fa-user-plus', data.thu_viec, 'Thử việc', '#BA7517')}
                        ${this._kpiCard('fa-user-times', data.nghi_viec, 'Nghỉ việc', '#1D9E75')}
                    </div>

                    <!-- KPI Cards hàng 2 -->
                    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:20px;">
                        ${this._kpiCard('fa-file-text', data.sap_het_han, 'HĐ sắp hết hạn', '#534AB7')}
                        ${this._kpiCard('fa-trophy', data.khen_thuong, 'Khen thưởng', '#639922')}
                        ${this._kpiCard('fa-gavel', data.ky_luat, 'Kỷ luật', '#E24B4A')}
                    </div>

                    <!-- Chart + Tổng hợp chấm công -->
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">

                        <!-- Chart phòng ban -->
                        <div style="background:white; border-radius:8px; padding:16px;
                                    border:0.5px solid #e0e0e0;">
                            <h5 style="margin:0 0 14px; color:#555; font-size:14px; font-weight:500;">
                                <i class="fa fa-bar-chart" style="color:#875A7B;"></i>
                                Nhân viên theo phòng ban
                            </h5>
                            <div id="chartNhanVien"></div>
                        </div>

                        <!-- Tổng hợp chấm công -->
                        <div style="background:white; border-radius:8px; padding:16px;
                                    border:0.5px solid #e0e0e0;">

                            <!-- Hôm nay -->
                            <h5 style="margin:0 0 10px; color:#555; font-size:14px; font-weight:500;">
                                <i class="fa fa-calendar-check-o" style="color:#875A7B;"></i>
                                Chấm công hôm nay (${data.ngay_hom_nay})
                            </h5>
                            <table style="width:100%; border-collapse:collapse; font-size:13px; margin-bottom:16px;">
                                <tr style="border-bottom:1px solid #f0f0f0;">
                                    <td style="padding:8px 0; color:#666;">
                                        <i class="fa fa-check-circle" style="color:#639922;"></i> Đi làm đúng giờ
                                    </td>
                                    <td style="text-align:right; font-weight:500; color:#639922;">${data.hom_nay_di_lam} người</td>
                                </tr>
                                <tr style="border-bottom:1px solid #f0f0f0;">
                                    <td style="padding:8px 0; color:#666;">
                                        <i class="fa fa-clock-o" style="color:#BA7517;"></i> Đi muộn
                                    </td>
                                    <td style="text-align:right; font-weight:500; color:#BA7517;">${data.hom_nay_di_muon} người</td>
                                </tr>
                                <tr style="border-bottom:1px solid #f0f0f0;">
                                    <td style="padding:8px 0; color:#666;">
                                        <i class="fa fa-times-circle" style="color:#E24B4A;"></i> Vắng mặt
                                    </td>
                                    <td style="text-align:right; font-weight:500; color:#E24B4A;">${data.hom_nay_vang_mat} người</td>
                                </tr>
                                <tr>
                                    <td style="padding:8px 0; color:#666;">
                                        <i class="fa fa-calendar-times-o" style="color:#378ADD;"></i> Vắng có phép
                                    </td>
                                    <td style="text-align:right; font-weight:500; color:#378ADD;">${data.hom_nay_co_phep} người</td>
                                </tr>
                            </table>

                            <!-- Tổng kết tháng -->
                            <div style="border-top:1px solid #f0f0f0; padding-top:14px;">
                                <h5 style="margin:0 0 10px; color:#555; font-size:14px; font-weight:500;">
                                    <i class="fa fa-bar-chart" style="color:#875A7B;"></i>
                                    Tổng kết tháng ${data.thang_hien_tai}
                                </h5>
                                <table style="width:100%; border-collapse:collapse; font-size:13px;">
                                    <tr style="border-bottom:1px solid #f0f0f0;">
                                        <td style="padding:8px 0; color:#666;">
                                            <i class="fa fa-clock-o" style="color:#BA7517;"></i> Có đi muộn
                                        </td>
                                        <td style="text-align:right; font-weight:500; color:#BA7517;">${data.nv_di_muon} người</td>
                                    </tr>
                                    <tr style="border-bottom:1px solid #f0f0f0;">
                                        <td style="padding:8px 0; color:#666;">
                                            <i class="fa fa-times-circle" style="color:#E24B4A;"></i> Có vắng mặt
                                        </td>
                                        <td style="text-align:right; font-weight:500; color:#E24B4A;">${data.nv_vang_mat} người</td>
                                    </tr>
                                    <tr style="border-bottom:1px solid #f0f0f0;">
                                        <td style="padding:8px 0; color:#666;">
                                            <i class="fa fa-exclamation-circle" style="color:#BA7517;"></i> Chưa chốt công
                                        </td>
                                        <td style="text-align:right; font-weight:500; color:#BA7517;">${data.nv_chua_chot} người</td>
                                    </tr>
                                    <tr>
                                        <td style="padding:8px 0; color:#666;">
                                            <i class="fa fa-bar-chart" style="color:#534AB7;"></i> TB phút đi muộn
                                        </td>
                                        <td style="text-align:right; font-weight:500; color:#534AB7;">${data.tb_phut_muon} phút/người</td>
                                    </tr>
                                </table>
                            </div>

                        </div>
                    </div>
                </div>
            `;
            this.$el.html(html);
            this._renderChart(data.chart_labels, data.chart_values);
        },

        _kpiCard: function (icon, value, label, borderColor) {
            return `
                <div style="background:white; border-radius:8px; padding:16px;
                            border:0.5px solid #e0e0e0;
                            border-left:3px solid ${borderColor};">
                    <div style="font-size:26px; font-weight:500; color:#333;">${value}</div>
                    <div style="font-size:12px; color:#888; margin-top:4px;">
                        <i class="fa ${icon}" style="margin-right:4px; color:${borderColor};"></i>
                        ${label}
                    </div>
                </div>
            `;
        },

        _renderChart: function (labels, values) {
            var container = this.$el.find('#chartNhanVien')[0];
            if (!container) return;
            if (!labels || labels.length === 0) {
                container.innerHTML = '<p style="color:#aaa;text-align:center;padding:20px;">Chưa có dữ liệu</p>';
                return;
            }
            var max = Math.max.apply(null, values);
            var colors = ['#378ADD','#534AB7','#1D9E75','#BA7517','#E24B4A','#639922'];
            var bars = labels.map(function(label, i) {
                var pct = max > 0 ? (values[i] / max * 100) : 0;
                return `
                    <div style="margin-bottom:14px;">
                        <div style="font-size:12px; color:#666; margin-bottom:4px;">${label}</div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <div style="flex:1; background:#f5f5f5; border-radius:4px; height:24px;">
                                <div style="width:${pct}%; background:${colors[i % colors.length]};
                                            height:100%; border-radius:4px; min-width:28px;
                                            display:flex; align-items:center; justify-content:flex-end;
                                            padding-right:8px;">
                                    <span style="color:white; font-size:12px; font-weight:500;">${values[i]}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            container.innerHTML = bars;
        },
    });

    core.action_registry.add('nhan_su_dashboard', NhanSuDashboard);
    return NhanSuDashboard;
});