document.addEventListener('DOMContentLoaded', function() {
    const chatWidget = document.querySelector('.chat-widget');
    let isResizing = false;
    let startX, startY, startWidth, startHeight;

    // Lưu kích thước vào localStorage
    function saveChatSize() {
        localStorage.setItem('chatWidth', chatWidget.style.width);
        localStorage.setItem('chatHeight', chatWidget.style.height);
    }

    // Khôi phục kích thước từ localStorage
    function restoreChatSize() {
        const savedWidth = localStorage.getItem('chatWidth');
        const savedHeight = localStorage.getItem('chatHeight');
        if (savedWidth && savedHeight) {
            chatWidget.style.width = savedWidth;
            chatWidget.style.height = savedHeight;
        }
    }

    // Khôi phục kích thước khi load trang
    restoreChatSize();

    // Lưu kích thước khi resize kết thúc
    chatWidget.addEventListener('mouseup', function() {
        if (isResizing) {
            isResizing = false;
            saveChatSize();
        }
    });
});