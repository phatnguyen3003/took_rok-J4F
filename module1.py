import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageGrab
import pytesseract
import re
import os
import time
import ctypes

# Thêm dòng này để cấu hình đường dẫn Tesseract OCR cho Windows
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except:
    pass

# Thêm thư viện ctypes để lấy kích thước màn hình vật lý
try:
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()  # Cho phép app lấy kích thước thật
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
except:
    screen_width = 1920
    screen_height = 1080

# --- Hàm chọn vùng màn hình (đã sửa lỗi để tương thích) ---
def chon_vung(callback):
    coords = {}

    selector = tk.Toplevel()
    selector.overrideredirect(True)
    selector.geometry(f"{screen_width}x{screen_height}+0+0")
    selector.attributes("-topmost", True)
    selector.attributes("-alpha", 0.3)
    selector.configure(bg='black')

    canvas = tk.Canvas(selector, cursor="cross", bg='gray', highlightthickness=0,
                       width=screen_width, height=screen_height)
    canvas.pack(fill=tk.BOTH, expand=True)

    rect = None

    def start_select(event):
        nonlocal rect
        canvas.delete("rect")
        coords['x1'], coords['y1'] = event.x_root, event.y_root
        rect = canvas.create_rectangle(event.x_root, event.y_root, event.x_root, event.y_root,
                                       outline='red', width=2, tags="rect")

    def update_select(event):
        if rect:
            canvas.coords("rect", coords['x1'], coords['y1'], event.x_root, event.y_root)

    def end_select(event):
        coords['x2'], coords['y2'] = event.x_root, event.y_root
        x1, x2 = sorted([coords['x1'], coords['x2']])
        y1, y2 = sorted([coords['y1'], coords['y2']])

        # Truyền tọa độ về callback dưới dạng tuple
        callback((x1, y1, x2, y2))
        
        selector.destroy()

    def cancel(event=None):
        selector.destroy()

    canvas.bind("<Button-1>", start_select)
    canvas.bind("<B1-Motion>", update_select)
    canvas.bind("<ButtonRelease-1>", end_select)
    selector.bind("<Escape>", cancel)

    selector.mainloop()

# --- Hàm trích xuất từ màn hình (giữ nguyên) ---
def tx_tu_man_hinh_test(region_coords, crop_ratio=(0, 0, 0, 0), mode="all"):
    if not region_coords or len(region_coords) != 4:
        print("Lỗi: Vùng chưa được chọn hoặc tọa độ không hợp lệ.")
        return "", None
    
    x1, y1, x2, y2 = region_coords
    
    try:
        # Sử dụng ImageGrab có thể gặp vấn đề lệch vùng trên màn hình phụ
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    except Exception as e:
        print(f"Lỗi khi chụp màn hình: {e}")
        return "", None
    
    width, height = img.size
    
    left_margin = int(width * crop_ratio[0])
    right_margin = int(width * crop_ratio[1])
    top_margin = int(height * crop_ratio[2])
    bottom_margin = int(height * crop_ratio[3])
    
    if left_margin + right_margin >= width or top_margin + bottom_margin >= height:
        print("Lỗi: Tỷ lệ cắt quá lớn, không còn vùng để trích xuất.")
        return "", None
        
    crop_img = img.crop((
        left_margin,
        top_margin,
        width - right_margin,
        height - bottom_margin
    ))
    
    try:
        text_ocr_raw = pytesseract.image_to_string(crop_img, config='--psm 6').strip()
    except pytesseract.TesseractNotFoundError:
        messagebox.showerror("Lỗi", "Không tìm thấy Tesseract OCR. Vui lòng kiểm tra lại cài đặt.")
        return "", None
    
    if mode == "toado":
        text_trich_xuat = re.sub(r'[^xyXY0-9,.]+', '', text_ocr_raw)
    elif mode == "so":
        text_trich_xuat = re.sub(r'[^0-9.]+', '', text_ocr_raw)
    elif mode == "chu":
        text_trich_xuat = re.sub(r'[^a-zA-Z]+', '', text_ocr_raw)
    elif mode == "all":
        text_trich_xuat = text_ocr_raw
    else:
        print(f"Chế độ '{mode}' không hợp lệ, mặc định dùng 'all'")
        text_trich_xuat = text_ocr_raw
        
    return text_trich_xuat, crop_img

# --- Giao diện người dùng (GUI) ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trình Test OCR Màn hình")
        self.geometry("400x400")
        
        self.region_coords = None
        
        self.label_coords = tk.Label(self, text="Tọa độ vùng: Chưa chọn")
        self.label_coords.pack(pady=10)
        
        self.btn_select_region = tk.Button(self, text="Chọn Vùng", command=self.select_region)
        self.btn_select_region.pack(pady=5)
        
        self.frame_crop = tk.LabelFrame(self, text="Tỷ lệ cắt (0.0 - 1.0)")
        self.frame_crop.pack(pady=10, padx=10, fill="x")
        
        self.entries_crop = {}
        for i, name in enumerate(["Trái", "Phải", "Trên", "Dưới"]):
            frame = tk.Frame(self.frame_crop)
            frame.pack(side="left", padx=5)
            tk.Label(frame, text=f"{name}:").pack()
            entry = tk.Entry(frame, width=5)
            entry.insert(0, "0.0")
            entry.pack()
            self.entries_crop[name] = entry

        self.frame_mode = tk.LabelFrame(self, text="Chế độ Trích xuất")
        self.frame_mode.pack(pady=10, padx=10, fill="x")

        self.mode_var = tk.StringVar(value="all")
        modes = ["all", "toado", "so", "chu"]
        for mode in modes:
            tk.Radiobutton(self.frame_mode, text=mode.capitalize(), variable=self.mode_var, value=mode).pack(side="left", padx=5)

        self.btn_run_test = tk.Button(self, text="Chạy Test OCR", command=self.run_test)
        self.btn_run_test.pack(pady=10)
        
        self.text_result = tk.Text(self, height=5, width=40)
        self.text_result.pack(pady=10)

    def select_region(self):
        self.withdraw()
        time.sleep(0.2)
        chon_vung(self.update_coordinates)
        
    def update_coordinates(self, coords):
        self.region_coords = coords
        self.label_coords.config(text=f"Tọa độ vùng: ({coords[0]}, {coords[1]}) đến ({coords[2]}, {coords[3]})")
        self.deiconify()

    def run_test(self):
        if not self.region_coords:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn vùng màn hình trước.")
            return

        try:
            crop_ratio = (
                float(self.entries_crop["Trái"].get()),
                float(self.entries_crop["Phải"].get()),
                float(self.entries_crop["Trên"].get()),
                float(self.entries_crop["Dưới"].get())
            )
            mode = self.mode_var.get()

            result, crop_img = tx_tu_man_hinh_test(self.region_coords, crop_ratio, mode)
            
            if result is not None:
                self.text_result.delete(1.0, tk.END)
                self.text_result.insert(tk.END, result)
                self.show_crop_info_popup(crop_img)

        except ValueError:
            messagebox.showerror("Lỗi", "Tỷ lệ cắt phải là số thập phân.")

    def show_crop_info_popup(self, crop_img):
        popup = tk.Toplevel(self)
        popup.title("Ảnh vùng đã cắt")
        
        if crop_img:
            tk_image = ImageTk.PhotoImage(crop_img)
            label_image = tk.Label(popup, image=tk_image)
            label_image.image = tk_image
            label_image.pack(padx=10, pady=10)

            ok_button = tk.Button(popup, text="OK", command=popup.destroy)
            ok_button.pack(pady=5)
        else:
            label_text = tk.Label(popup, text="Không có ảnh để hiển thị.", padx=10, pady=10)
            label_text.pack()

if __name__ == "__main__":
    app = App()
    app.mainloop()