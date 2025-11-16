import tkinter as tk
import ctypes
import pyautogui
import time

def chon_vung():
    """
    Cho phép người dùng chọn một vùng trên màn hình và trả về tọa độ.
    Returns:
        tuple: (x1, y1, x2, y2) hoặc None nếu người dùng hủy bỏ.
    """
    selection_coords = None
    
    # Lấy kích thước màn hình thật (bỏ qua Windows scaling)
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # Sử dụng tk.Toplevel() để tạo cửa sổ con
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
        x_start, y_start = event.x_root, event.y_root
        rect = canvas.create_rectangle(x_start, y_start, x_start, y_start,
                                       outline='red', width=2, tags="rect")
        canvas.x_start = x_start
        canvas.y_start = y_start

    def update_select(event):
        if rect:
            x_start = canvas.x_start
            y_start = canvas.y_start
            canvas.coords("rect", x_start, y_start, event.x_root, event.y_root)

    def end_select(event):
        nonlocal selection_coords
        x_end, y_end = event.x_root, event.y_root
        x1, x2 = sorted([canvas.x_start, x_end])
        y1, y2 = sorted([canvas.y_start, y_end])
        
        selection_coords = (x1, y1, x2, y2)
        selector.destroy()

    def cancel(event=None):
        nonlocal selection_coords
        selection_coords = None
        selector.destroy()

    canvas.bind("<Button-1>", start_select)
    canvas.bind("<B1-Motion>", update_select)
    canvas.bind("<ButtonRelease-1>", end_select)
    selector.bind("<Escape>", cancel)
    
    selector.wait_window(selector)
    
    return selection_coords

def thuc_hien_vuot(x1, y1, x2, y2, huong, khoang_cach, thoi_gian=0.2):
    """
    Thực hiện thao tác vuốt mô phỏng để cuộn màn hình.
    """
    if None in (x1, y1, x2, y2):
        print("Lỗi: Chưa có tọa độ vùng. Vui lòng chọn vùng trước.")
        return

    try:
        khoang_cach = int(khoang_cach)
    except (ValueError, TypeError):
        print("Lỗi: Khoảng cách không hợp lệ. Vui lòng nhập số.")
        return

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    
    start_x, start_y = center_x, center_y
    end_x, end_y = center_x, center_y

    # Tính toán điểm bắt đầu và kết thúc của thao tác vuốt
    # Bắt đầu từ 1/3 khoảng cách về phía ngược lại, kết thúc tại điểm cuối cùng
    if huong == "trai":
        start_x += khoang_cach // 3
        end_x -= khoang_cach
    elif huong == "phai":
        start_x -= khoang_cach // 3
        end_x += khoang_cach
    elif huong == "tren":
        start_y += khoang_cach // 3
        end_y -= khoang_cach
    elif huong == "duoi":
        start_y -= khoang_cach // 3
        end_y += khoang_cach

    # Di chuyển chuột đến điểm bắt đầu
    print(f"Di chuyển chuột đến điểm bắt đầu vuốt: ({start_x}, {start_y})")
    pyautogui.moveTo(start_x, start_y, duration=0.2)

    # Giữ chuột và kéo đến điểm kết thúc để cuộn màn hình
    print(f"Giữ chuột và kéo đến điểm kết thúc: ({end_x}, {end_y})")
    pyautogui.dragTo(end_x, end_y, duration=thoi_gian, button='left')
    
    print(f"Đã vuốt {huong} với khoảng cách {khoang_cach} xong.")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Test Chức Năng Vuốt")
        self.geometry("300x350")
        self.coords = (None, None, None, None)

        self.khoang_cach = {
            "trai": tk.StringVar(value="100"),
            "phai": tk.StringVar(value="100"),
            "tren": tk.StringVar(value="100"),
            "duoi": tk.StringVar(value="100")
        }

        self.create_widgets()
        
        # Thêm binding cho các phím mũi tên trên cửa sổ chính
        self.bind("<Left>", self.xu_ly_phim_mui_ten)
        self.bind("<Right>", self.xu_ly_phim_mui_ten)
        self.bind("<Up>", self.xu_ly_phim_mui_ten)
        self.bind("<Down>", self.xu_ly_phim_mui_ten)
        
    def create_widgets(self):
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        btn_chon_vung = tk.Button(main_frame, text="1. Chọn Vùng", command=self.xu_ly_chon_vung)
        btn_chon_vung.pack(fill=tk.X, pady=5)
        
        self.coords_label = tk.Label(main_frame, text="Tọa độ: Chưa chọn", fg="blue")
        self.coords_label.pack(pady=5)
        
        vuot_frame = tk.LabelFrame(main_frame, text="2. Thực hiện Vuốt", padx=5, pady=5)
        vuot_frame.pack(fill=tk.X, pady=10)
        
        self.create_vuot_button(vuot_frame, "PHẢI", "phai")
        self.create_vuot_button(vuot_frame, "TRÁI", "trai")
        self.create_vuot_button(vuot_frame, "TRÊN", "tren")
        self.create_vuot_button(vuot_frame, "DƯỚI", "duoi")
        
        # Thêm label thông báo về phím tắt
        info_label = tk.Label(main_frame, text="Hoặc dùng phím mũi tên để vuốt", fg="gray")
        info_label.pack(pady=5)
        
    def create_vuot_button(self, parent, text, huong):
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        btn = tk.Button(frame, text=f"Vuốt {text}", command=lambda: self.xu_ly_vuot(huong))
        btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        label = tk.Label(frame, text="Khoảng cách:")
        label.pack(side=tk.LEFT, padx=(5, 2))
        
        entry = tk.Entry(frame, textvariable=self.khoang_cach[huong], width=5)
        entry.pack(side=tk.LEFT)

    def xu_ly_chon_vung(self):
        self.coords = chon_vung()
        
        if self.coords:
            x1, y1, x2, y2 = self.coords
            self.coords_label.config(text=f"Tọa độ: x1={x1}, y1={y1}, x2={x2}, y2={y2}", fg="green")
            print("Đã chọn vùng thành công.")
        else:
            self.coords_label.config(text="Tọa độ: Đã hủy", fg="red")
            print("Đã hủy chọn vùng.")

    def xu_ly_vuot(self, huong):
        x1, y1, x2, y2 = self.coords
        if x1 is None:
            self.coords_label.config(text="Lỗi: Vui lòng chọn vùng trước!", fg="red")
            return
        
        khoang_cach_str = self.khoang_cach[huong].get()
        print(f"\nĐang thực hiện vuốt {huong} với khoảng cách {khoang_cach_str}...")
        
        try:
            khoang_cach_int = int(khoang_cach_str)
            thuc_hien_vuot(x1, y1, x2, y2, huong, khoang_cach_int)
        except ValueError:
            print("Lỗi: Khoảng cách phải là một số nguyên hợp lệ.")
            self.coords_label.config(text="Lỗi: Khoảng cách không hợp lệ!", fg="red")
        print("Hoàn tất.")

    def xu_ly_phim_mui_ten(self, event):
        """Hàm xử lý sự kiện khi người dùng nhấn phím mũi tên."""
        if self.coords[0] is None:
            # Nếu chưa chọn vùng, không làm gì cả
            return
            
        key = event.keysym
        huong = ""
        
        if key == "Left":
            huong = "trai"
        elif key == "Right":
            huong = "phai"
        elif key == "Up":
            huong = "tren"
        elif key == "Down":
            huong = "duoi"
            
        if huong:
            self.xu_ly_vuot(huong)
            
if __name__ == "__main__":
    app = App()
    app.mainloop()
