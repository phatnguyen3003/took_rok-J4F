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
    # Cấu hình đường dẫn tesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except Exception as e:
    print(f"Lỗi: Không tìm thấy tesseract.exe. Vui lòng cài đặt và cấu hình đường dẫn. {e}")

# --- Biến toàn cục để lưu trữ tọa độ và các widget ---
coords = {}  # Lưu tọa độ vùng đã chọn
popup_img = None # Biến toàn cục cho hình ảnh trong popup

def tx_ky_tu_va_so(bbox, crop_ratio=(0.2, 0.2, 0.2, 0.2)):
    """
    Trích xuất ký tự và số từ một vùng màn hình đã được định nghĩa bởi bbox, với tỷ lệ cắt tùy chỉnh.

    bbox: một tuple (x1, y1, x2, y2) chứa tọa độ vùng đã chọn.
    crop_ratio: một tuple (trái, phải, trên, dưới) với giá trị từ 0 đến 1.
                Ví dụ: (0.1, 0.1, 0.2, 0.2) sẽ cắt 10% từ trái/phải, 20% từ trên/dưới.
    """
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1

    if width <= 0 or height <= 0:
        print("Lỗi: Vùng chọn không hợp lệ.")
        return "", None

    # Chụp ảnh vùng
    try:
        img = ImageGrab.grab(bbox=bbox)

        # Áp dụng tỷ lệ cắt từ tham số crop_ratio theo thứ tự: trái, phải, trên, dưới
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
        
        # SỬA ĐỔI: Loại bỏ tùy chọn 'digits' để trích xuất cả ký tự và số.
        # Sử dụng psm 7 để đọc một dòng văn bản.
        text = pytesseract.image_to_string(crop_img, config='--psm 7').strip()
        
        print(f"OCR đã trích xuất: '{text}'")
        return text, crop_img

    except Exception as e:
        print(f"Lỗi trong hàm tx_ky_tu_va_so: {e}")
        return "", None


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

    # SỬA ĐỔI: Gọi hàm trích xuất ký tự và số
    text_extracted, img_cropped = tx_ky_tu_va_so(bbox, crop_ratio)

    if img_cropped:
        # SỬA ĐỔI: Gửi chuỗi văn bản đã trích xuất đến hàm hiển thị
        hien_popup(img_cropped, text_extracted)
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
    
    # SỬA ĐỔI: Hiển thị văn bản đã trích xuất (bao gồm cả ký tự và số)
    label_result = tk.Label(popup, text=f"Văn bản trích xuất: '{text_extracted}'", font=("Arial", 12))
    label_result.pack(pady=(0, 10))

# --- Giao diện chính ---
root = tk.Tk()
root.title("Công cụ tinh chỉnh tỷ lệ cắt và trích xuất ký tự")

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
