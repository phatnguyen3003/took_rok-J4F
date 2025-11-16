import tkinter as tk
import ctypes
import os
import pytesseract
import time
import sys
import cv2
import numpy as np
from PIL import ImageGrab, Image

# Bật DPI awareness để lấy full resolution
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

# Cấu hình đường dẫn tới tesseract.exe (chỉnh lại nếu cần)
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except Exception as e:
    print(f"Lỗi: Không tìm thấy tesseract.exe. {e}")
    sys.exit()

# --- Các biến toàn cục ---
coords = {}
popup = None


# --- Hàm chọn vùng ---
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
        rect = canvas.create_rectangle(event.x_root, event.y_root,
                                       event.x_root, event.y_root,
                                       outline='red', width=2, tags="rect")

    def update_select(event):
        if rect:
            canvas.coords("rect", coords['x1'], coords['y1'], event.x_root, event.y_root)

    def end_select(event):
        coords['x2'], coords['y2'] = event.x_root, event.y_root
        root_select.destroy()
        print(f"Đã chọn vùng: x1={coords['x1']}, y1={coords['y1']}, "
              f"x2={coords['x2']}, y2={coords['y2']}")

    canvas.bind("<Button-1>", start_select)
    canvas.bind("<B1-Motion>", update_select)
    canvas.bind("<ButtonRelease-1>", end_select)
    root_select.bind("<Escape>", lambda e: root_select.destroy())
    root_select.mainloop()


# --- Hàm xử lý OCR (cũ) ---
def dem_va_xu_ly_diem_trung():
    if not coords:
        print("Bạn chưa chọn vùng!")
        return

    print("\n--- OCR tìm điểm trùng ---")

    x_sorted = sorted([coords['x1'], coords['x2']])
    y_sorted = sorted([coords['y1'], coords['y2']])
    bbox = (x_sorted[0], y_sorted[0], x_sorted[1], y_sorted[1])

    img_vung_chon = ImageGrab.grab(bbox)
    data = pytesseract.image_to_data(img_vung_chon, output_type=pytesseract.Output.DATAFRAME)

    words = data[data.conf != '-1']
    words['text'] = words['text'].astype(str).str.strip()
    words = words[words['text'] != '']

    diem_trung = {}
    for _, row in words.iterrows():
        text = row['text']
        if len(text) > 1:
            x, y, w, h = row['left'], row['top'], row['width'], row['height']
            diem_trung.setdefault(text, []).append((x, y, w, h))

    found = False
    for text, vi_tri in diem_trung.items():
        if len(vi_tri) > 1:
            found = True
            print(f"\n'{text}' trùng {len(vi_tri)} lần:")
            for i, (x, y, w, h) in enumerate(vi_tri, 1):
                abs_x = x_sorted[0] + x
                abs_y = y_sorted[0] + y
                print(f"  - {i}: ({abs_x},{abs_y})")
                thuc_hien_thao_tac_tai_diem_trung(text, abs_x, abs_y, w, h)
    if not found:
        print("Không có văn bản trùng.")


# --- Hàm xử lý Template Matching ---
def dem_va_xu_ly_trung_testpng():
    if not coords:
        print("Bạn chưa chọn vùng!")
        return

    print("\n--- Template Matching với test.png ---")

    img_path = os.path.join("buttons", "test.png")
    if not os.path.exists(img_path):
        print(f"Lỗi: Không có {img_path}")
        return

    x_sorted = sorted([coords['x1'], coords['x2']])
    y_sorted = sorted([coords['y1'], coords['y2']])
    bbox = (x_sorted[0], y_sorted[0], x_sorted[1], y_sorted[1])

    # Chụp màn hình
    img_screen = ImageGrab.grab(bbox)
    img_screen = cv2.cvtColor(np.array(img_screen), cv2.COLOR_RGB2BGR)

    # Ảnh mẫu
    template = cv2.imread(img_path, cv2.IMREAD_COLOR)
    h, w = template.shape[:2]

    # Template Matching
    result = cv2.matchTemplate(img_screen, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.85  # chỉ xử lý khi >= 0.85
    loc = np.where(result >= threshold)

    points = []
    for pt in zip(*loc[::-1]):
        # Chỉ thêm nếu không gần điểm đã có (lọc theo nửa kích thước mẫu)
        if not any(abs(pt[0]-p[0]) < w//2 and abs(pt[1]-p[1]) < h//2 for p in points):
            points.append(pt)

    if not points:
        print("Không tìm thấy khớp (≥0.85).")
        return

    for i, (px, py) in enumerate(points, 1):
        abs_x = x_sorted[0] + px
        abs_y = y_sorted[0] + py
        print(f"Điểm {i}: ({abs_x},{abs_y}), độ khớp >= {threshold}")
        thuc_hien_thao_tac_tai_diem_trung("test.png", abs_x, abs_y, w, h)



# --- Hàm thao tác ---
def thuc_hien_thao_tac_tai_diem_trung(text, x, y, w, h):
    print(f"  -> Xử lý {text} tại ({x},{y}), size=({w}x{h})")
    time.sleep(0.5)


# --- GUI ---
root = tk.Tk()
root.title("Công cụ tìm & xử lý điểm trùng")

btn1 = tk.Button(root, text="1. Chọn vùng màn hình", command=chon_vung)
btn1.pack(pady=10, padx=20)

btn2 = tk.Button(root, text="2. OCR - Tìm điểm trùng", command=dem_va_xu_ly_diem_trung)
btn2.pack(pady=10, padx=20)

btn3 = tk.Button(root, text="3. Template Matching test.png", command=dem_va_xu_ly_trung_testpng)
btn3.pack(pady=10, padx=20)

root.mainloop()
