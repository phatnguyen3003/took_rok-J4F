import customtkinter as ctk
from PIL import Image
import pyautogui

def toadocon():
    try:
        # Lấy dữ liệu từ Entry
        x1 = int(entry_x1.get())
        y1 = int(entry_y1.get())
        x2 = int(entry_x2.get())
        y2 = int(entry_y2.get())

        tlx1 = float(entry_tlx1.get())
        tly1 = float(entry_tly1.get())
        tlx2 = float(entry_tlx2.get())
        tly2 = float(entry_tly2.get())
    except ValueError:
        print("Lỗi: nhập chưa hợp lệ")
        return None

    w = x2 - x1
    h = y2 - y1

    x1_con = int(x1 + w * tlx1)
    y1_con = int(y1 + h * tly1)
    x2_con = int(x1 + w * tlx2)
    y2_con = int(y1 + h * tly2)

    # Update label kết quả
    label_x1_con.configure(text=f"x1_con = {x1_con}")
    label_y1_con.configure(text=f"y1_con = {y1_con}")
    label_x2_con.configure(text=f"x2_con = {x2_con}")
    label_y2_con.configure(text=f"y2_con = {y2_con}")

    return x1_con, y1_con, x2_con, y2_con

def chup_vung():
    coords = toadocon()
    if coords is None:
        return
    x1, y1, x2, y2 = coords
    w, h = x2 - x1, y2 - y1

    screenshot = pyautogui.screenshot(region=(x1, y1, w, h))

    popup = ctk.CTkToplevel()
    popup.title("Ảnh chụp màn hình")
    popup.geometry(f"{w}x{h}")

    img_ctk = ctk.CTkImage(light_image=screenshot, size=(w, h))
    label = ctk.CTkLabel(popup, image=img_ctk, text="")
    label.image = img_ctk
    label.pack()

# ==== Giao diện ====
main_win = ctk.CTk()
main_win.geometry("400x500")
main_win.title("Test Toạ độ con")

frame = ctk.CTkScrollableFrame(main_win)
frame.pack(fill="both", expand=True, padx=10, pady=10)

entry_x1 = ctk.CTkEntry(frame, placeholder_text="x1"); entry_x1.pack(padx=5, pady=5)
entry_y1 = ctk.CTkEntry(frame, placeholder_text="y1"); entry_y1.pack(padx=5, pady=5)
entry_x2 = ctk.CTkEntry(frame, placeholder_text="x2"); entry_x2.pack(padx=5, pady=5)
entry_y2 = ctk.CTkEntry(frame, placeholder_text="y2"); entry_y2.pack(padx=5, pady=5)

entry_tlx1 = ctk.CTkEntry(frame, placeholder_text="tlx1"); entry_tlx1.pack(padx=5, pady=5)
entry_tly1 = ctk.CTkEntry(frame, placeholder_text="tly1"); entry_tly1.pack(padx=5, pady=5)
entry_tlx2 = ctk.CTkEntry(frame, placeholder_text="tlx2"); entry_tlx2.pack(padx=5, pady=5)
entry_tly2 = ctk.CTkEntry(frame, placeholder_text="tly2"); entry_tly2.pack(padx=5, pady=5)

label_x1_con = ctk.CTkLabel(frame, text="x1_con"); label_x1_con.pack(padx=5, pady=5)
label_y1_con = ctk.CTkLabel(frame, text="y1_con"); label_y1_con.pack(padx=5, pady=5)
label_x2_con = ctk.CTkLabel(frame, text="x2_con"); label_x2_con.pack(padx=5, pady=5)
label_y2_con = ctk.CTkLabel(frame, text="y2_con"); label_y2_con.pack(padx=5, pady=5)

btn = ctk.CTkButton(frame, text="Tính toạ độ con", command=toadocon)
btn.pack(pady=10)

btn2 = ctk.CTkButton(frame, text="Chụp vùng", command=chup_vung)
btn2.pack(pady=10)

main_win.mainloop()
