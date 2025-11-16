import tkinter as tk
import ctypes
import os
import pytesseract
import re
from PIL import ImageGrab, ImageTk

# Bật DPI awareness để lấy full resolution
ctypes.windll.user32.SetProcessDPIAware()
# Cấu hình đường dẫn tới tesseract.exe. Vui lòng kiểm tra và chỉnh sửa.
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except Exception as e:
    print(f"Lỗi: Không tìm thấy tesseract.exe. Vui lòng cài đặt và cấu hình đường dẫn. {e}")

# --- Các hàm trích xuất và phân tích tọa độ do bạn cung cấp ---
def lay_so_tu_chuoi(chuoi_dau_vao):
    """
    Trích xuất tất cả các chữ số từ một chuỗi bất kỳ.
    Sử dụng biểu thức chính quy để tìm tất cả các chuỗi con chứa số, sau đó nối chúng lại.
    Args:
        chuoi_dau_vao (str): Chuỗi chứa cả chữ và số.
    Returns:
        str: Chuỗi chỉ chứa các chữ số.
    """
    danh_sach_so = re.findall(r'\d+', chuoi_dau_vao)
    ket_qua = "".join(danh_sach_so)
    return ket_qua

def tach_chuoi_toa_do(chuoi_dau_vao):
    """
    Tách chuỗi thành hai phần dựa trên các định dạng cụ thể và chỉ lấy các chữ số.
    Hàm này xử lý các trường hợp: X1234Y1234, X1234 1234
    
    Args:
        chuoi_dau_vao (str): Chuỗi cần tách.
    Returns:
        tuple: Một tuple chứa hai chuỗi chỉ toàn số đã tách. Trả về (None, None) nếu không khớp.
    """
    # Sử dụng biểu thức chính quy để tìm và bắt các nhóm số.
    match = re.search(r'^[xX](.+)[yY\s](.+)$', chuoi_dau_vao)
    
    if match:
        chuoi_goc_1 = match.group(1)
        chuoi_goc_2 = match.group(2)
        
        # Gọi hàm lay_so_tu_chuoi để làm sạch và chỉ lấy các chữ số
        so_trich_xuat_1 = lay_so_tu_chuoi(chuoi_goc_1)
        so_trich_xuat_2 = lay_so_tu_chuoi(chuoi_goc_2)
        
        return so_trich_xuat_1, so_trich_xuat_2
    else:
        return None, None

def trich_xuat_doc_lap(bbox, crop_ratio=(0.0, 0.0, 0.0, 0.0)):
    """
    Trích xuất toàn bộ chuỗi ký tự từ một vùng màn hình đã xác định.
    Sử dụng lang='eng' và biểu thức chính quy để chỉ giữ lại chữ cái Latin, số và khoảng trắng.
    """
    try:
        x1, y1, x2, y2 = bbox
    except (ValueError, TypeError):
        print("Lỗi: bbox không phải tuple 4 giá trị hợp lệ.")
        return "", None

    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    width, height = img.size

    left_margin = int(width * crop_ratio[0])
    right_margin = int(width * crop_ratio[1])
    top_margin = int(height * crop_ratio[2])
    bottom_margin = int(height * crop_ratio[3])

    crop_img = img.crop((
        left_margin,
        top_margin,
        width - right_margin,
        height - bottom_margin
    ))
    
    text_ocr_raw = pytesseract.image_to_string(crop_img, lang='eng', config='--psm 6').strip()
    
    # regex_english chỉ giữ lại chữ cái Latin, số và khoảng trắng
    regex_english = r'[^a-zA-Z0-9\s]+'
    text_trich_xuat = re.sub(regex_english, '', text_ocr_raw)
    
    return text_trich_xuat, crop_img

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

def process_and_display():
    """Lấy tọa độ từ vùng chọn, gọi hàm trích xuất và hiển thị kết quả."""
    global popup
    if not coords:
        print("Bạn chưa chọn vùng!")
        return

    if popup and popup.winfo_exists():
        popup.destroy()

    try:
        left_margin_ratio = float(entry_left.get())
        right_margin_ratio = float(entry_right.get())
        top_margin_ratio = float(entry_top.get())
        bottom_margin_ratio = float(entry_bottom.get())
    except ValueError:
        print("Vui lòng nhập số hợp lệ cho tỷ lệ!")
        return

    crop_ratio_tuple = (left_margin_ratio, right_margin_ratio, top_margin_ratio, bottom_margin_ratio)

    x_sorted = sorted([coords['x1'], coords['x2']])
    y_sorted = sorted([coords['y1'], coords['y2']])
    bbox = (x_sorted[0], y_sorted[0], x_sorted[1], y_sorted[1])

    # Bước 1: Trích xuất văn bản từ vùng đã chọn
    text_trich_xuat, img_cropped = trich_xuat_doc_lap(bbox, crop_ratio=crop_ratio_tuple)
    
    # Bước 2: Phân tích tọa độ từ chuỗi văn bản
    x_coord, y_coord = tach_chuoi_toa_do(text_trich_xuat)

    if img_cropped:
        hien_popup(img_cropped, text_trich_xuat, x_coord, y_coord)
    else:
        print("Không thể trích xuất. Vui lòng kiểm tra lại vùng đã chọn và tỷ lệ.")

def hien_popup(img, text_trich_xuat, x_coord, y_coord):
    """Tạo cửa sổ popup để hiển thị ảnh đã chụp và văn bản trích xuất."""
    global popup
    popup = tk.Toplevel(root)
    popup.title("Ảnh Cắt Xem Trước & Kết Quả")
    popup.attributes("-topmost", True)

    tk_img = ImageTk.PhotoImage(img)
    label_img = tk.Label(popup, image=tk_img)
    label_img.image = tk_img
    label_img.pack(padx=5, pady=5)
    
    text_result = f"Văn bản trích xuất: '{text_trich_xuat}'\n"
    text_result += f"Tọa độ X đã phân tích: '{x_coord}'\n"
    text_result += f"Tọa độ Y đã phân tích: '{y_coord}'"
    label_result = tk.Label(popup, text=text_result, font=("Arial", 12))
    label_result.pack(pady=(0, 10))

# --- Giao diện chính ---
root = tk.Tk()
root.title("Công cụ trích xuất và phân tích tọa độ")

btn_chon = tk.Button(root, text="1. Chọn Vùng Màn Hình", command=chon_vung)
btn_chon.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

tk.Label(root, text="Lề Trái (0-1)").grid(row=1, column=0, padx=5, pady=2)
entry_left = tk.Entry(root)
entry_left.insert(0, "0.2")
entry_left.grid(row=1, column=1, padx=5, pady=2)

tk.Label(root, text="Lề Phải (0-1)").grid(row=2, column=0, padx=5, pady=2)
entry_right = tk.Entry(root)
entry_right.insert(0, "0.2")
entry_right.grid(row=2, column=1, padx=5, pady=2)

tk.Label(root, text="Lề Trên (0-1)").grid(row=3, column=0, padx=5, pady=2)
entry_top = tk.Entry(root)
entry_top.insert(0, "0.2")
entry_top.grid(row=3, column=1, padx=5, pady=2)

tk.Label(root, text="Lề Dưới (0-1)").grid(row=4, column=0, padx=5, pady=2)
entry_bottom = tk.Entry(root)
entry_bottom.insert(0, "0.2")
entry_bottom.grid(row=4, column=1, padx=5, pady=2)

btn_process = tk.Button(root, text="2. Trích Xuất & Phân Tích", command=process_and_display)
btn_process.grid(row=5, column=0, columnspan=2, pady=10, padx=10)

root.mainloop()
