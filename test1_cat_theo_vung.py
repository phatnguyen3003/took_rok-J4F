import tkinter as tk
from PIL import ImageGrab, ImageTk
import ctypes

# --- Cấu hình ---
SCALE = 1.0  # scale mặc định của màn hình (125%)
coords = {}   # Lưu tọa độ vùng chọn

# Bật DPI awareness để lấy full resolution
ctypes.windll.user32.SetProcessDPIAware()

# Hàm chọn vùng trên màn hình
def chon_vung():
    global coords
    coords.clear()

    # Lấy kích thước thật của màn hình
    root = tk.Toplevel()
    root.overrideredirect(True)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.3)
    root.configure(bg='black')

    canvas = tk.Canvas(root, cursor="cross", bg='gray', highlightthickness=0)
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
        root.destroy()

    canvas.bind("<Button-1>", start_select)
    canvas.bind("<B1-Motion>", update_select)
    canvas.bind("<ButtonRelease-1>", end_select)
    root.bind("<Escape>", lambda e: root.destroy())

    root.mainloop()

# Hàm cắt ảnh theo tọa độ đã chọn và tỷ lệ margin
def cat_anh():
    if not coords:
        print("Bạn chưa chọn vùng!")
        return

    try:
        left_margin = float(entry_left.get())
        right_margin = float(entry_right.get())
        top_margin = float(entry_top.get())
        bottom_margin = float(entry_bottom.get())
    except ValueError:
        print("Vui lòng nhập số hợp lệ cho tỷ lệ!")
        return

    # Sắp xếp tọa độ
    x_sorted = sorted([coords['x1'], coords['x2']])
    y_sorted = sorted([coords['y1'], coords['y2']])
    x1, x2 = x_sorted
    y1, y2 = y_sorted

    width = x2 - x1
    height = y2 - y1

    # Nhân scale khi chụp để khớp pixel thật
    box = (
        int((x1 + width * left_margin) * SCALE),
        int((y1 + height * top_margin) * SCALE),
        int((x2 - width * right_margin) * SCALE),
        int((y2 - height * bottom_margin) * SCALE)
    )

    img = ImageGrab.grab(bbox=box)
    hien_popup(img)

# Hàm hiển thị ảnh popup trong 10 giây
def hien_popup(img):
    popup = tk.Toplevel(root)
    popup.title("Ảnh Cắt Xem Trước")
    popup.attributes("-topmost", True)

    tk_img = ImageTk.PhotoImage(img)
    label = tk.Label(popup, image=tk_img)
    label.image = tk_img
    label.pack()

    popup.after(10000, popup.destroy)

# Giao diện chính
root = tk.Tk()
root.title("Chọn & Cắt Ảnh Theo Tỷ Lệ (Scale 1.25)")

btn_chon = tk.Button(root, text="Chọn Vùng", command=chon_vung)
btn_chon.grid(row=0, column=0, columnspan=2, pady=10)

tk.Label(root, text="Trái (%)").grid(row=1, column=0)
entry_left = tk.Entry(root)
entry_left.insert(0, "0.0")
entry_left.grid(row=1, column=1)

tk.Label(root, text="Phải (%)").grid(row=2, column=0)
entry_right = tk.Entry(root)
entry_right.insert(0, "0.0")
entry_right.grid(row=2, column=1)

tk.Label(root, text="Trên (%)").grid(row=3, column=0)
entry_top = tk.Entry(root)
entry_top.insert(0, "0.0")
entry_top.grid(row=3, column=1)

tk.Label(root, text="Dưới (%)").grid(row=4, column=0)
entry_bottom = tk.Entry(root)
entry_bottom.insert(0, "0.0")
entry_bottom.grid(row=4, column=1)

btn_cat = tk.Button(root, text="Cắt & Xem", command=cat_anh)
btn_cat.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()
