import tkinter as tk
import ctypes
from PIL import ImageGrab, ImageTk, ImageDraw
import pyautogui
import time
# Bật DPI awareness để lấy full resolution
ctypes.windll.user32.SetProcessDPIAware()

# --- Biến toàn cục để lưu trữ tọa độ và các widget ---
coords = {}
label_raw_coords = None
label_point_coords = None
entry_ratio_x = None
entry_ratio_y = None

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

        if label_raw_coords:
            label_raw_coords.config(text=f"Tọa độ đã chọn: (x1={coords['x1']}, y1={coords['y1']}), (x2={coords['x2']}, y2={coords['y2']})")
        print(f"Đã chọn vùng: x1={coords['x1']}, y1={coords['y1']}, x2={coords['x2']}, y2={coords['y2']}")

    canvas.bind("<Button-1>", start_select)
    canvas.bind("<B1-Motion>", update_select)
    canvas.bind("<ButtonRelease-1>", end_select)
    root_select.bind("<Escape>", lambda e: root_select.destroy())
    root_select.mainloop()

# --- Hàm hiển thị pop-up với điểm ---
def show_point_popup(bbox, point):
    x1, y1, x2, y2 = bbox
    px, py = point

    # Chụp ảnh của vùng đã chọn
    try:
        img = ImageGrab.grab(bbox=bbox)
        popup = tk.Toplevel()
        popup.title(f"Điểm tại ({px}, {py})")
        popup.attributes("-topmost", True)

        tk_img = ImageTk.PhotoImage(img)
        canvas = tk.Canvas(popup, width=img.width, height=img.height)
        canvas.create_image(0, 0, image=tk_img, anchor="nw")
        canvas.image = tk_img  # Keep a reference

        # Tính toán tọa độ tương đối của điểm trên ảnh
        relative_x = px - x1
        relative_y = py - y1

        # Vẽ một hình tròn nhỏ tại tọa độ điểm
        point_radius = 5
        canvas.create_oval(relative_x - point_radius, relative_y - point_radius,
                             relative_x + point_radius, relative_y + point_radius,
                             fill="red", outline="red")
        canvas.pack()

    except Exception as e:
        print(f"Lỗi khi hiển thị pop-up: {e}")

# --- Hàm tính toán và hiển thị tọa độ điểm ---
def tinh_va_hien_thi_diem():
    if not coords:
        if label_raw_coords:
            label_raw_coords.config(text="Bạn chưa chọn vùng!")
        if label_point_coords:
            label_point_coords.config(text="")
        return

    try:
        ratio_x = float(entry_ratio_x.get())
        ratio_y = float(entry_ratio_y.get())
    except ValueError:
        if label_point_coords:
            label_point_coords.config(text="Lỗi: Vui lòng nhập số hợp lệ cho tỷ lệ!")
        return

    # Sắp xếp tọa độ để đảm bảo x1 < x2 và y1 < y2
    x_sorted = sorted([coords['x1'], coords['x2']])
    y_sorted = sorted([coords['y1'], coords['y2']])
    bbox = (x_sorted_min, y_sorted_min, x_sorted_max, y_sorted_max) = (x_sorted.pop(0), y_sorted.pop(0), x_sorted.pop(), y_sorted.pop())

    x1, y1, x2, y2 = bbox

    # Tính toán tọa độ điểm
    x_point = int(x1 + (x2 - x1) * ratio_x)
    y_point = int(y1 + (y2 - y1) * ratio_y)

    # Hiển thị tọa độ điểm trên giao diện chính
    if label_point_coords:
        label_point_coords.config(text=f"Tọa độ điểm: ({x_point}, {y_point})")
        #time.sleep(3)
        #pyautogui.click(x_point,y_point)
    print(f"Tọa độ điểm đã tính: ({x_point}, {y_point})")

    # Hiển thị pop-up
    show_point_popup(bbox, (x_point, y_point))

# --- Giao diện chính ---
def main_gui():
    global label_raw_coords, label_point_coords, entry_ratio_x, entry_ratio_y

    root = tk.Tk()
    root.title("Công cụ xác định tọa độ điểm")

    btn_chon = tk.Button(root, text="1. Chọn Vùng", command=chon_vung)
    btn_chon.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

    tk.Label(root, text="Tỷ lệ X (0-1)").grid(row=1, column=0, padx=5, pady=2, sticky="W")
    entry_ratio_x = tk.Entry(root)
    entry_ratio_x.insert(0, "0.5")
    entry_ratio_x.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(root, text="Tỷ lệ Y (0-1)").grid(row=2, column=0, padx=5, pady=2, sticky="W")
    entry_ratio_y = tk.Entry(root)
    entry_ratio_y.insert(0, "0.5")
    entry_ratio_y.grid(row=2, column=1, padx=5, pady=2)

    label_raw_coords = tk.Label(root, text="Tọa độ đã chọn: Chưa có", font=("Arial", 10), fg="blue")
    label_raw_coords.grid(row=3, column=0, columnspan=2, pady=5)

    label_point_coords = tk.Label(root, text="Tọa độ điểm: Chưa có", font=("Arial", 10), fg="green")
    label_point_coords.grid(row=4, column=0, columnspan=2, pady=5)

    btn_process = tk.Button(root, text="2. Tính & Hiển thị Điểm", command=tinh_va_hien_thi_diem)
    btn_process.grid(row=5, column=0, columnspan=2, pady=10, padx=10)

    root.mainloop()

# Chạy chương trình
if __name__ == "__main__":
    main_gui()