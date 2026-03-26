odoo.define('nhan_su.chatbot', function (require) {
    'use strict';

    var rpc = require('web.rpc');
    var core = require('web.core');

    function initChatbot() {
        // Tạo HTML chatbot
        var chatbotHtml = `
            <div id="hrChatbot" style="
                position:fixed; bottom:24px; right:24px; z-index:9999;
                font-family:sans-serif;">

                <!-- Nút mở -->
                <div id="chatbotToggle" style="
                    width:52px; height:52px; border-radius:50%;
                    background:#875A7B; color:white;
                    display:flex; align-items:center; justify-content:center;
                    cursor:pointer; box-shadow:0 2px 8px rgba(0,0,0,0.2);">
                    <i class="fa fa-comments" style="font-size:22px;"></i>
                </div>

                <!-- Cửa sổ chat -->
                <div id="chatbotWindow" style="
                    display:none;
                    position:absolute; bottom:64px; right:0;
                    width:360px; height:480px;
                    background:white; border-radius:12px;
                    box-shadow:0 4px 20px rgba(0,0,0,0.15);
                    border:0.5px solid #e0e0e0;
                    flex-direction:column; overflow:hidden;">

                    <!-- Header -->
                    <div style="
                        background:#875A7B; color:white;
                        padding:12px 16px;
                        display:flex; align-items:center; justify-content:space-between;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <i class="fa fa-robot" style="font-size:18px;"></i>
                            <div>
                                <div style="font-size:14px; font-weight:500;">Trợ lý HR</div>
                                <div style="font-size:11px; opacity:0.8;">Powered by Gemini AI</div>
                            </div>
                        </div>
                        <i id="chatbotClose" class="fa fa-times" style="cursor:pointer; font-size:16px;"></i>
                    </div>

                    <!-- Messages -->
                    <div id="chatbotMessages" style="
                        flex:1; overflow-y:auto; padding:12px;
                        display:flex; flex-direction:column; gap:8px;
                        background:#f8f8f8;">
                        <div class="bot-msg" style="
                            background:white; border-radius:8px; padding:10px 12px;
                            font-size:13px; color:#333; max-width:85%;
                            border:0.5px solid #e0e0e0; align-self:flex-start;">
                            Xin chào! Tôi là trợ lý HR. Bạn có thể hỏi tôi về thông tin nhân viên, chấm công, bảng lương... 😊
                        </div>
                    </div>

                    <!-- Input -->
                    <div style="
                        padding:10px 12px;
                        border-top:0.5px solid #e0e0e0;
                        background:white;
                        display:flex; gap:8px; align-items:center;">
                        <input id="chatbotInput" type="text"
                            placeholder="Nhập câu hỏi..."
                            style="
                                flex:1; border:0.5px solid #e0e0e0;
                                border-radius:20px; padding:8px 14px;
                                font-size:13px; outline:none;"/>
                        <button id="chatbotSend" style="
                            width:36px; height:36px; border-radius:50%;
                            background:#875A7B; color:white; border:none;
                            cursor:pointer; display:flex; align-items:center;
                            justify-content:center;">
                            <i class="fa fa-paper-plane" style="font-size:14px;"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatbotHtml);

        var history = [];
        var isLoading = false;

        // Toggle chatbot
        document.getElementById('chatbotToggle').addEventListener('click', function() {
            var win = document.getElementById('chatbotWindow');
            win.style.display = win.style.display === 'none' ? 'flex' : 'none';
            if (win.style.display === 'flex') {
                document.getElementById('chatbotInput').focus();
            }
        });

        document.getElementById('chatbotClose').addEventListener('click', function() {
            document.getElementById('chatbotWindow').style.display = 'none';
        });

        // Gửi tin nhắn
        function sendMessage() {
            if (isLoading) return;
            var input = document.getElementById('chatbotInput');
            var msg = input.value.trim();
            if (!msg) return;

            // Hiển thị tin nhắn người dùng
            appendMessage(msg, 'user');
            input.value = '';

            // Hiển thị loading
            isLoading = true;
            appendLoading();

            // Gọi API
            rpc.query({
                route: '/nhan_su/chatbot',
                params: { message: msg, history: history }
            }).then(function(result) {
                removeLoading();
                isLoading = false;
                if (result.success) {
                    appendMessage(result.answer, 'bot');
                    history.push({ role: 'user', content: msg });
                    history.push({ role: 'model', content: result.answer });
                    // Giữ tối đa 10 tin nhắn gần nhất
                    if (history.length > 20) history = history.slice(-20);
                } else {
                    appendMessage('Xin lỗi, có lỗi xảy ra: ' + result.answer, 'bot');
                }
            }).catch(function() {
                removeLoading();
                isLoading = false;
                appendMessage('Xin lỗi, không thể kết nối. Vui lòng thử lại!', 'bot');
            });
        }

        function appendMessage(text, role) {
            var messages = document.getElementById('chatbotMessages');
            var isBot = role === 'bot';
            var div = document.createElement('div');
            div.style.cssText = `
                background:${isBot ? 'white' : '#875A7B'};
                color:${isBot ? '#333' : 'white'};
                border-radius:8px; padding:10px 12px;
                font-size:13px; max-width:85%; line-height:1.5;
                align-self:${isBot ? 'flex-start' : 'flex-end'};
                border:${isBot ? '0.5px solid #e0e0e0' : 'none'};
                white-space:pre-wrap;
            `;
            div.textContent = text;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function appendLoading() {
            var messages = document.getElementById('chatbotMessages');
            var div = document.createElement('div');
            div.id = 'chatbotLoading';
            div.style.cssText = `
                background:white; border-radius:8px; padding:10px 12px;
                font-size:13px; color:#999; align-self:flex-start;
                border:0.5px solid #e0e0e0;
            `;
            div.textContent = 'Đang xử lý...';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function removeLoading() {
            var loading = document.getElementById('chatbotLoading');
            if (loading) loading.remove();
        }

        // Enter để gửi
        document.getElementById('chatbotInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
        document.getElementById('chatbotSend').addEventListener('click', sendMessage);
    }

    // Khởi động sau khi DOM load
    $(document).ready(function() {
        setTimeout(initChatbot, 1000);
    });
});