import customtkinter as ctk
import threading
import queue
import time
import json
import os
import script
from script import chay_da, chay_go, chay_lt, chay_vang, tac_vu_thong_thuong, trinh_sat,chay_gems,chay_do_hang

# ----------------------------------------------------------------------
# Lớp GUI chính
# ----------------------------------------------------------------------
class QuanLyVungGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Quản lý vùng")
        self.geometry("600x400")

        # Hàng đợi để gửi tác vụ đến luồng phụ
        self.task_queue = queue.Queue()
        
        # Biến cờ để kiểm soát việc dừng/chạy
        self.running = False
        # THAY ĐỔI: Biến cờ để quản lý trạng thái tác vụ thông thường đang chạy
        self.is_common_task_running = False
        # Lưu trữ thời gian đếm ngược và chế độ của mỗi tác vụ
        self.countdowns = {}  # {(vung_id, dq): {'master_time_left': int, 'che_do': int}}
        # Lưu trữ các widget label
        self.labels = {}
        # ID của hàm after() để hủy vòng lặp cập nhật GUI
        self.after_id = None
        # Lưu danh sách các vung_id để chạy tac_vu_thong_thuong
        self.vung_ids = []

        # Thêm biến để quản lý thời gian chờ 40 phút và trạng thái lần chạy đầu tiên
        self.common_task_cooldown_minutes = 40
        self.common_task_last_completed_time = 0
        self.initial_common_task_run = False
        self.all_masters_initialized = False

        # Tạo khung chính
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Khung điều khiển
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.pack(fill="x", pady=(0, 10))

        # Nút chạy & dừng
        self.btn_chay = ctk.CTkButton(self.control_frame, text="Chạy", command=self.start_queue)
        self.btn_chay.pack(side="left", padx=5)
        self.btn_dung = ctk.CTkButton(self.control_frame, text="Dừng", command=self.stop_queue)
        self.btn_dung.pack(side="left", padx=5)
        
        # Nhãn trạng thái tổng quan
        self.lbl_global_status = ctk.CTkLabel(self.control_frame, text="Hệ thống đang chờ...")
        self.lbl_global_status.pack(side="left", padx=10)
        
        # Nhãn trạng thái tác vụ thông thường
        self.common_task_label = ctk.CTkLabel(self.control_frame, text="Tác vụ thông thường: Đang chờ...")
        self.common_task_label.pack(side="left", padx=10)

        # Khung hiển thị countdown
        self.countdown_frame = ctk.CTkFrame(self.main_frame)
        self.countdown_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(self.countdown_frame, text="Trạng thái đếm ngược").pack(pady=(5, 0))
        self.frame_cd = ctk.CTkScrollableFrame(self.countdown_frame)
        self.frame_cd.pack(pady=10, padx=10, fill="both", expand=True)
        
    def load_data(self):
        """
        Tải dữ liệu từ file JSON.
        Để chạy code này, bạn cần có một file `dulieu.json`
        trong thư mục `data` cùng cấp với file Python này.
        """
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, "data", "dulieu.json")
            with open(data_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except FileNotFoundError:
            print("Lỗi: Không tìm thấy file dulieu.json.")
            return

        vung_data = config.get("vung", {})
        if not vung_data:
            print("Dữ liệu vùng trống trong dulieu.json")
            return
        
        # Sắp xếp các vung_id để đảm bảo thứ tự
        self.vung_ids = sorted(list(vung_data.keys()))
        
        for vung_id in self.vung_ids:
            info = vung_data[vung_id]
            # Chắc chắn rằng so_dq được chuyển đổi thành int một cách chính xác
            so_dq = int(info.get("dq", 1))
            che_do = int(info.get("che_do", 1))
            label_che_do="ĐQ"
            if che_do==6:
                label_che_do="Trinh Sát"
            for dq in range(1, so_dq + 1):
                key = (vung_id, dq)
                # Đưa tất cả các tác vụ vào hàng đợi ban đầu
                self.task_queue.put(('master', vung_id, dq, che_do))
                # Khởi tạo thời gian đếm ngược
                self.countdowns[key] = {
                    'master_time_left': -1, # Dùng -1 để đánh dấu tác vụ chưa chạy lần nào
                    'che_do': che_do,
                }
                # Tạo label cho tác vụ
                lbl = ctk.CTkLabel(self.frame_cd, text=f"Vùng {vung_id} - {label_che_do} {dq}: Đang chờ...")
                lbl.pack(anchor="w", pady=2, padx=5)
                self.labels[key] = lbl

    def start_queue(self):
        if not self.running:
            self.running = True
            # Load dữ liệu nếu hàng đợi rỗng
            if not self.countdowns:
                self.load_data()
            
            # Bắt đầu luồng phụ để xử lý các tác vụ
            threading.Thread(target=self.run_worker, daemon=True).start()
            
            # Bắt đầu vòng lặp cập nhật GUI mỗi giây
            self.after_id = self.after(1000, self._update_gui)

    def stop_queue(self):
        if self.running:
            self.running = False
            if self.after_id:
                self.after_cancel(self.after_id)
            # Dọn dẹp hàng đợi để luồng phụ có thể dừng
            with self.task_queue.mutex:
                self.task_queue.queue.clear()
            self.lbl_global_status.configure(text="Hệ thống đã dừng.")
            self.common_task_label.configure(text="Tác vụ thông thường: Dừng")
            
    def run_worker(self):
        """Luồng phụ để xử lý các tác vụ một cách an toàn."""
        while self.running:
            try:
                task_type, *task_args = self.task_queue.get(timeout=1)
                
                if task_type == 'master':
                    vung_id, dq, che_do = task_args
                    
                    # Ghi lại thời gian bắt đầu
                    start_time = time.time()
                    
                    # Gọi hàm chế độ
                    if che_do == 1:
                        tg = chay_lt(vung_id)
                    elif che_do == 2:
                        tg = chay_go(vung_id)
                    elif che_do == 3:
                        tg = chay_da(vung_id)
                    elif che_do == 4:
                        tg = chay_vang(vung_id)
                    elif che_do == 5:
                        tg = chay_gems(vung_id)
                    elif che_do == 6:
                        tg = trinh_sat(vung_id)
                    elif che_do == 7:
                        tg = chay_do_hang(vung_id)
                    else:
                        tg = 10
                    
                    # Ghi lại thời gian kết thúc và tính toán duration
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    # Cập nhật thời gian đếm ngược chính mới vào biến chung
                    key = (vung_id, dq)
                    if self.countdowns[key]['master_time_left'] == -1:
                        self.countdowns[key]['master_time_left'] = int(tg)
                    
                    print(f"Vùng {vung_id} - ĐQ {dq}: Hoàn thành tác vụ chính lúc {time.strftime('%H:%M:%S', time.localtime(end_time))}, thời gian chạy: {duration:.2f}s")
                    
                elif task_type == 'common':
                    # THAY ĐỔI: Bật cờ khi tác vụ phụ bắt đầu
                    self.is_common_task_running = True
                    self.common_task_label.configure(text="Tác vụ thông thường: Đang chạy...")
                    print("Bắt đầu chạy tác vụ thông thường...")
                    
                    common_start_time = time.time()
                    
                    for vung_id_common_str in self.vung_ids:
                        try:
                            vung_id_common = int(vung_id_common_str)
                        except ValueError:
                            print(f"Lỗi: Không thể chuyển đổi '{vung_id_common_str}' thành số nguyên.")
                            continue
                        
                        print(f"Chạy tác vụ thông thường cho vùng {vung_id_common}")
                        tac_vu_thong_thuong(vung_id_common)
                        if not self.running:
                            break
                    
                    common_end_time = time.time()
                    common_duration = common_end_time - common_start_time
                    print(f"Tác vụ thông thường: Hoàn thành lúc {time.strftime('%H:%M:%S', time.localtime(common_end_time))}, thời gian chạy: {common_duration:.2f}s")
                    
                    print("Hoàn thành tất cả các tác vụ thông thường.")
                    # THAY ĐỔI: Tắt cờ khi tác vụ phụ hoàn thành
                    self.is_common_task_running = False
                    self.common_task_last_completed_time = time.time()
                    self.common_task_label.configure(text="Tác vụ thông thường: Đã hoàn thành")
            except queue.Empty:
                continue
            except NameError as ne:
                print(f"Lỗi: {ne}. Tác vụ không thể chạy vì hàm chưa được định nghĩa.")
                self.running = False
            except Exception as e:
                print(f"Lỗi khi xử lý tác vụ: {e}")
                self.running = False
                
    def _update_gui(self):
        """Hàm được gọi mỗi giây để cập nhật GUI trên luồng chính."""
        if not self.running:
            return
        
        is_all_masters_initialized = all(self.countdowns[k]['master_time_left'] > -1 for k in self.countdowns)
        
        for key in sorted(list(self.countdowns.keys())):
            vung_id, dq = key
            che_do = self.countdowns[key]['che_do']
            label_che_do = "ĐQ"
            if che_do == 6:
                label_che_do = "Trinh Sát"
            master_time = self.countdowns[key]['master_time_left']

            if master_time > 0:
                self.countdowns[key]['master_time_left'] = int(master_time) - 1
                self.labels[key].configure(text=f"Vùng {vung_id} - {label_che_do} {dq}: Còn lại {self.countdowns[key]['master_time_left']}s")
            # THAY ĐỔI: Chỉ đưa tác vụ vào hàng đợi nếu tác vụ phụ không chạy
            elif master_time == 0 and not self.is_common_task_running:
                self.labels[key].configure(text=f"Vùng {vung_id} - {label_che_do} {dq}: Đã sẵn sàng!")
                self.task_queue.put(('master', vung_id, dq, che_do))
                self.countdowns[key]['master_time_left'] = -1
        
        if is_all_masters_initialized and self.task_queue.empty() and not self.is_common_task_running:
            time_since_common_task = time.time() - self.common_task_last_completed_time
            time_to_wait = self.common_task_cooldown_minutes * 60

            should_run_common_task = False
            if not self.initial_common_task_run:
                should_run_common_task = True
            elif time_since_common_task >= time_to_wait:
                should_run_common_task = True
            
            if should_run_common_task:
                self.lbl_global_status.configure(text="Tất cả các tác vụ chính đã hoàn thành. Chuẩn bị chạy tác vụ thông thường...")
                self.task_queue.put(('common',))
                # THAY ĐỔI: Bỏ common_task_queued vì đã sử dụng is_common_task_running
                self.initial_common_task_run = True
                self.common_task_last_completed_time = time.time()
            else:
                remaining_time = int(time_to_wait - time_since_common_task)
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                self.lbl_global_status.configure(text=f"Tác vụ thông thường sẽ chạy lại sau {minutes:02d}:{seconds:02d}")
                self.common_task_label.configure(text="Tác vụ thông thường: Đang chờ")

        elif not is_all_masters_initialized:
            self.lbl_global_status.configure(text="Đang chờ các tác vụ chính khởi động...")
            self.common_task_label.configure(text="Tác vụ thông thường: Đang chờ...")
        elif not self.is_common_task_running:
            self.lbl_global_status.configure(text="Hệ thống đang chờ tác vụ chính hoàn thành...")
            self.common_task_label.configure(text="Tác vụ thông thường: Đang chờ...")
        
        self.after_id = self.after(1000, self._update_gui)

def mo_quan_ly_vung():
    app = QuanLyVungGUI()
    app.mainloop()

if __name__ == "__main__":
    mo_quan_ly_vung()
