import customtkinter as ctk
import tkinter as tk
from PIL import ImageGrab
import pytesseract
import cv2
import numpy as np
import pyautogui
import time, random, re, os

# ================== GLOBAL =====================
coords = {}          # Lưu vùng chọn tạm
luu_toa_do = []      # Lưu kết quả xử lý

# ================== HÀM CHỌN VÙNG =====================
def chon_vung():
    global coords
    coords.clear()

    root_select = tk.Toplevel()
    root_select.overrideredirect(True)
    sw, sh = root_select.winfo_screenwidth(), root_select.winfo_screenheight()
    root_select.geometry(f"{sw}x{sh}+0+0")
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
        print(f"Đã chọn vùng: ({coords['x1']},{coords['y1']}) → ({coords['x2']},{coords['y2']})")

    canvas.bind("<Button-1>", start_select)
    canvas.bind("<B1-Motion>", update_select)
    canvas.bind("<ButtonRelease-1>", end_select)
    root_select.bind("<Escape>", lambda e: root_select.destroy())
    root_select.mainloop()
    return coords

# ================== HÀM OCR =====================
def tx_gems(che_do=1, crop_ratio=None):
    if not coords:
        print("Chưa chọn vùng")
        return "", None

    x1,y1,x2,y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
    img = ImageGrab.grab(bbox=(x1,y1,x2,y2))

    if crop_ratio:
        w,h = img.size
        l = int(w*crop_ratio[0]); r = int(w*crop_ratio[1])
        t = int(h*crop_ratio[2]); b = int(h*crop_ratio[3])
        img = img.crop((l,t,w-r,h-b))

    text = pytesseract.image_to_string(img, lang="vie", config="--psm 7").strip()
    if che_do==2: text = re.sub(r'[^0-9xyXY]', '', text)
    print(f"[tx_gems] OCR='{text}'")
    return text, img

# ================== HÀM CLICK ẢNH =====================
def click_co_ban(filename, threshold=0.8):
    if not coords:
        print("Chưa chọn vùng")
        return None

    x1,y1,x2,y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
    screenshot = ImageGrab.grab(bbox=(x1,y1,x2,y2))
    scr_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    if not filename.lower().endswith(".png"): filename += ".png"
    if not os.path.exists(filename):
        print(f"Không tìm thấy file mẫu {filename}")
        return None

    tpl = cv2.imread(filename)
    res = cv2.matchTemplate(scr_bgr, tpl, cv2.TM_CCOEFF_NORMED)
    _,max_val,_,max_loc = cv2.minMaxLoc(res)

    if max_val >= threshold:
        h,w = tpl.shape[:2]
        cx,cy = x1+max_loc[0]+w//2, y1+max_loc[1]+h//2
        pyautogui.click(cx,cy)
        print(f"Click {filename} tại ({cx},{cy}) - match={max_val:.2f}")
        return (cx,cy)
    else:
        print(f"Không khớp {filename}, match={max_val:.2f}")
        return None

# ================== HÀM GIỮ NÚT =====================
def giu_nut(filename, threshold=0.7):
    if not coords:
        print("Chưa chọn vùng")
        return False
    thoi_gian = random.randint(3,6)
    x1,y1,x2,y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']

    scr=ImageGrab.grab(bbox=(x1,y1,x2,y2))
    scr_bgr=cv2.cvtColor(np.array(scr),cv2.COLOR_RGB2BGR)

    if not filename.lower().endswith(".png"): filename+=".png"
    tpl=cv2.imread(filename)
    res=cv2.matchTemplate(scr_bgr,tpl,cv2.TM_CCOEFF_NORMED)
    _,max_val,_,max_loc=cv2.minMaxLoc(res)

    if max_val>=threshold:
        h,w=tpl.shape[:2]
        cx,cy=x1+max_loc[0]+w//2,y1+max_loc[1]+h//2
        pyautogui.mouseDown(cx,cy); time.sleep(thoi_gian); pyautogui.mouseUp(cx,cy)
        print(f"Giữ {filename} tại ({cx},{cy}) {thoi_gian}s")
        return True
    else:
        return False

# ================== HÀM CLICK TỈ LỆ =====================
def click_theo_toa_do(ratio_x=0.5, ratio_y=0.5):
    if not coords:
        print("Chưa chọn vùng")
        return False
    x1,y1,x2,y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
    x_click=x1+int((x2-x1)*ratio_x); y_click=y1+int((y2-y1)*ratio_y)
    pyautogui.click(x_click,y_click)
    print(f"Click theo tỉ lệ tại ({x_click},{y_click})")
    return True

def click_vao_toa_do(x,y):
    pyautogui.click(x,y)
    time.sleep(random.randint(3,6))

def nhap_ban_phim(chuoi=""):
    pyautogui.write(chuoi,0.8); time.sleep(1); pyautogui.press('enter')

def nhap_toa_do(x,y):
    click_theo_toa_do(0.195,0.03); time.sleep(2)
    click_theo_toa_do(0.5,0.2); nhap_ban_phim(str(x)); time.sleep(2)
    click_theo_toa_do(0.64,0.2); nhap_ban_phim(str(y)); time.sleep(2)
    click_theo_toa_do(0.69,0.19); time.sleep(2)

# ================== GUI =====================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Test Chọn Vùng + OCR + Click")
        self.geometry("400x350")

        ctk.CTkButton(self,text="Chọn Vùng",command=chon_vung).pack(pady=5)
        ctk.CTkButton(self,text="OCR tx_gems",command=lambda: tx_gems()).pack(pady=5)
        ctk.CTkButton(self,text="Click Ảnh",command=lambda: click_co_ban("button.png")).pack(pady=5)
        ctk.CTkButton(self,text="Giữ Ảnh",command=lambda: giu_nut("button.png")).pack(pady=5)
        ctk.CTkButton(self,text="Click Tỉ Lệ",command=lambda: click_theo_toa_do(0.5,0.5)).pack(pady=5)

# ================== MAIN =====================
if __name__=="__main__":
    app=App()
    app.mainloop()
