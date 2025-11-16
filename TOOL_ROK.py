import customtkinter as ctk
import tkinter as tk
import json
import os
from tkinter import filedialog, messagebox
from PIL import ImageGrab, ImageTk
import ctypes
from chon_vung_gui import chon_vung
from hang_doi import mo_quan_ly_vung

# Bật DPI awareness
ctypes.windll.user32.SetProcessDPIAware()

#================== GLOBAL =========================================================
config_path = os.path.join("data", "config.json")
duong_dan = ""
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        du_lieu = json.load(f)
        duong_dan = du_lieu.get("duong_dan", "")
else:
    print("Không tìm thấy file config.json")

du_lieu_cu = {}
duong_dan_du_lieu = os.path.join(duong_dan, r"data\dulieu.json")

if os.path.exists(duong_dan_du_lieu):
    with open(duong_dan_du_lieu, "r", encoding="utf-8") as f:
        try:
            du_lieu_cu = json.load(f)
        except json.JSONDecodeError:
            du_lieu_cu = {}

danh_sach_dropdown1 = []
danh_sach_dropdown2 = []
danh_sach_toa_do = []
danh_sach_entry_map_var = []  # Danh sách entry bán kính cho từng vùng

#=================== DEF ===========================================================
def ghi_vao_file_json(du_lieu_moi):
    duong_dan_file = os.path.join(duong_dan, r"data\config.json")
    du_lieu_cu = {}
    if os.path.exists(duong_dan_file):
        with open(duong_dan_file, "r", encoding="utf-8") as f:
            try:
                du_lieu_cu = json.load(f)
            except json.JSONDecodeError:
                pass

    du_lieu_cu.update(du_lieu_moi)

    with open(duong_dan_file, "w", encoding="utf-8") as f:
        json.dump(du_lieu_cu, f, ensure_ascii=False, indent=4)


def chon_thu_muc():
    global duong_dan
    new_path = filedialog.askdirectory(title="Chọn thư mục chứa file tool")
    if new_path:
        duong_dan = new_path
        entry_duong_dan.delete(0, "end")
        entry_duong_dan.insert(0, duong_dan)
        ghi_vao_file_json({"duong_dan": duong_dan})


#================ CỬA SỔ TÙY CHỈNH ===================
def cua_so_tc():
    so_vung_var = tk.StringVar()
    do_phan_giai_var = tk.StringVar(value="960x540")

    def chon_noi_dung(gia_tri_pg):
        do_phan_giai_var.set(gia_tri_pg)
        print("Độ phân giải đã chọn:", gia_tri_pg)

    def luu_gia_tri_sau_khi_nhan_enter(event=None):
        so_vung_var.set(entry_so_vung.get())
        print("Giá trị đã nhập là:", so_vung_var.get())

    def luu_cai_dat():
        du_lieu = {
            "so_vung": so_vung_var.get(),
            "Do_phan_giai": do_phan_giai_var.get(),
        }
        print("Lưu dữ liệu:", du_lieu)
        ghi_vao_file_json(du_lieu)

    cua_so_1 = ctk.CTkToplevel()
    cua_so_1.title("Tùy Chỉnh")
    cua_so_1.geometry("350x200")

    frame_top = ctk.CTkFrame(cua_so_1)
    frame_top.pack(pady=10)

    label_so_vung = ctk.CTkLabel(frame_top, text="Nhập Số Vùng:")
    label_so_vung.pack(side="left", padx=10)

    entry_so_vung = ctk.CTkEntry(frame_top, width=150)
    entry_so_vung.pack(side="left", padx=10)
    entry_so_vung.bind("<Return>", luu_gia_tri_sau_khi_nhan_enter)

    cac_gia_tri = ["960x540", "1280x720", "1600x900", "1920x1080"]
    dropdown = ctk.CTkOptionMenu(cua_so_1, values=cac_gia_tri, command=chon_noi_dung)
    dropdown.set(do_phan_giai_var.get())
    dropdown.pack(pady=10)

    btn_luu = ctk.CTkButton(cua_so_1, text="Lưu Cài Đặt", command=luu_cai_dat)
    btn_luu.pack(pady=10)


#================ CỬA SỔ CHẠY CODE ===================
def cua_so_chay():
    cua_so_2 = ctk.CTkToplevel()
    cua_so_2.title("Thiết Lập Chạy")
    cua_so_2.geometry("400x600")

    # Đọc config
    with open(os.path.join(duong_dan, r"data\config.json"), "r", encoding="utf-8") as f:
        du_lieu = json.load(f)
    so_vung = int(du_lieu.get("so_vung", 0))
    print("Số vùng là:", so_vung)

    du_lieu_cu = {}
    try:
        with open(os.path.join(duong_dan, r"data\dulieu.json"), "r", encoding="utf-8") as f:
            du_lieu_cu = json.load(f)
    except FileNotFoundError:
        pass

    danh_sach_toa_do = [{} for _ in range(so_vung)]
    danh_sach_entry_map_var = [[] for _ in range(so_vung)]

    frame_tc_chay = ctk.CTkScrollableFrame(cua_so_2)
    frame_tc_chay.pack(fill="both", expand=True, padx=10, pady=10)

    def luu_du_lieu():
        du_lieu_can_luu = {
            "so_vung": so_vung,
            "vung": {}
        }

        for i in range(so_vung):
            try:
                ban_kinh_value = danh_sach_entry_map_var[i][0].get()
            except ValueError:
                messagebox.showerror("Lỗi nhập liệu", f"Vui lòng nhập số hợp lệ cho bán kính của Vùng {i+1}")
                return

            map_var_data = {
                "ban_kinh": ban_kinh_value
            }

            du_lieu_can_luu["vung"][str(i + 1)] = {
                "dq": danh_sach_dropdown1[i].get(),
                "che_do": danh_sach_dropdown2[i].get(),
                "toa_do": danh_sach_toa_do[i],
                "map_var": map_var_data
            }

        try:
            duong_dan_data = os.path.join(duong_dan, "data")
            os.makedirs(duong_dan_data, exist_ok=True)

            file_path = os.path.join(duong_dan_data, "dulieu.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(du_lieu_can_luu, f, ensure_ascii=False, indent=4)

            print(f"\nĐã lưu dữ liệu vào: {file_path}")
            for i in range(so_vung):
                print(f"Vùng {i+1}: {danh_sach_toa_do[i]}, Bán kính: {danh_sach_entry_map_var[i][0].get()}")

        except Exception as e:
            print(f"Lỗi khi ghi file dulieu.json:\n{e}")

    def luu_toa_do_cho_vung(i, toa_do):
        danh_sach_toa_do[i] = toa_do
        print(f"Đã lưu tọa độ cho vùng {i+1}: {toa_do}")

    # Giao diện theo số vùng
    for i in range(so_vung):
        frame = ctk.CTkFrame(frame_tc_chay)
        frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame, text=f"Khung {i + 1}").pack(anchor="w", padx=10)

        nut_cv = ctk.CTkButton(frame, text="Chọn Vùng",
                               command=lambda i=i: chon_vung(lambda toa_do: luu_toa_do_cho_vung(i, toa_do)))
        nut_cv.pack(padx=10, pady=(5, 10))

        # --- Bán kính ---
        frame_radius = ctk.CTkFrame(frame)
        frame_radius.pack(padx=10, pady=5, fill="x")

        ctk.CTkLabel(frame_radius, text="Bán kính:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        entry_radius = ctk.CTkEntry(frame_radius, width=80)
        entry_radius.grid(row=0, column=1, padx=5, pady=2)
        danh_sach_entry_map_var[i].append(entry_radius)

        # --- Dropdown số đội quân ---
        ctk.CTkLabel(frame, text="Chọn Số Đội Quân").pack(anchor="w", padx=10, pady=(10, 0))
        so_dq = ["1", "2", "3", "4", "5", "6", "7"]
        dropdown1 = ctk.CTkOptionMenu(frame, values=so_dq)
        dq_cu = du_lieu_cu.get("vung", {}).get(str(i + 1), {}).get("dq", so_dq[0])
        dropdown1.set(dq_cu)
        dropdown1.pack(padx=10, pady=(5, 10))
        danh_sach_dropdown1.append(dropdown1)

        # --- Dropdown chế độ ---
        ctk.CTkLabel(frame, text="Chọn Chế Độ").pack(anchor="w", padx=10)
        che_do = ["1", "2", "3", "4", "5", "6", "7", "8"]
        dropdown2 = ctk.CTkOptionMenu(frame, values=che_do)
        cd_cu = du_lieu_cu.get("vung", {}).get(str(i + 1), {}).get("che_do", che_do[0])
        dropdown2.set(cd_cu)
        dropdown2.pack(padx=10, pady=(5, 10))
        danh_sach_dropdown2.append(dropdown2)

        # Gán dữ liệu cũ
        toa_do_cu = du_lieu_cu.get("vung", {}).get(str(i + 1), {}).get("toa_do", {})
        danh_sach_toa_do[i] = toa_do_cu

        map_var_cu = du_lieu_cu.get("vung", {}).get(str(i + 1), {}).get("map_var", {})
        entry_radius.insert(0, map_var_cu.get("ban_kinh", ""))

    nut_luu = ctk.CTkButton(cua_so_2, text="Lưu Tùy Chỉnh", command=luu_du_lieu)
    nut_luu.pack(pady=10)


#==================== GIAO DIỆN CHÍNH ==============================
main_window = ctk.CTk()
main_window.title("Menu Chinh")
main_window.geometry("450x200")

frame_duong_dan = ctk.CTkFrame(main_window)
frame_duong_dan.pack(pady=10, padx=10, fill="x")

frame_giao_dien = ctk.CTkFrame(main_window)
frame_giao_dien.pack(pady=10, padx=10, fill="x")

label_duong_dan = ctk.CTkLabel(frame_duong_dan, text="Nhập đường dẫn:")
label_duong_dan.pack(side="left", padx=10)

entry_duong_dan = ctk.CTkEntry(frame_duong_dan, width=250)
entry_duong_dan.insert(0, duong_dan)
entry_duong_dan.pack(side="left", padx=10)

nut_nhap_duong_dan = ctk.CTkButton(frame_duong_dan, text="Chọn", command=chon_thu_muc, width=50)
nut_nhap_duong_dan.pack(side="right", padx=10)

nut_tc = ctk.CTkButton(frame_giao_dien, text="Tuy Chinh", command=cua_so_tc, width=120)
nut_tc.pack(side="top", padx=10)

nut_tl_chay = ctk.CTkButton(frame_giao_dien, text="Thiet Lap Chay", command=cua_so_chay, width=120)
nut_tl_chay.pack(side="top", padx=10, pady=10)

nut_ql_chay = ctk.CTkButton(frame_giao_dien, text="Quan Ly Chay", command=mo_quan_ly_vung, width=120)
nut_ql_chay.pack(side="top", padx=10, pady=10)

main_window.mainloop()
