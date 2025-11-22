# LùnPetShop Chatbot Customization Guide / Hướng dẫn Tùy chỉnh Chatbot

This guide helps you customize the LùnPetShop chatbot, including its personality, business information, and user interface.

Tài liệu này giúp bạn tùy chỉnh chatbot LùnPetShop, bao gồm tính cách, thông tin cửa hàng và giao diện người dùng.

---

## 1. Changing AI Personality / Thay đổi Tính cách AI

The AI's personality and instructions are defined in the **System Prompt**.
Tính cách và hướng dẫn của AI được định nghĩa trong **System Prompt**.

*   **File / Tệp tin:** `backend/src/prompts.py`
*   **Function / Hàm:** `get_system_prompt`

### How to edit / Cách chỉnh sửa:
Open the file and look for the text inside `f"""..."""`. You will see two versions: one for Vietnamese (`if language == "vi"`) and one for English (`else`).
Mở tệp tin và tìm đoạn văn bản bên trong `f"""..."""`. Bạn sẽ thấy hai phiên bản: một cho tiếng Việt (`if language == "vi"`) và một cho tiếng Anh (`else`).

**Example / Ví dụ:**
To make the AI more formal, change:
Để làm cho AI trang trọng hơn, thay đổi:
> "Tính cách: Thân thiện, nhiệt tình"
> -> "Tính cách: Chuyên nghiệp, lịch sự"

---

## 2. Updating Business Info / Cập nhật Thông tin Cửa hàng

Phone numbers, addresses, and opening hours are stored in one place.
Số điện thoại, địa chỉ và giờ mở cửa được lưu trữ tại một nơi duy nhất.

*   **File / Tệp tin:** `backend/src/knowledge_base.py`
*   **Variable / Biến:** `BUSINESS_INFO`

### How to edit / Cách chỉnh sửa:
Change the values in the dictionary.
Thay đổi các giá trị trong từ điển.

```python
BUSINESS_INFO = {
    "name": "LùnPetShop",
    "address": "K18/26 Nguyễn Văn Linh, Hải Châu, Đà Nẵng", # Change this / Thay đổi dòng này
    "zalo": "0935005762",
    # ...
}
```

---

## 3. Editing the UI / Chỉnh sửa Giao diện

The chat widget's look and feel (colors, size, fonts) are controlled by CSS.
Giao diện của widget chat (màu sắc, kích thước, phông chữ) được điều khiển bởi CSS.

*   **File / Tệp tin:** `widget/assets/css/chat-widget.css`

### Common Changes / Các thay đổi phổ biến:

*   **Change Colors / Đổi màu:**
    Look for the `:root` or `.lunpetshop-chat-widget` section at the top.
    Tìm phần `:root` hoặc `.lunpetshop-chat-widget` ở đầu tệp.
    ```css
    --primary-color: #FFC107; /* Main yellow color / Màu vàng chủ đạo */
    --dark-bg: #1a1a2e;       /* Background color / Màu nền */
    ```

*   **Change Size / Đổi kích thước:**
    Look for `.chat-window`.
    Tìm `.chat-window`.
    ```css
    .lunpetshop-chat-widget .chat-window {
        width: 380px;  /* Width / Chiều rộng */
        height: 600px; /* Height / Chiều cao */
    }
    ```

---

## 4. Applying UI Changes / Áp dụng Thay đổi Giao diện

After editing the CSS or JS in the `widget/` folder, you must run the build script to update the WordPress plugin.
Sau khi chỉnh sửa CSS hoặc JS trong thư mục `widget/`, bạn phải chạy script build để cập nhật plugin WordPress.

*   **Command / Lệnh:**
    ```bash
    ./bin/build-plugin.sh
    ```

This script copies your changes to the plugin folder and creates a new `.zip` file for you to upload to WordPress.
Script này sẽ sao chép các thay đổi của bạn vào thư mục plugin và tạo một tệp `.zip` mới để bạn tải lên WordPress.

---

## 5. Troubleshooting / Khắc phục sự cố

*   **AI not replying? / AI không trả lời?**
    Check if your `XAI_API_KEY` is set in the `.env` file.
    Kiểm tra xem `XAI_API_KEY` đã được cài đặt trong tệp `.env` chưa.

*   **Changes not showing? / Thay đổi không hiển thị?**
    Clear your browser cache or try Incognito mode. If using WordPress, reinstall the plugin zip file.
    Xóa cache trình duyệt hoặc thử chế độ Ẩn danh. Nếu dùng WordPress, hãy cài lại tệp zip plugin.


