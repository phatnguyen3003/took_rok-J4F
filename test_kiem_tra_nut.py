import tkinter as tk
import ctypes
import os
import cv2
import pytesseract
import numpy as np
from PIL import ImageGrab, ImageTk

# Bật DPI awareness để lấy full resolution
ctypes.windll.user32.SetProcessDPIAware()

# Cấu hình đường dẫn tới tesseract.exe
# Vui lòng kiểm tra và chỉnh sửa đường dẫn này nếu cần.
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except Exception as e:
    print(f"Lỗi: Không tìm thấy tesseract.exe. Vui lòng cài đặt và cấu hình đường dẫn. {e}")

# --- Biến toàn cục để lưu trữ tọa độ và các widget ---
coords = {}  # Lưu tọa độ vùng đã chọn
popup_img = None # Biến toàn cục cho hình ảnh trong popup

def kiem_tra_nut(bbox, filename):
    """
    Kiểm tra xem ảnh filename có nằm trong vùng i hay không.
    i: chỉ số vùng (int)
    filename: đường dẫn file ảnh mẫu (str)
    Trả về True nếu tìm thấy, False nếu không.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "data", "dulieu.json")
    buttons_dir = os.path.join(base_dir, "buttons")

    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1

    if width <= 0 or height <= 0:
        print("Lỗi: Vùng chọn không hợp lệ.")
        return 0, None

    # Chụp ảnh màn hình vùng
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Đọc ảnh mẫu
    filename = os.path.join(buttons_dir, filename)
    if not os.path.exists(filename):
        print(f"Không tìm thấy file mẫu: {filename}")
        return False,None

    try:
        template = cv2.imread(filename, cv2.IMREAD_COLOR)
        if template is None:
            print(f"Không thể đọc file ảnh mẫu: {filename}")
            return False,None
    except Exception as e:
        print(f"Lỗi khi đọc ảnh mẫu: {e}")
        return False,None

    # So khớp ảnh
    result = cv2.matchTemplate(img_np, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    # Ngưỡng nhận diện
    threshold = 0.65
    if max_val >= threshold:
        print(f"[OK] Nút tìm thấy trong vùng , độ khớp: {max_val:.2f}")
        return True,None
    else:
        print(f"[Fail] Không tìm thấy nút trong vùng, độ khớp: {max_val:.2f}")
        return False,None

# --- Hàm chọn vùng trên màn hình ---
def chon_vung():
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
        print(f"Đã chọn vùng: (x1={coords['x1']}, y1={coords['y1']}), (x2={coords['x2']}, y2={coords['y2']})")


    canvas.bind("<Button-1>", start_select)
    canvas.bind("<B1-Motion>", update_select)
    canvas.bind("<ButtonRelease-1>", end_select)
    root_select.bind("<Escape>", lambda e: root_select.destroy())
    root_select.mainloop()

# Hàm xử lý và hiển thị kết quả
def process_and_display():
    global popup_img
    if not coords:
        print("Bạn chưa chọn vùng!")
        return

    try:
        left_ratio = float(entry_left.get())
        right_ratio = float(entry_right.get())
        top_ratio = float(entry_top.get())
        bottom_ratio = float(entry_bottom.get())
        
        crop_ratio = (left_ratio, right_ratio, top_ratio, bottom_ratio)
    except ValueError:
        print("Vui lòng nhập số hợp lệ cho tỷ lệ!")
        return

    # Sắp xếp tọa độ để đảm bảo x1 < x2 và y1 < y2
    x_sorted = sorted([coords['x1'], coords['x2']])
    y_sorted = sorted([coords['y1'], coords['y2']])
    bbox = (x_sorted[0], y_sorted[0], x_sorted[1], y_sorted[1])

    # Gọi hàm trích xuất số
    so_trich_xuat, img_cropped = kiem_tra_nut(bbox, "mo_map.png")

    if img_cropped:
        hien_popup(img_cropped, so_trich_xuat)
    else:
        print("Không thể trích xuất. Kiểm tra lại vùng đã chọn.")

# Hàm hiển thị ảnh popup và kết quả
def hien_popup(img, text_extracted):
    global popup_img
    popup = tk.Toplevel(root)
    popup.title("Ảnh Cắt Xem Trước & Kết Quả")
    popup.attributes("-topmost", True)

    tk_img = ImageTk.PhotoImage(img)
    label_img = tk.Label(popup, image=tk_img)
    label_img.image = tk_img
    label_img.pack(padx=5, pady=5)
    
    label_result = tk.Label(popup, text=f"Số trích xuất: '{text_extracted}'", font=("Arial", 12))
    label_result.pack(pady=(0, 10))

# --- Giao diện chính ---
root = tk.Tk()
root.title("Công cụ tinh chỉnh tỷ lệ cắt và trích xuất số")

btn_chon = tk.Button(root, text="1. Chọn Vùng Màn Hình", command=chon_vung)
btn_chon.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

tk.Label(root, text="Lề Trái").grid(row=1, column=0, padx=5, pady=2)
entry_left = tk.Entry(root)
entry_left.insert(0, "0.2")
entry_left.grid(row=1, column=1, padx=5, pady=2)

tk.Label(root, text="Lề Phải").grid(row=2, column=0, padx=5, pady=2)
entry_right = tk.Entry(root)
entry_right.insert(0, "0.2")
entry_right.grid(row=2, column=1, padx=5, pady=2)

tk.Label(root, text="Lề Trên").grid(row=3, column=0, padx=5, pady=2)
entry_top = tk.Entry(root)
entry_top.insert(0, "0.2")
entry_top.grid(row=3, column=1, padx=5, pady=2)

tk.Label(root, text="Lề Dưới").grid(row=4, column=0, padx=5, pady=2)
entry_bottom = tk.Entry(root)
entry_bottom.insert(0, "0.2")
entry_bottom.grid(row=4, column=1, padx=5, pady=2)

btn_process = tk.Button(root, text="2. Trích Xuất & Xem", command=process_and_display)
btn_process.grid(row=5, column=0, columnspan=2, pady=10, padx=10)

root.mainloop()
