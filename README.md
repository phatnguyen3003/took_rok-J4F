# TOOL_ROK — Trình trợ giúp thao tác màn hình (README tóm tắt)

Mô tả ngắn
-	`TOOL_ROK` là một bộ script Python để tự động thao tác GUI, chụp/cắt vùng màn hình, nhận dạng ký tự (OCR), và thực hiện các tác vụ nhấp/giữ/di chuyển chuột. Dự án dùng `tkinter`/`customtkinter` cho giao diện, `Pillow`/`OpenCV`/`numpy` cho xử lý ảnh, `pytesseract` cho OCR, và `pyautogui` cho tương tác chuột/bàn phím.

Mục tiêu của README này
-	Giải thích cấu trúc, các phụ thuộc cần cài, cách cài đặt nhanh trên Windows, cách chạy và lưu ý quan trọng.

**Cấu trúc thư mục chính**
- `TOOL_ROK.py` : Entrypoint / giao diện chính của ứng dụng.
- `chon_vung_gui.py` : Màn hình chọn vùng (GUI) để cắt/scan.
- `chuc_nang.py` : Các hàm xử lý chính (tách text, chuẩn hóa, xử lý ảnh, logic xử lý vùng).
- `hang_doi.py` : Bộ quản lý hàng đợi / thread cho chạy tác vụ nền.
- `module1.py`, `script.py` : Bộ helper và tập lệnh thực thi nhiệm vụ.
- `tx_khung.py`, `test_*.py`, `test1_*.py` : File test và các module kiểm thử/ ví dụ.
- `data/` : Chứa `config.json`, `dulieu.json` — cấu hình và dữ liệu được dùng bởi ứng dụng.
- `buttons/`, `debug/` : Các tài nguyên giao diện và log/debug.

Phụ thuộc (thư viện Python và hệ thống)
- Thư viện Python bên thứ ba (cài bằng pip):
  - `customtkinter` (giao diện hiện đại trên nền `tkinter`)
  - `Pillow` (nhập với `from PIL import ...`) — pip package name: `Pillow`
  - `opencv-python` (nhập là `cv2`)
  - `numpy` (nhập là `numpy as np`)
  - `pytesseract` (Python wrapper cho Tesseract OCR)
  - `pyautogui` (tự động nhấp chuột/nhập bàn phím)

- Thư viện chuẩn Python (thường có sẵn):
  - `tkinter`, `json`, `os`, `time`, `sys`, `re`, `ctypes`, `threading`, `queue`, `random`, `unicodedata`

- Phụ thuộc hệ thống / ngoài pip:
  - Tesseract OCR: cần cài đặt `tesseract` (ví dụ trên Windows cài Tesseract-OCR và thêm `tesseract.exe` vào `PATH`).

Cài đặt nhanh (Windows)
1. Tạo và kích hoạt virtual environment (khuyến nghị):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```



```powershell
pip install customtkinter Pillow opencv-python numpy pytesseract pyautogui
```

3. Cài Tesseract OCR (Windows):
  - Tải từ: https://github.com/tesseract-ocr/tesseract/releases (chọn bản phù hợp, thường là bản Windows installer).
  - Cài xong, thêm đường dẫn cài `tesseract.exe` vào `PATH` (ví dụ `C:\Program Files\Tesseract-OCR`).
  - Kiểm tra bằng: `tesseract --version` trong PowerShell.

4. (Tùy chọn) Nếu `pyautogui` yêu cầu thêm gói, pip sẽ cài tự động. Trên một số hệ, cần cài thêm thư viện cho screenshot region (Pillow/ pyscreeze).

Cấu hình trước khi chạy
- Mở `data/config.json` hoặc `data/dulieu.json` để chỉnh các tham số mặc định (nếu có).
- Nếu ứng dụng cần quyền truy cập màn hình (antivirus/Windows settings), cho phép.

Chạy ứng dụng
- Từ PowerShell (đã activate virtualenv):

```powershell
python TOOL_ROK.py
```

- Hoặc chạy trực tiếp file test/scrip để thực hiện các tác vụ tự động:
  - `python script.py` (nếu `script.py` là runner của tác vụ bạn muốn)

Lưu ý về OCR và môi trường
- `pytesseract` chỉ là wrapper; bạn vẫn cần cài Tesseract binary. Nếu `pytesseract` báo lỗi không tìm `tesseract.exe`, kiểm tra PATH hoặc set `pytesseract.pytesseract.tesseract_cmd` trỏ trực tiếp tới `tesseract.exe`.

Ví dụ setting:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Chạy tests:
- Repo chứa nhiều file `test_*.py`. Bạn có thể chạy từng file bằng Python hoặc dùng `pytest` nếu muốn tổ chức tests:

```powershell
pip install pytest
pytest -q
```

Tối ưu hóa và gợi ý
- Nếu ứng dụng chụp màn hình nhiều, cân nhắc dùng `region` để giảm kích thước ảnh và tăng tốc xử lý.
- Dùng `numpy` + `cv2` cho tiền xử lý ảnh trước OCR (chuyển grayscale, thresholding, morphological operations) để tăng độ chính xác OCR.
- Nếu gặp vấn đề với `pyautogui`, kiểm tra quyền/driver chuột ảo/antivirus.

Các file cấu hình/ dữ liệu quan trọng
- `data/config.json` : cấu hình ứng dụng (đường dẫn, tham số OCR, timeout...)
- `data/dulieu.json` : dữ liệu lưu trữ người dùng/ hoặc dự liệu mẫu



---
