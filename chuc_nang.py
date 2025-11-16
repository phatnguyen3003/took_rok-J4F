import json
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
import os
import pytesseract
import random
import re
import script
import time
import unicodedata
#======================= TOAN CUC =============================
CHIA_CHO_MAP = [3000, 3000, 3800, 1100]
SCALE = 1.25
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
luu_toa_do=[]
x_hien_tai=0
y_hien_tai=0
#======================= CHUC NANG ============================
def click_co_ban(i, filename, threshold=0.8):
    """
    i: Số vùng (1-based index)
    filename: Tên file ảnh mẫu (.png hoặc không cần .png)
    threshold: Ngưỡng khớp ảnh (0-1)
    """
    try:
        i = int(i)
    except ValueError:
        print(f"Lỗi: Tham số i='{i}' không phải số nguyên")
        return False

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "data", "dulieu.json")
    buttons_dir = os.path.join(base_dir, "buttons")

    # Đọc tọa độ vùng
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "vung" not in data or not isinstance(data["vung"], dict):
            print("Lỗi: File dulieu.json không chứa danh sách 'vung'")
            return False

        vung = data["vung"].get(str(i))
        if not vung:
            print(f"Không tìm thấy vùng {i} trong file dữ liệu")
            return False

        toa_do = vung.get("toa_do")
        if not toa_do:
            print(f"Vùng {i} không có thông tin tọa độ")
            return False

        x1, y1, x2, y2 = int(toa_do["x1"]), int(toa_do["y1"]), int(toa_do["x2"]), int(toa_do["y2"])

    except Exception as e:
        print(f"Lỗi khi đọc tọa độ vùng {i}: {e}")
        return False

    # Chụp ảnh vùng
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    screenshot_rgb = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_rgb, cv2.COLOR_RGB2BGR)

    # Đường dẫn file ảnh mẫu
    if not filename.lower().endswith(".png"):
        filename += ".png"
    template_path = os.path.join(buttons_dir, filename)

    if not os.path.exists(template_path):
        print(f"Không tìm thấy file mẫu: {template_path}")
        return False

    try:
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            print(f"Không thể đọc file ảnh mẫu: {template_path}")
            return False
    except Exception as e:
        print(f"Lỗi khi đọc ảnh mẫu: {e}")
        return False

    # So khớp
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        click_x = x1 + max_loc[0] + w // 2
        click_y = y1 + max_loc[1] + h // 2
        pyautogui.click(click_x, click_y)
        print(f"Đã click tại ({click_x}, {click_y}) - Độ khớp: {max_val:.2f}")
        return True
    else:
        print(f"Không tìm thấy ảnh '{filename}' trong vùng {i} (độ khớp {max_val:.2f})")
        return False



def tx_du_tru(i):
    """
    Trích xuất số từ vùng i trong dulieu.json với scale 1.25.
    i: vùng (1-based index)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, "data", "dulieu.json")

    with open(data_file, "r", encoding="utf-8") as f:
        dulieu = json.load(f)

    vung_dict = dulieu.get("vung", {})
    vung = vung_dict.get(str(i))
    if not vung:
        raise ValueError(f"Không tìm thấy vùng {i} trong dulieu.json")

    toa_do = vung.get("toa_do", {})
    x1 = int(toa_do.get("x1", 0))
    y1 = int(toa_do.get("y1", 0))
    x2 = int(toa_do.get("x2", 0))
    y2 = int(toa_do.get("y2", 0))
    che_do = int(vung.get("che_do", 0))

    try:
        chia_cho = CHIA_CHO_MAP[che_do-1]
    except IndexError:
        chia_cho = CHIA_CHO_MAP[0]

    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    width, height = img.size

    left_margin = int(width * 0.765)
    right_margin = int(width * 0.09)
    top_margin = int(height * 0.37)
    bottom_margin = int(height * 0.575)

    crop_img = img.crop((
        left_margin,
        top_margin,
        width - right_margin,
        height - bottom_margin
    ))

    os.makedirs(os.path.join(base_dir, "debug"), exist_ok=True)
    crop_img.save(os.path.join(base_dir, "debug", f"tx_du_tru_vung_{i}.png"))

    text = pytesseract.image_to_string(crop_img, config='--psm 7 digits').strip()
    try:
        so_luong_con_lai = int(''.join(filter(str.isdigit, text)))
    except ValueError:
        so_luong_con_lai = 0

    so_phut = so_luong_con_lai / chia_cho
    so_giay = int(so_phut * 60)

    print(f"[tx_du_tru] Vùng {i}, Chế độ {che_do}: OCR='{text}', số={so_luong_con_lai}, phút={so_phut}, giây={so_giay}")
    return so_giay



def tx_hanh_quan(i):
    """
    Đọc thời gian hh:mm:ss trong vùng i, áp dụng scale 1.25.
    i: vùng (1-based index)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, "data", "dulieu.json")

    with open(data_file, "r", encoding="utf-8") as f:
        dulieu = json.load(f)

    vung_dict = dulieu.get("vung", {})
    vung = vung_dict.get(str(i))
    if not vung:
        raise ValueError(f"Không tìm thấy vùng {i} trong dulieu.json")

    toa_do = vung.get("toa_do", {})
    x1 = int(toa_do.get("x1", 0))
    y1 = int(toa_do.get("y1", 0))
    x2 = int(toa_do.get("x2", 0))
    y2 = int(toa_do.get("y2", 0))

    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    width, height = img.size

    left_margin = int(width * 0.695)
    right_margin = int(width * 0.22)
    top_margin = int(height * 0.885)
    bottom_margin = int(height * 0.075)

    crop_img = img.crop((
        left_margin,
        top_margin,
        width - right_margin,
        height - bottom_margin
    ))

    os.makedirs(os.path.join(base_dir, "debug"), exist_ok=True)
    crop_img.save(os.path.join(base_dir, "debug", f"tx_hanh_quan_vung_{i}.png"))

    text = pytesseract.image_to_string(crop_img, config='--psm 7').strip()

    h = m = s = 0
    parts = text.split(":")
    if len(parts) == 3:
        try:
            h, m, s = map(int, parts)
        except ValueError:
            pass
    else:
        print(f"[tx_hanh_quan] Lỗi OCR, không đúng định dạng hh:mm:ss → '{text}'")

    total_seconds = h * 3600 + m * 60 + s
    ket_qua = total_seconds * 2 + 120

    print(f"[tx_hanh_quan] Vùng {i}: OCR='{text}', {total_seconds} giây → KQ={ket_qua} giây")
    return ket_qua


def tinh_tong_thoi_gian(du_tru, hanh_quan):
    tong = du_tru + hanh_quan

    print(f"🧮 Tổng thời gian: {tong} giây")
    return tong

def click_lech(i, filename, offset_x=0, offset_y=0, threshold=0.7):
    """
    i: Số vùng (1-based index)
    filename: Tên file ảnh mẫu (.png hoặc không cần .png)
    offset_x: Khoảng cách dịch chuyển theo trục X (âm hoặc dương)
    offset_y: Khoảng cách dịch chuyển theo trục Y (âm hoặc dương)
    threshold: Ngưỡng khớp ảnh (0-1)
    """
    try:
        i = int(i)
    except ValueError:
        print(f"Lỗi: Tham số i='{i}' không phải số nguyên")
        return False

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "data", "dulieu.json")
    buttons_dir = os.path.join(base_dir, "buttons")

    # Đọc tọa độ vùng
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "vung" not in data or not isinstance(data["vung"], dict):
            print("Lỗi: File dulieu.json không chứa danh sách 'vung'")
            return False

        vung = data["vung"].get(str(i))
        if not vung:
            print(f"Không tìm thấy vùng {i} trong file dữ liệu")
            return False

        toa_do = vung.get("toa_do")
        if not toa_do:
            print(f"Vùng {i} không có thông tin tọa độ")
            return False

        x1, y1, x2, y2 = int(toa_do["x1"]), int(toa_do["y1"]), int(toa_do["x2"]), int(toa_do["y2"])

    except Exception as e:
        print(f"Lỗi khi đọc tọa độ vùng {i}: {e}")
        return False

    # Chụp ảnh vùng
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    screenshot_rgb = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_rgb, cv2.COLOR_RGB2BGR)

    # Đường dẫn file ảnh mẫu
    if not filename.lower().endswith(".png"):
        filename += ".png"
    template_path = os.path.join(buttons_dir, filename)

    if not os.path.exists(template_path):
        print(f"Không tìm thấy file mẫu: {template_path}")
        return False

    try:
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            print(f"Không thể đọc file ảnh mẫu: {template_path}")
            return False
    except Exception as e:
        print(f"Lỗi khi đọc ảnh mẫu: {e}")
        return False

    # So khớp
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        # Tính toán tọa độ click với offset
        click_x = x1 + max_loc[0] + w // 2 + offset_x
        click_y = y1 + max_loc[1] + h // 2 + offset_y
        
        pyautogui.click(click_x, click_y)
        print(f"Đã click tại ({click_x}, {click_y}) - Offset: ({offset_x}, {offset_y}) - Độ khớp: {max_val:.2f}")
        return True
    else:
        print(f"Không tìm thấy ảnh '{filename}' trong vùng {i} (độ khớp {max_val:.2f})")
        return False

def tx_so(i, crop_ratio=(0.2, 0.2, 0.2, 0.2)):
    """
    Trích xuất số từ vùng i trong dulieu.json, với tỷ lệ cắt tùy chỉnh.

    i: Số vùng (1-based index)
    crop_ratio: Một tuple (trái, phải, trên, dưới) với giá trị từ 0 đến 1.
                Ví dụ: (0.1, 0.1, 0.2, 0.2) sẽ cắt 10% từ trái/phải, 20% từ trên/dưới.
    """
    try:
        i = int(i)
    except ValueError:
        print(f"Lỗi: Tham số i='{i}' không phải số nguyên")
        return 0

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, "data", "dulieu.json")

    # Đọc tọa độ vùng từ file JSON
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            dulieu = json.load(f)

        vung_dict = dulieu.get("vung", {})
        vung = vung_dict.get(str(i))
        if not vung:
            print(f"Không tìm thấy vùng {i} trong dulieu.json")
            return 0

        toa_do = vung.get("toa_do", {})
        x1 = int(toa_do.get("x1", 0))
        y1 = int(toa_do.get("y1", 0))
        x2 = int(toa_do.get("x2", 0))
        y2 = int(toa_do.get("y2", 0))

    except Exception as e:
        print(f"Lỗi khi đọc tọa độ vùng {i}: {e}")
        return 0

    # Chụp ảnh vùng
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    width, height = img.size

    # Áp dụng tỷ lệ cắt từ tham số crop_ratio theo thứ tự mới (trái, phải, trên, dưới)
    left_margin = int(width * crop_ratio[0])
    right_margin = int(width * crop_ratio[1])
    top_margin = int(height * crop_ratio[2])
    bottom_margin = int(height * crop_ratio[3])

    crop_img = img.crop((
        left_margin,
        top_margin,
        width - right_margin,
        height - bottom_margin
    ))

    # Lưu ảnh đã cắt để debug (bạn có thể bỏ dòng này)
    os.makedirs(os.path.join(base_dir, "debug"), exist_ok=True)
    crop_img.save(os.path.join(base_dir, "debug", f"tx_so_vung_{i}.png"))

    # Trích xuất số
    text = pytesseract.image_to_string(crop_img, config='--psm 7 digits').strip()
    
    # Chuyển đổi kết quả sang số nguyên và trả về
    try:
        so_trich_xuat = int(''.join(filter(str.isdigit, text)))
    except ValueError:
        so_trich_xuat = 0

    print(f"[{__name__}] Vùng {i}: OCR='{text}', số đã trích xuất={so_trich_xuat}")
    return so_trich_xuat



def vuot_trong_vung(i, huong, khoang_cach=100, thoi_gian=2):
    """
    Tìm vùng i trong dulieu.json, di chuyển chuột đến điểm bắt đầu vuốt,
    giữ chuột và thực hiện thao tác vuốt.

    Args:
        i (int): Chỉ số vùng (1-based index)
        huong (str): Hướng vuốt ("trai", "phai", "tren", "duoi")
        khoang_cach (int): Khoảng cách vuốt (mặc định 100 pixels)
        thoi_gian (float): Thời gian vuốt (mặc định 0.2 giây)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, "data", "dulieu.json")
    khoang_cach=random.randint(100,300)
    # Kiểm tra và tải file dulieu.json
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Không tìm thấy file dulieu.json tại đường dẫn: {data_file}")

    with open(data_file, "r", encoding="utf-8") as f:
        dulieu = json.load(f)

    vung_dict = dulieu.get("vung", {})
    vung = vung_dict.get(str(i))
    if not vung:
        raise ValueError(f"Không tìm thấy vùng {i} trong dulieu.json")

    toa_do = vung.get("toa_do", {})
    if not toa_do or 'x1' not in toa_do or 'y1' not in toa_do or 'x2' not in toa_do or 'y2' not in toa_do:
        raise ValueError(f"Vùng {i} thiếu tọa độ trong dulieu.json")
    
    x1 = toa_do['x1']
    y1 = toa_do['y1']
    x2 = toa_do['x2']
    y2 = toa_do['y2']

    # Tính toán tâm của vùng
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
    else:
        print(f"Hướng '{huong}' không hợp lệ. Vui lòng chọn một trong các hướng: 'trai', 'phai', 'tren', 'duoi'.")
        return

    # Di chuyển chuột đến điểm bắt đầu
    print(f"Di chuyển chuột đến điểm bắt đầu vuốt: ({start_x}, {start_y})")
    pyautogui.moveTo(start_x, start_y, duration=0.2)

    # Giữ chuột và kéo đến điểm kết thúc
    print(f"Giữ chuột và kéo đến điểm kết thúc: ({end_x}, {end_y})")
    pyautogui.dragTo(end_x, end_y, duration=thoi_gian, button='left')
    
    print(f"Đã vuốt {huong} với khoảng cách {khoang_cach} xong.")

def giu_nut(i, filename, threshold=0.7):
    """
    Tìm ảnh mẫu trong vùng đã chọn và giữ chuột tại đó trong một khoảng thời gian.
    
    Args:
        i (int): Số vùng (1-based index)
        filename (str): Tên file ảnh mẫu (không cần .png)
        threshold (float): Ngưỡng khớp ảnh (từ 0.0 đến 1.0)
    """
    # Khai báo và tùy chỉnh thời gian giữ nút tại đây
    thoi_gian_giu_nut = random.randint(3,6)

    try:
        i = int(i)
    except ValueError:
        print(f"Lỗi: Tham số i='{i}' không phải số nguyên")
        return False

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "data", "dulieu.json")
    buttons_dir = os.path.join(base_dir, "buttons")

    # Đọc tọa độ vùng
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "vung" not in data or not isinstance(data["vung"], dict):
            print("Lỗi: File dulieu.json không chứa danh sách 'vung'")
            return False

        vung = data["vung"].get(str(i))
        if not vung:
            print(f"Không tìm thấy vùng {i} trong file dữ liệu")
            return False

        toa_do = vung.get("toa_do")
        if not toa_do:
            print(f"Vùng {i} không có thông tin tọa độ")
            return False

        x1, y1, x2, y2 = int(toa_do["x1"]), int(toa_do["y1"]), int(toa_do["x2"]), int(toa_do["y2"])

    except Exception as e:
        print(f"Lỗi khi đọc tọa độ vùng {i}: {e}")
        return False

    # Chụp ảnh vùng
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    screenshot_rgb = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_rgb, cv2.COLOR_RGB2BGR)

    # Đường dẫn file ảnh mẫu
    if not filename.lower().endswith(".png"):
        filename += ".png"
    template_path = os.path.join(buttons_dir, filename)

    if not os.path.exists(template_path):
        print(f"Không tìm thấy file mẫu: {template_path}")
        return False

    try:
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            print(f"Không thể đọc file ảnh mẫu: {template_path}")
            return False
    except Exception as e:
        print(f"Lỗi khi đọc ảnh mẫu: {e}")
        return False

    # So khớp
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        click_x = x1 + max_loc[0] + w // 2
        click_y = y1 + max_loc[1] + h // 2
        
        # --- Phần logic giữ chuột mới ---
        print(f"Tìm thấy '{filename}' với độ khớp: {max_val:.2f}")
        print(f"Bắt đầu giữ chuột tại ({click_x}, {click_y}) trong {thoi_gian_giu_nut} giây...")
        
        pyautogui.mouseDown(click_x, click_y)
        pyautogui.sleep(thoi_gian_giu_nut)
        pyautogui.mouseUp(click_x, click_y)
        
        print("Đã thả chuột.")
        return True
    else:
        print(f"Không tìm thấy ảnh '{filename}' trong vùng {i} (độ khớp {max_val:.2f})")
        return False

def kiem_tra_nut(i, filename):
    """
    Kiểm tra xem ảnh filename có nằm trong vùng i hay không.
    i: chỉ số vùng (int)
    filename: đường dẫn file ảnh mẫu (str)
    Trả về True nếu tìm thấy, False nếu không.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "data", "dulieu.json")
    buttons_dir = os.path.join(base_dir, "buttons")
    # Đọc dữ liệu vùng từ dulieu.json
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(base_dir, "data", "dulieu.json")
        with open(data_file, "r", encoding="utf-8") as f:
            du_lieu = json.load(f)
    except FileNotFoundError:
        print("[Lỗi] Không tìm thấy file dulieu.json.")
        return False
    
    # Chuyển đổi chỉ số i sang chuỗi để truy cập đúng khóa trong JSON
    vung_key = str(i)
    
    # Sử dụng .get() để truy cập dữ liệu một cách an toàn
    vung_data = du_lieu.get("vung", {}).get(vung_key, {})
    if not vung_data:
        print(f"[Lỗi] Không tìm thấy thông tin vùng {vung_key} trong dulieu.json")
        return False

    toa_do = vung_data.get("toa_do", {})
    x1 = toa_do.get("x1", 0)
    y1 = toa_do.get("y1", 0)
    x2 = toa_do.get("x2", 0)
    y2 = toa_do.get("y2", 0)

    # Chụp ảnh màn hình vùng
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Đọc ảnh mẫu
    filename = os.path.join(buttons_dir, filename)
    if not os.path.exists(filename):
        print(f"Không tìm thấy file mẫu: {filename}")
        return False,None

    try:
        template = cv2.imread(filename, cv2.IMREAD_COLOR)
        if template is None:
            print(f"Không thể đọc file ảnh mẫu: {filename}")
            return False,None
    except Exception as e:
        print(f"Lỗi khi đọc ảnh mẫu: {e}")
        return False,None

    # So khớp ảnh
    result = cv2.matchTemplate(img_np, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    # Ngưỡng nhận diện
    threshold = 0.65
    if max_val >= threshold:
        print(f"[OK] Nút tìm thấy trong vùng {vung_key}, độ khớp: {max_val:.2f}")
        return True
    else:
        print(f"[Fail] Không tìm thấy nút trong vùng {vung_key}, độ khớp: {max_val:.2f}")
        return False

def tx_thoi_gian(i, crop_ratio=(0.2, 0.2, 0.2, 0.2)):
    """
    Trích xuất thời gian (hh:mm:ss) từ một vùng màn hình và trả về giờ, phút, giây.

    i: Số vùng (1-based index)
    crop_ratio: Một tuple (trái, phải, trên, dưới) để cắt ảnh.
    """
    try:
        i = int(i)
    except ValueError:
        print(f"Lỗi: Tham số i='{i}' không phải số nguyên")
        return 0, 0, 0 # Trả về 0, 0, 0 nếu có lỗi

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, "data", "dulieu.json")

    # Đọc tọa độ vùng từ file JSON
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            dulieu = json.load(f)

        vung_dict = dulieu.get("vung", {})
        vung = vung_dict.get(str(i))
        if not vung:
            print(f"Không tìm thấy vùng {i} trong dulieu.json")
            return 0, 0, 0

        toa_do = vung.get("toa_do", {})
        x1 = int(toa_do.get("x1", 0))
        y1 = int(toa_do.get("y1", 0))
        x2 = int(toa_do.get("x2", 0))
        y2 = int(toa_do.get("y2", 0))

    except Exception as e:
        print(f"Lỗi khi đọc tọa độ vùng {i}: {e}")
        return 0, 0, 0

    # Chụp ảnh và cắt vùng đã xác định
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    width, height = img.size

    left_margin = int(width * crop_ratio[0])
    right_margin = int(width * crop_ratio[1])
    top_margin = int(height * crop_ratio[2])
    bottom_margin = int(height * crop_ratio[3])

    crop_img = img.crop((
        left_margin,
        top_margin,
        width - right_margin,
        height - bottom_margin
    ))

    # Lưu ảnh đã cắt để debug
    os.makedirs(os.path.join(base_dir, "debug"), exist_ok=True)
    crop_img.save(os.path.join(base_dir, "debug", f"tx_thoi_gian_vung_{i}.png"))

    # Trích xuất toàn bộ chuỗi ký tự, không chỉ số
    # Sử dụng psm 6 để đọc một dòng văn bản
    text = pytesseract.image_to_string(crop_img, config='--psm 6').strip()
    
    # Xóa các ký tự không phải số hoặc dấu hai chấm
    text = ''.join(c for c in text if c.isdigit() or c == ':')

    gio, phut, giay = 0, 0, 0
    try:
        # Phân tích chuỗi thời gian thành giờ, phút, giây
        thanh_phan = text.split(':')
        if len(thanh_phan) == 3:
            gio = int(thanh_phan[0])
            phut = int(thanh_phan[1])
            giay = int(thanh_phan[2])
    except (ValueError, IndexError):
        print(f"Lỗi: Không thể phân tích thời gian từ chuỗi '{text}'")
        gio, phut, giay = 0, 0, 0
    giay+=gio*3600+phut*60

    print(f"[{__name__}] Vùng {i}: OCR='{text}', Thời gian đã trích xuất={gio}:{phut}:{giay}")
    return giay


def click_theo_toa_do(i, ratio_x=0.5, ratio_y=0.5):
    """
    Lấy tọa độ của một vùng từ file cấu hình, sau đó sử dụng tỷ lệ để tính
    tọa độ của một điểm click duy nhất bên trong vùng đó.

    Args:
        i (int): Số vùng (1-based index) trong file dulieu.json.
        ratio_x (float): Tỷ lệ theo chiều ngang (0.0 đến 1.0) để xác định điểm.
        ratio_y (float): Tỷ lệ theo chiều dọc (0.0 đến 1.0) để xác định điểm.
        
    Returns:
        tuple: Một tuple chứa (x_click, y_click) nếu thành công,
               hoặc None nếu có lỗi.
    """
    try:
        i = int(i)
    except ValueError:
        print(f"Lỗi: Tham số i='{i}' không phải số nguyên.")
        return None

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "data", "dulieu.json")

    # Đọc tọa độ vùng
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "vung" not in data or not isinstance(data["vung"], dict):
            print("Lỗi: File dulieu.json không chứa danh sách 'vung'.")
            return None

        vung = data["vung"].get(str(i))
        if not vung:
            print(f"Không tìm thấy vùng {i} trong file dữ liệu.")
            return None

        toa_do = vung.get("toa_do")
        if not toa_do:
            print(f"Vùng {i} không có thông tin tọa độ.")
            return None

        x1, y1, x2, y2 = int(toa_do["x1"]), int(toa_do["y1"]), int(toa_do["x2"]), int(toa_do["y2"])

    except Exception as e:
        print(f"Lỗi khi đọc tọa độ vùng {i}: {e}")
        return None
    
    # Sắp xếp tọa độ để đảm bảo x1 <= x2 và y1 <= y2
    x_min, x_max = min(x1, x2), max(x1, x2)
    y_min, y_max = min(y1, y2), max(y1, y2)

    # Tính toán tọa độ điểm click dựa trên tỷ lệ
    x_click = x_min + int((x_max - x_min) * ratio_x)
    y_click = y_min + int((y_max - y_min) * ratio_y)
    
    print(f"Vùng {i} đã lấy: (x1={x_min}, y1={y_min}, x2={x_max}, y2={y_max})")
    print(f"Tỷ lệ đã dùng: ({ratio_x}, {ratio_y})")
    print(f"Tọa độ điểm click đã tính: ({x_click}, {y_click})")
    try:
        pyautogui.click(x_click, y_click)
        print(f"Đã click tại tọa độ ({x_click}, {y_click})")
        return True
    except Exception as e:
        print(f"Lỗi khi thực hiện click: {e}")
        return False

def tx_tg_khung(i, ten_anh_khung="khung.png", crop_ratios=(0.889, 0.04, 0.25, 0.65)):
    """
    Hàm trích xuất thời gian từ một khung mẫu trong vùng đã xác định và trả về tổng số giây.
    Nếu OCR trả về dạng hhmmss sẽ tự tách thành hh:mm:ss.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, "data", "dulieu.json")

    # Đọc tọa độ vùng từ file JSON
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            dulieu = json.load(f)

        vung_dict = dulieu.get("vung", {})
        vung = vung_dict.get(str(i))
        if not vung:
            print(f"Không tìm thấy vùng {i} trong dulieu.json")
            return 0

        toa_do = vung.get("toa_do", {})
        x_search = int(toa_do.get("x1", 0))
        y_search = int(toa_do.get("y1", 0))
        x2_search = int(toa_do.get("x2", 0))
        y2_search = int(toa_do.get("y2", 0))

    except Exception as e:
        print(f"Lỗi khi đọc tọa độ vùng {i}: {e}")
        return 0

    try:
        # Chụp màn hình của vùng tìm kiếm
        search_region_img = ImageGrab.grab(bbox=(x_search, y_search, x2_search, y2_search))
        search_region_cv = cv2.cvtColor(np.array(search_region_img), cv2.COLOR_RGB2BGR)

        # Tải ảnh mẫu
        template_path = os.path.join(base_dir, "buttons", ten_anh_khung)
        template = cv2.imread(template_path)
        if template is None:
            raise FileNotFoundError(f"Không tìm thấy file ảnh mẫu {ten_anh_khung} tại {template_path}")

        # Tìm khung mẫu
        result = cv2.matchTemplate(search_region_cv, template, cv2.TM_CCOEFF_NORMED)
        _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.6:
            x_khung_relative, y_khung_relative = max_loc
            w_khung, h_khung = template.shape[1], template.shape[0]

            # Cắt ảnh theo crop_ratios
            left_margin_ratio, right_margin_ratio, top_margin_ratio, bottom_margin_ratio = crop_ratios
            x1_crop = x_khung_relative + int(w_khung * left_margin_ratio)
            y1_crop = y_khung_relative + int(h_khung * top_margin_ratio)
            x2_crop = x_khung_relative + w_khung - int(w_khung * right_margin_ratio)
            y2_crop = y_khung_relative + h_khung - int(h_khung * bottom_margin_ratio)

            crop_img = search_region_img.crop((x1_crop, y1_crop, x2_crop, y2_crop))

            # Lưu ảnh debug
            os.makedirs(os.path.join(base_dir, "debug"), exist_ok=True)
            debug_filename = f"tx_{os.path.splitext(ten_anh_khung)[0]}_vung_{i}.png"
            crop_img.save(os.path.join(base_dir, "debug", debug_filename))

            # OCR
            text = pytesseract.image_to_string(crop_img, config='--psm 6').strip()
            text = ''.join(c for c in text if c.isdigit() or c == ':')

            gio, phut, giay = 0, 0, 0
            try:
                text_digits = ''.join(c for c in text if c.isdigit())

                if len(text_digits) == 6:  # Mặc định dạng hhmmss
                    gio = int(text_digits[0:2])
                    phut = int(text_digits[2:4])
                    giay = int(text_digits[4:6])
                    text = f"{gio:02}:{phut:02}:{giay:02}"
                else:
                    # Fallback khi không đủ 6 số
                    parts = text.split(':')
                    if len(parts) == 3:
                        gio, phut, giay = map(int, parts)
                    elif len(parts) == 2:
                        phut, giay = map(int, parts)
                    elif len(parts) == 1 and parts[0].isdigit():
                        giay = int(parts[0])

                    text = f"{gio:02}:{phut:02}:{giay:02}"

            except (ValueError, IndexError):
                print(f"Lỗi: Không thể phân tích thời gian từ chuỗi '{text}'")
                return 0

            tong_giay = gio * 3600 + phut * 60 + giay
            print(f"[{os.path.splitext(ten_anh_khung)[0]}] Vùng {i}: OCR='{text}', Tổng giây={tong_giay}")
            return tong_giay

        else:
            print(f"Không tìm thấy khung mẫu '{ten_anh_khung}' trong vùng đã xác định.")
            return 0

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return 0




#=================================================================================
def ghi_toa_do(x,y):
    dia_chi_hien_tai=os.path.dirname(os.path.abspath(__file__))
    dia_chi_file=os.path.join(dia_chi_hien_tai, "data", "toa_do.txt")
    try:
        with open(dia_chi_file,"w",encoding="utf-8") as f:
            f.write(f"{x}\n{y}")
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn '{dia_chi_hien_tai}'")

def doc_toa_do():
    dia_chi_hien_tai=os.path.dirname(os.path.abspath(__file__))
    dia_chi_file=os.path.join(dia_chi_hien_tai, "data", "toa_do.txt")

    if not os.path.exists(dia_chi_file):
        print(f"Lỗi: Không tìm thấy file '{dia_chi_file}'.")
        return None, None

    try:
        with open(dia_chi_file,"r",encoding="utf-8") as f:
            toado=f.readlines()

            if len(toado)<2:
                print("Toa Do Khong Du X va Y")
                return None,None
            toa_do_x=int(toado[0].strip())
            toa_do_y=int(toado[1].strip())
            return toa_do_x,toa_do_y
    except ValueError:
        print("Lỗi: Dữ liệu trong file không phải là số nguyên.")
        return None, None
    except Exception as e:
        print(f"Lỗi khi đọc file: {e}")
        return None, None
#=================================================================================
def tx_tu_man_hinh(i, crop_ratio=(0.2, 0.2, 0.2, 0.2), mode="toado"):
    """
    Trích xuất ký tự từ vùng màn hình được chỉ định trong file JSON,
    với các chế độ lọc khác nhau.

    Args:
        i (int): Chỉ mục vùng (1-based index) trong dulieu.json.
        crop_ratio (tuple): Tỷ lệ lề (trái, phải, trên, dưới) để cắt ảnh.
        mode (str): Chế độ trích xuất:
            - "toado": chỉ giữ x,y (XY) và số
            - "so": chỉ giữ số
            - "chu": chỉ giữ chữ Latin
            - "all": giữ nguyên toàn bộ OCR (chỉ strip khoảng trắng)

    Returns:
        str: Chuỗi đã trích xuất theo chế độ
    """
    try:
        i = int(i)
    except ValueError:
        print(f"Lỗi: Tham số i='{i}' không phải số nguyên")
        return ""

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, "data", "dulieu.json")

    try:
        if not os.path.exists(data_file):
            print(f"Lỗi: Không tìm thấy file dữ liệu tại '{data_file}'")
            return ""

        with open(data_file, "r", encoding="utf-8") as f:
            dulieu = json.load(f)

        vung_dict = dulieu.get("vung", {})
        vung = vung_dict.get(str(i))
        if not vung:
            print(f"Không tìm thấy vùng {i} trong dulieu.json")
            return ""

        toa_do = vung.get("toa_do", {})
        x1, y1, x2, y2 = (int(toa_do.get("x1", 0)),
                           int(toa_do.get("y1", 0)),
                           int(toa_do.get("x2", 0)),
                           int(toa_do.get("y2", 0)))

    except Exception as e:
        print(f"Lỗi khi đọc tọa độ vùng {i} từ file: {e}")
        return ""

    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    width, height = img.size

    left_margin = int(width * crop_ratio[0])
    right_margin = int(width * crop_ratio[1])
    top_margin = int(height * crop_ratio[2])
    bottom_margin = int(height * crop_ratio[3])

    crop_img = img.crop((
        left_margin,
        top_margin,
        width - right_margin,
        height - bottom_margin
    ))

    text_ocr_raw = pytesseract.image_to_string(crop_img, config='--psm 6').strip()

    # Lọc theo chế độ
    if mode == "toado":
        text_trich_xuat = re.sub(r'[^xyXY0-9]+', '', text_ocr_raw)
    elif mode == "so":
        text_trich_xuat = re.sub(r'[^0-9]+', '', text_ocr_raw)
    elif mode == "chu":
        text_trich_xuat = re.sub(r'[^a-zA-Z]+', '', text_ocr_raw)
    elif mode == "all":
        text_trich_xuat = text_ocr_raw
    else:
        print(f"Chế độ '{mode}' không hợp lệ, mặc định dùng 'all'")
        text_trich_xuat = text_ocr_raw

    print(f"[{__name__}] Vùng {i}, chế độ={mode}: OCR gốc='{text_ocr_raw}', đã lọc='{text_trich_xuat}'")

    return text_trich_xuat


def lay_so_tu_chuoi(chuoi_dau_vao):
    """
    Trích xuất tất cả các chữ số từ một chuỗi bất kỳ.
    Sử dụng biểu thức chính quy để tìm tất cả các chuỗi con chứa số, sau đó nối chúng lại.
    Args:
        chuoi_dau_vao (str): Chuỗi chứa cả chữ và số.
    Returns:
        str: Chuỗi chỉ chứa các chữ số.
    """
    # Biểu thức chính quy '\d+' tìm kiếm một hoặc nhiều chữ số đứng liền nhau.
    # re.findall() sẽ trả về một danh sách các chuỗi số tìm được.
    danh_sach_so = re.findall(r'\d+', chuoi_dau_vao)
    
    # Nối tất cả các chuỗi số trong danh sách lại thành một chuỗi duy nhất.
    ket_qua = "".join(danh_sach_so)
    
    return ket_qua

def tach_chuoi_toa_do(chuoi_dau_vao):
    """
    Tách chuỗi OCR thành 2 số nguyên (x, y).
    Hỗ trợ nhiều biến thể như: X123Y456, Xx123Y456, X123Yy456, Xx123Yy456...
    """
    if not chuoi_dau_vao:
        return None, None

    # Chuẩn hóa chuỗi: bỏ ký tự lạ, xuống dòng...
    s = str(chuoi_dau_vao).strip()
    s = s.replace("\n", "").replace("\r", "")

    # Tìm tất cả số trong chuỗi
    numbers = re.findall(r"\d+", s)

    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    return None, None

def tx_toa_do(i, crop_ratio=(0.2, 0.2, 0.2, 0.2)):
    chuoi_dau_vao=tx_tu_man_hinh(i,crop_ratio)
    x,y=tach_chuoi_toa_do(chuoi_dau_vao)
    return x,y


#========================= GEMS =============================
def tx_gems(i,filename="khung.png", che_do=1, crop_ratio=None):
    """
    Hàm trích xuất số bằng cách tìm khung mẫu trong một vùng đã xác định.
    Tỷ lệ cắt được truyền vào qua tham số `crop_ratio`.
    Hàm này giả định rằng `crop_ratio` luôn là một tuple hợp lệ.

    Args:
        i: Vùng (1-based index) cần trích xuất.
        che_do: Chế độ trích xuất (1: văn bản tiếng Việt, 2: chỉ 'x,y' và số).
        crop_ratio: Tuple chứa các tỷ lệ cắt: (top, bottom, left, right).
    
    Returns:
        tuple: (chuỗi văn bản trích xuất, ảnh đã cắt)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, "data", "dulieu.json")
    
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            dulieu = json.load(f)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file dulieu.json tại {data_file}.")
        return "", None
    except json.JSONDecodeError:
        print(f"Lỗi: File dulieu.json bị lỗi định dạng.")
        return "", None

    vung_dict = dulieu.get("vung", {})
    vung = vung_dict.get(str(i))
    if not vung:
        print(f"Lỗi: Không tìm thấy vùng {i} trong dulieu.json")
        return "", None

    toa_do = vung.get("toa_do", {})
    if not toa_do:
        print(f"Lỗi: Thiếu 'toa_do' cho vùng {i} trong dulieu.json")
        return "", None

    # Lấy tỷ lệ cắt
    top_ratio, bottom_ratio, left_ratio, right_ratio = crop_ratio
    
    try:
        # --- 1. Lấy tọa độ vùng tìm kiếm
        x_search, y_search, x2_search, y2_search = \
            toa_do.get("x1", 0), toa_do.get("y1", 0), toa_do.get("x2", 0), toa_do.get("y2", 0)
        
        # Chụp vùng tìm kiếm
        search_region_img = ImageGrab.grab(bbox=(x_search, y_search, x2_search, y2_search))
        search_region_cv = cv2.cvtColor(np.array(search_region_img), cv2.COLOR_RGB2BGR)

        # --- 2. Đọc ảnh mẫu khung
        template_path = os.path.join(base_dir, "buttons", filename)
        template = cv2.imread(template_path)
        if template is None:
            raise FileNotFoundError(f"Không tìm thấy file ảnh mẫu khung.png tại {template_path}")

        # --- 3. Tìm khung
        result = cv2.matchTemplate(search_region_cv, template, cv2.TM_CCOEFF_NORMED)
        _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.8:  # Ngưỡng độ chính xác
            x_khung_rel, y_khung_rel = max_loc
            w_khung, h_khung = template.shape[1], template.shape[0]

            # --- 4. Tọa độ tuyệt đối của khung
            x_khung_abs = x_search + x_khung_rel
            y_khung_abs = y_search + y_khung_rel

            # --- 5. Tính toán crop bên trong khung
            x1_abs = x_khung_abs + int(w_khung * left_ratio)
            x2_abs = x_khung_abs + int(w_khung * (1 - right_ratio))
            y1_abs = y_khung_abs + int(h_khung * top_ratio)
            y2_abs = y_khung_abs + int(h_khung * (1 - bottom_ratio))

            # --- 6. Crop trực tiếp từ toàn màn hình
            full_screen = ImageGrab.grab()
            crop_img = full_screen.crop((x1_abs, y1_abs, x2_abs, y2_abs))

            # --- 7. Lưu debug
            os.makedirs(os.path.join(base_dir, "debug"), exist_ok=True)
            crop_img.save(os.path.join(base_dir, "debug", f"tx_gems_vung_{i}.png"))

            # --- 8. OCR
            text = pytesseract.image_to_string(
                crop_img,
                lang='vie',
                config='--psm 7'
            ).strip()

            if che_do == 2:
                cleaned_text = re.sub(r'[^xyXY0-9]', '', text)
            else:
                cleaned_text = text

            print(f"[tx_gems] Vùng {i}: OCR='{cleaned_text}'")
            return cleaned_text, crop_img
        else:
            print("Không tìm thấy khung mẫu trong vùng đã xác định.")
            return "", None

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return "", None



#============ XU LY QUET GEMS =====================

def nhap_ban_phim(i,chuoi_ky_tu=""):
    for kytuchuoi in chuoi_ky_tu:
        kytuchuoi+=".png"
        click_co_ban(i,kytuchuoi)
        time.sleep(0.2)
    click_co_ban(i,"done.png")



def click_vao_toa_do(x,y):
    pyautogui.click(x,y)
    time.sleep(1)


def nhap_toa_do(i, x, y):
    x_temp=x
    y_temp=y
    time.sleep(0.8)
    click_theo_toa_do(i,0.25,0.03)
    time.sleep(0.8)
    x_input = str(x_temp)  # chỉ dùng local variable
    y_input = str(y_temp)
    click_theo_toa_do(i,0.5,0.2)
    time.sleep(0.8)
    nhap_ban_phim(i, x_input)
    time.sleep(0.8)
    click_theo_toa_do(i,0.64,0.2)
    time.sleep(0.8)
    nhap_ban_phim(i, y_input)
    time.sleep(0.8)
    click_theo_toa_do(i,0.69,0.19)
    time.sleep(0.8)





def chuan_hoa_text_nguoi_thu_hoach(text_ocr: str) -> str:
    if not isinstance(text_ocr, str):
        text_ocr = str(text_ocr)

    # chuẩn hóa unicode NFC (gom dấu về dạng chuẩn)
    text_clean = unicodedata.normalize("NFC", text_ocr)

    # bỏ khoảng trắng dư thừa + lowercase
    text_clean = text_clean.strip().lower()
    text_clean = re.sub(r"\s+", " ", text_clean)

    # chuẩn hóa 'không có'
    if text_clean in ["khong co", "không co", "không có"]:
        return "không có"

    return text_clean




_templates_cache = {}

def dem_va_xu_ly_diem_trung(i, filename="gems_map.png", threshold=0.85):
    """
    Tìm tất cả điểm khớp ảnh mẫu trong vùng i.
    - Đọc tọa độ từ data/dulieu.json
    - Cắt màn hình trong vùng đó
    - So khớp template (grayscale)
    - Gom nhóm trùng lặp
    - Trả về list [(cx, cy), ...]

    Args:
        i (int|str): số vùng (1-based index)
        filename (str): tên file mẫu (có hoặc không .png)
        threshold (float): ngưỡng khớp (0-1)
    """
    try:
        i = int(i)
    except ValueError:
        print(f"Lỗi: Tham số i='{i}' không phải số nguyên")
        return []

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "data", "dulieu.json")
    buttons_dir = os.path.join(base_dir, "buttons")

    # chuẩn hóa tên file
    if not filename.lower().endswith(".png"):
        filename += ".png"
    img_path = os.path.join(buttons_dir, filename)

    # --- đọc template (có cache) ---
    if img_path not in _templates_cache:
        if not os.path.exists(img_path):
            print(f"Lỗi: Không tìm thấy file mẫu {img_path}")
            return []
        tmpl = cv2.imread(img_path, cv2.IMREAD_COLOR)
        if tmpl is None:
            print(f"Lỗi: Không thể đọc file mẫu {img_path}")
            return []
        _templates_cache[img_path] = tmpl
    template = _templates_cache[img_path]
    th, tw = template.shape[:2]

    # --- đọc tọa độ vùng ---
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        toa_do = data.get("vung", {}).get(str(i), {}).get("toa_do")
        if not toa_do:
            print(f"Không tìm thấy vùng {i} hoặc thiếu tọa độ")
            return []
        x1, y1, x2, y2 = int(toa_do["x1"]), int(toa_do["y1"]), int(toa_do["x2"]), int(toa_do["y2"])
    except Exception as e:
        print(f"Lỗi khi đọc tọa độ vùng {i}: {e}")
        return []

    # --- cắt ảnh màn hình ---
    bbox = (x1, y1, x2, y2)
    img_screen = ImageGrab.grab(bbox)
    img_screen = cv2.cvtColor(np.array(img_screen), cv2.COLOR_RGB2BGR)

    # --- grayscale ---
    img_gray = cv2.cvtColor(img_screen, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # --- template matching ---
    result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)

    # gom cụm
    rects = [[pt[0], pt[1], tw, th] for pt in zip(*loc[::-1])]
    rects, _ = cv2.groupRectangles(rects, groupThreshold=1, eps=0.5)

    if len(rects) == 0:
        print(f"Không tìm thấy {filename} trong vùng {i} (ngưỡng {threshold}).")
        return []

    # --- tính tâm ---
    points = []
    for idx, (px, py, _, _) in enumerate(rects, 1):
        cx = x1 + px + tw // 2
        cy = y1 + py + th // 2
        points.append((cx, cy))
        print(f"Điểm {idx} khớp {filename}: Tâm ({cx},{cy}), ngưỡng≥{threshold}")
        try:
            print("chua co ham")  # gọi hàm ngoài nếu có
        except NameError:
            pass  # nếu chưa định nghĩa thì bỏ qua

    return points

def lay_thong_tin_gems(i):
    """
    Lấy bán kính của vùng i từ file dulieu.json và trả về kiểu int.
    Nếu không tìm thấy hoặc không hợp lệ, trả về None.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "data", "dulieu.json")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("Lỗi khi đọc file dulieu.json:", e)
        return None  # Trả về None thay vì False

    try:
        ban_kinh_str = data["vung"][str(i)]["map_var"].get("ban_kinh")
        print(f"DEBUG: ban_kinh_str = {ban_kinh_str!r}")
        if ban_kinh_str is None:
            print(f"Vùng {i} không có giá trị 'ban_kinh'")
            return None

        # Ép kiểu int, đảm bảo không bị lỗi chuỗi
        return int(ban_kinh_str)

    except KeyError:
        print(f"Không tìm thấy dữ liệu 'ban_kinh' cho vùng {i}")
        return None
    except (ValueError, TypeError):
        print(f"Giá trị 'ban_kinh' của vùng {i} không hợp lệ ({ban_kinh_str})")
        return None

def click_trong_vung(x1, y1, x2, y2, filename, threshold=0.8):
    """
    Click vào ảnh mẫu trong vùng chỉ định.

    x1, y1, x2, y2: tọa độ vùng (pixel)
    filename: tên file ảnh mẫu (có thể bỏ .png)
    threshold: ngưỡng khớp ảnh (0-1)
    """

    # Chụp ảnh trong vùng
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    screenshot_rgb = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_rgb, cv2.COLOR_RGB2BGR)

    # Đường dẫn file ảnh mẫu
    base_dir = os.path.dirname(os.path.abspath(__file__))
    buttons_dir = os.path.join(base_dir, "buttons")

    if not filename.lower().endswith(".png"):
        filename += ".png"
    template_path = os.path.join(buttons_dir, filename)

    if not os.path.exists(template_path):
        print(f"Không tìm thấy file mẫu: {template_path}")
        return False

    # Đọc file mẫu
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"Không thể đọc file ảnh mẫu: {template_path}")
        return False

    # So khớp template
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        click_x = x1 + max_loc[0] + w // 2
        click_y = y1 + max_loc[1] + h // 2
        pyautogui.click(click_x, click_y)
        print(f"Đã click tại ({click_x}, {click_y}) - Độ khớp: {max_val:.2f}")
        return True
    else:
        print(f"Không tìm thấy ảnh '{filename}' trong vùng ({x1},{y1},{x2},{y2}) - Độ khớp {max_val:.2f}")
        return False

def toa_do_con(i, tlx1, tly1, tlx2, tly2):
    try:
        dia_chi_code = os.path.dirname(os.path.abspath(__file__))
        dia_chi_file = os.path.join(dia_chi_code, "data", "dulieu.json")

        with open(dia_chi_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Kiểm tra cấu trúc
        if "vung" not in data or not isinstance(data["vung"], dict):
            print("Lỗi: File dulieu.json không chứa danh sách 'vung'")
            return False

        vung = data["vung"].get(str(i))
        if not vung:
            print(f"Không tìm thấy vùng {i} trong file dữ liệu")
            return False

        toa_do = vung.get("toa_do")
        if not toa_do:
            print(f"Vùng {i} không có thông tin tọa độ")
            return False

        # Tọa độ gốc
        x1_val, y1_val = int(toa_do["x1"]), int(toa_do["y1"])
        x2_val, y2_val = int(toa_do["x2"]), int(toa_do["y2"])

    except Exception as e:
        print(f"Lỗi khi đọc tọa độ vùng {i}: {e}")
        return False

    # Tính chiều rộng, chiều cao
    w = x2_val - x1_val
    h = y2_val - y1_val

    # Tính tọa độ con theo tỉ lệ
    x1_con = int(x1_val + w * tlx1)
    y1_con = int(y1_val + h * tly1)
    x2_con = int(x1_val + w * tlx2)
    y2_con = int(y1_val + h * tly2)

    return x1_con, y1_con, x2_con, y2_con


def click_vung_con(i,filename,che_do):
    if che_do==1:
        tilex1,tiley1,tilex2,tiley2=0.37,0.32,0.95,0.5
    elif che_do==2:
        tilex1,tiley1,tilex2,tiley2=0.37,0.5,0.95,0.68
    elif che_do==3:
        tilex1,tiley1,tilex2,tiley2=0.37,0.7,0.95,0.88
    x1,y1,x2,y2=toa_do_con(i,tilex1,tiley1,tilex2,tiley2)
    return click_trong_vung(x1,y1,x2,y2,filename,0.85)