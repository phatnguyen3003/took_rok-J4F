import tkinter as tk
from PIL import ImageGrab
import os
import ctypes

def chon_vung(callback):
    coords = {}

    # Lấy kích thước màn hình thật (bỏ qua Windows scaling)
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()  # Cho phép app lấy kích thước thật
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # Tạo cửa sổ full màn hình thật
    selector = tk.Toplevel()
    selector.overrideredirect(True)  # Bỏ thanh tiêu đề
    selector.geometry(f"{screen_width}x{screen_height}+0+0")
    selector.attributes("-topmost", True)
    selector.attributes("-alpha", 0.3)
    selector.configure(bg='black')

    # Canvas phủ kín màn hình
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

        # Lấy index từ closure callback
        i = None
        for cell in callback.__closure__ or []:
            if isinstance(cell.cell_contents, int):
                i = cell.cell_contents
                break

        # Lưu ảnh debug
        os.makedirs("debug", exist_ok=True)
        img = ImageGrab.grab()
        crop = img.crop((x1, y1, x2, y2))
        filename = f"vung_{i+1}.png" if i is not None else "vung_unknown.png"
        crop.save(os.path.join("debug", filename))

        # In ra terminal
        if i is not None:
            print(f"Đã lưu vùng {i+1}: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
        else:
            print(f"Đã lưu vùng (không rõ index): x1={x1}, y1={y1}, x2={x2}, y2={y2}")

        # Gửi tọa độ về callback
        callback({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
        selector.destroy()

    def cancel(event=None):
        selector.destroy()

    canvas.bind("<Button-1>", start_select)
    canvas.bind("<B1-Motion>", update_select)
    canvas.bind("<ButtonRelease-1>", end_select)
    selector.bind("<Escape>", cancel)

    selector.mainloop()
