import tkinter as tk
import ctypes
import os
import cv2
import pytesseract
import numpy as np
from PIL import ImageGrab, ImageTk
import re # Thêm thư viện re để sử dụng biểu thức chính quy

# Bật DPI awareness để lấy full resolution
ctypes.windll.user32.SetProcessDPIAware()

# Cấu hình đường dẫn tới file tesseract.exe.
# Vui lòng kiểm tra và chỉnh sửa đường dẫn này nếu cần.
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except Exception as e:
    print(f"Lỗi: Không tìm thấy tesseract.exe. Vui lòng cài đặt và cấu hình đường dẫn. {e}")

# --- Định nghĩa hàm trích xuất chuỗi ký tự ---
def tx_gems(x_search, y_search, x2_search, y2_search, left_margin_ratio, right_margin_ratio, top_margin_ratio, bottom_margin_ratio, extraction_mode):
    """
    Hàm trích xuất chuỗi ký tự bằng cách tìm khung mẫu trong một vùng đã xác định.
    
    Args:
        x_search, y_search, x2_search, y2_search: Tọa độ vùng tìm kiếm khung mẫu.
        left_margin_ratio: Tỷ lệ lề trái để cắt ảnh (0.0 đến 1.0).
        right_margin_ratio: Tỷ lệ lề phải để cắt ảnh (0.0 đến 1.0).
        top_margin_ratio: Tỷ lệ lề trên để cắt ảnh (0.0 đến 1.0).
        bottom_margin_ratio: Tỷ lệ lề dưới để cắt ảnh (0.0 đến 1.0).
        extraction_mode: Chế độ trích xuất ('vietnamese' hoặc 'xy_numbers').

    Returns:
        tuple: (chuỗi văn bản trích xuất, ảnh đã cắt)
    """
    # Lấy thư mục hiện tại của script để tìm file ảnh mẫu
    base_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        # Chụp màn hình của vùng tìm kiếm đã được định nghĩa
        search_region_img = ImageGrab.grab(bbox=(x_search, y_search, x2_search, y2_search))
        search_region_cv = cv2.cvtColor(np.array(search_region_img), cv2.COLOR_RGB2BGR)

        # Tải ảnh mẫu khung lớn từ thư mục buttons
        template_path = os.path.join(base_dir, "buttons", "khung.png")
        template = cv2.imread(template_path)
        
        if template is None:
            # Thông báo lỗi nếu không tìm thấy file ảnh mẫu
            raise FileNotFoundError(f"Không tìm thấy file ảnh mẫu khung.png tại {template_path}. Vui lòng đảm bảo file tồn tại.")

        # Tìm vị trí khung mẫu trong vùng đã chụp
        result = cv2.matchTemplate(search_region_cv, template, cv2.TM_CCOEFF_NORMED)
        _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.6:  # Sử dụng ngưỡng độ chính xác
            x_khung_relative, y_khung_relative = max_loc
            w_khung, h_khung = template.shape[1], template.shape[0]
            
            # Tính toán các lề cố định để cắt ảnh từ khung tìm được
            left_margin = int(w_khung * left_margin_ratio)
            right_margin = int(w_khung * right_margin_ratio)
            top_margin = int(h_khung * top_margin_ratio)
            bottom_margin = int(h_khung * bottom_margin_ratio)

            # Tính toán tọa độ cắt ảnh
            x1_crop = x_khung_relative + left_margin
            y1_crop = y_khung_relative + top_margin
            x2_crop = (x_khung_relative + w_khung) - right_margin
            y2_crop = (y_khung_relative + h_khung) - bottom_margin
            
            # Cắt ảnh từ vùng tìm kiếm ban đầu dựa trên các lề
            crop_img = search_region_img.crop((x1_crop, y1_crop, x2_crop, y2_crop))
            
            # Trích xuất văn bản từ ảnh đã cắt
            text = pytesseract.image_to_string(
                crop_img,
                lang='vie',
                config='--psm 7'
            ).strip()

            # Lựa chọn chế độ trích xuất dựa trên lựa chọn của người dùng
            if extraction_mode == 'xy_numbers':
                # Chế độ 2: Lọc chỉ giữ lại các ký tự 'x', 'y' và 0-9
                cleaned_text = re.sub(r'[^xyXY0-9]', '', text)
            else:
                # Chế độ 1: Giữ lại toàn bộ văn bản tiếng Việt
                cleaned_text = text
            
            return cleaned_text, crop_img
            
        else:
            print("Không tìm thấy khung mẫu trong vùng đã xác định.")
            return "", None
            
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return "", None

# --- Giao diện người dùng Tkinter ---
coords = {}  # Lưu tọa độ vùng chọn
popup = None # Biến toàn cục cho cửa sổ popup

def chon_vung():
    """Tạo cửa sổ trong suốt để người dùng chọn vùng trên màn hình."""
    global coords
    coords.clear()

    root_select = tk.Toplevel()
    root_select.overrideredirect(True)
    screen_width = root_select.winfo_screenwidth()
    screen_height = root_select.winfo_screenheight()
    root_select.geometry(f"{screen_width}x{screen_height}+0+0")
    root_select.attributes("-topmost", True)
    root_select.attributes("-alpha", 0.3)
    root_select.configure(bg='black')

    canvas = tk.Canvas(root_select, cursor="cross", bg='gray', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    rect = None

    def start_select(event):
        nonlocal rect
        coords['x1'], coords['y1'] = event.x_root, event.y_root
        canvas.delete("rect")
        rect = canvas.create_rectangle(event.x_root, event.y_root, event.x_root, event.y_root,
                                         outline='red', width=2, tags="rect")

    def update_select(event):
        if rect:
            canvas.coords("rect", coords['x1'], coords['y1'], event.x_root, event.y_root)

    def end_select(event):
        coords['x2'], coords['y2'] = event.x_root, event.y_root
        root_select.destroy()
        print(f"Đã chọn vùng: x1={coords['x1']}, y1={coords['y1']}, x2={coords['x2']}, y2={coords['y2']}")

    canvas.bind("<Button-1>", start_select)
    canvas.bind("<B1-Motion>", update_select)
    canvas.bind("<ButtonRelease-1>", end_select)
    root_select.bind("<Escape>", lambda e: root_select.destroy())

    root_select.mainloop()

# Hàm xử lý và hiển thị kết quả
def process_and_display():
    """Gọi hàm trích xuất và hiển thị kết quả lên cửa sổ popup."""
    global popup
    if not coords:
        print("Bạn chưa chọn vùng!")
        return

    if popup and popup.winfo_exists():
        popup.destroy()

    try:
        # Lấy giá trị từ các ô nhập lề
        left_margin_ratio = float(entry_left.get())
        right_margin_ratio = float(entry_right.get())
        top_margin_ratio = float(entry_top.get())
        bottom_margin_ratio = float(entry_bottom.get())
    except ValueError:
        print("Vui lòng nhập số hợp lệ cho tỷ lệ!")
        return

    # Lấy chế độ trích xuất được chọn
    mode = mode_var.get()

    # Sắp xếp tọa độ để đảm bảo chúng đúng thứ tự
    x_sorted = sorted([coords['x1'], coords['x2']])
    y_sorted = sorted([coords['y1'], coords['y2']])
    x_search, x2_search = x_sorted
    y_search, y2_search = y_sorted

    # Gọi hàm trích xuất với các tọa độ, lề và chế độ
    text_extracted, img_cropped = tx_gems(
        x_search, y_search, x2_search, y2_search, 
        left_margin_ratio, right_margin_ratio, top_margin_ratio, bottom_margin_ratio,
        mode
    )
    
    if img_cropped:
        hien_popup(img_cropped, text_extracted)
    else:
        print("Không thể trích xuất. Kiểm tra lại ảnh khung và vùng đã chọn.")

# Hàm hiển thị ảnh popup và kết quả
def hien_popup(img, text_extracted):
    """Tạo cửa sổ popup để hiển thị ảnh đã chụp và văn bản trích xuất."""
    global popup
    popup = tk.Toplevel(root)
    popup.title("Ảnh Cắt Xem Trước & Kết Quả")
    popup.attributes("-topmost", True)

    tk_img = ImageTk.PhotoImage(img)
    label_img = tk.Label(popup, image=tk_img)
    label_img.image = tk_img
    label_img.pack(padx=5, pady=5)
    
    label_result = tk.Label(popup, text=f"Chuỗi trích xuất: '{text_extracted}'", font=("Arial", 12))
    label_result.pack(pady=(0, 10))

# --- Giao diện chính ---
root = tk.Tk()
root.title("Công cụ tinh chỉnh tỷ lệ cắt")

btn_chon = tk.Button(root, text="1. Chọn Vùng Tìm Khung", command=chon_vung)
btn_chon.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

tk.Label(root, text="Lề Trái (%)").grid(row=1, column=0, padx=5, pady=2)
entry_left = tk.Entry(root)
entry_left.insert(0, "0.75")
entry_left.grid(row=1, column=1, padx=5, pady=2)

tk.Label(root, text="Lề Phải (%)").grid(row=2, column=0, padx=5, pady=2)
entry_right = tk.Entry(root)
entry_right.insert(0, "0.09")
entry_right.grid(row=2, column=1, padx=5, pady=2)

tk.Label(root, text="Lề Trên (%)").grid(row=3, column=0, padx=5, pady=2)
entry_top = tk.Entry(root)
entry_top.insert(0, "0.37")
entry_top.grid(row=3, column=1, padx=5, pady=2)

tk.Label(root, text="Lề Dưới (%)").grid(row=4, column=0, padx=5, pady=2)
entry_bottom = tk.Entry(root)
entry_bottom.insert(0, "0.575")
entry_bottom.grid(row=4, column=1, padx=5, pady=2)

# Khung chọn chế độ
mode_var = tk.StringVar(value='xy_numbers')
tk.Label(root, text="Chọn Chế Độ:").grid(row=5, column=0, columnspan=2, pady=(10, 0))

rb_vietnamese = tk.Radiobutton(root, text="1. Văn bản tiếng Việt", variable=mode_var, value='vietnamese')
rb_vietnamese.grid(row=6, column=0, columnspan=2, sticky='w', padx=10)

rb_xy_numbers = tk.Radiobutton(root, text="2. Chỉ 'x,y' và số", variable=mode_var, value='xy_numbers')
rb_xy_numbers.grid(row=7, column=0, columnspan=2, sticky='w', padx=10)

btn_process = tk.Button(root, text="3. Trích Xuất & Xem", command=process_and_display)
btn_process.grid(row=8, column=0, columnspan=2, pady=10, padx=10)

root.mainloop()
