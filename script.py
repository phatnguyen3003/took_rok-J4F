import chuc_nang
from chuc_nang import click_co_ban, click_trong_vung, nhap_ban_phim, tach_chuoi_toa_do,tx_du_tru,tx_hanh_quan,tinh_tong_thoi_gian,click_lech,tx_so,kiem_tra_nut,giu_nut,vuot_trong_vung,tx_thoi_gian,tx_tg_khung,tx_toa_do,tx_gems,click_theo_toa_do,lay_thong_tin_gems,nhap_toa_do,click_vung_con,chuan_hoa_text_nguoi_thu_hoach
import time
import random
import pyautogui

toa_do_x,toa_do_y,id_vung=None,None,None
mang_co_do_hang=[0]*3

def randomtg(x=2,y=3):
        return random.randint(x,y)


def chay_lt(i):
    while click_co_ban(i,"xac_nhan_ket_noi.png"):
        time.sleep(7)
        if not click_co_ban(i,"xac_nhan_ket_noi.png"):
            break
    click_co_ban(i,"mo_map.png")
    time.sleep(randomtg())
    click_co_ban(i,"tim.png")
    time.sleep(randomtg())
    click_co_ban(i,"dat_trong.png")
    time.sleep(randomtg())
    click_co_ban(i,"tim_kiem.png")
    time.sleep(randomtg())
    du_tru_time=tx_du_tru(i)
    time.sleep(6)
    click_co_ban(i,"thu_thap.png")
    time.sleep(randomtg())
    click_co_ban(i,"quan_moi.png")
    time.sleep(randomtg())
    hanh_quan_time=tx_hanh_quan(i)
    time.sleep(6)
    click_co_ban(i,"hanh_quan.png")
    time.sleep(randomtg())
    click_co_ban(i,"ve_thanh.png")
    tongtg=tinh_tong_thoi_gian(du_tru_time,hanh_quan_time)
    time.sleep(randomtg())
    return tongtg

def chay_go(i):
    while click_co_ban(i,"xac_nhan_ket_noi.png"):
        time.sleep(7)
        if not click_co_ban(i,"xac_nhan_ket_noi.png"):
            break
    click_co_ban(i,"mo_map.png")
    time.sleep(randomtg())
    click_co_ban(i,"tim.png")
    time.sleep(randomtg())
    click_co_ban(i,"xe_go.png")
    time.sleep(randomtg())
    click_co_ban(i,"tim_kiem.png")
    time.sleep(randomtg())
    du_tru_time=tx_du_tru(i)
    time.sleep(6)
    click_co_ban(i,"thu_thap.png")
    time.sleep(randomtg())
    click_co_ban(i,"quan_moi.png")
    time.sleep(randomtg())
    hanh_quan_time=tx_hanh_quan(i)
    time.sleep(6)
    click_co_ban(i,"hanh_quan.png")
    time.sleep(randomtg())
    click_co_ban(i,"ve_thanh.png")
    tongtg=tinh_tong_thoi_gian(du_tru_time,hanh_quan_time)
    time.sleep(randomtg())
    return tongtg

def chay_da(i):
    while click_co_ban(i,"xac_nhan_ket_noi.png"):
        time.sleep(7)
        if not click_co_ban(i,"xac_nhan_ket_noi.png"):
            break
    click_co_ban(i,"mo_map.png")
    time.sleep(randomtg())
    click_co_ban(i,"tim.png")
    time.sleep(randomtg())
    click_co_ban(i,"tram_tich_da.png")
    time.sleep(randomtg())
    click_co_ban(i,"tim_kiem.png")
    time.sleep(randomtg())
    du_tru_time=tx_du_tru(i)
    time.sleep(6)
    click_co_ban(i,"thu_thap.png")
    time.sleep(randomtg())
    click_co_ban(i,"quan_moi.png")
    time.sleep(randomtg())
    hanh_quan_time=tx_hanh_quan(i)
    time.sleep(6)
    click_co_ban(i,"hanh_quan.png")
    time.sleep(randomtg())
    click_co_ban(i,"ve_thanh.png")
    tongtg=tinh_tong_thoi_gian(du_tru_time,hanh_quan_time)
    time.sleep(randomtg())
    return tongtg

def chay_vang(i):
    while click_co_ban(i,"xac_nhan_ket_noi.png"):
        time.sleep(7)
        if not click_co_ban(i,"xac_nhan_ket_noi.png"):
            break
    click_co_ban(i,"mo_map.png")
    time.sleep(randomtg())
    click_co_ban(i,"tim.png")
    time.sleep(randomtg())
    click_co_ban(i,"tram_tich_vang.png")
    time.sleep(randomtg())
    click_co_ban(i,"tim_kiem.png")
    time.sleep(randomtg())
    du_tru_time=tx_du_tru(i)
    time.sleep(6)
    click_co_ban(i,"thu_thap.png")
    time.sleep(randomtg())
    click_co_ban(i,"quan_moi.png")
    time.sleep(randomtg())
    hanh_quan_time=tx_hanh_quan(i)
    time.sleep(6)
    click_co_ban(i,"hanh_quan.png")
    time.sleep(randomtg())
    click_co_ban(i,"ve_thanh.png")
    tongtg=tinh_tong_thoi_gian(du_tru_time,hanh_quan_time)
    time.sleep(randomtg())
    return tongtg



def gop_lm(i):
     #======== VAO LIEN MINH =============
    click_co_ban(i,"lien_minh.png")
    time.sleep(randomtg())
    click_co_ban(i,"tab_cn.png")
    time.sleep(randomtg())
    click_lech(i,"gioi_thieu.png",0,25)
    time.sleep(randomtg())
    so_lan_can_click=tx_so(i,(0.765,0.215,0.7,0.27))
    if so_lan_can_click>20:
        so_lan_can_click=20
    time.sleep(randomtg())
    for g in range(so_lan_can_click):
        click_co_ban(i,"tang_tn.png")
        time.sleep(2)
    time.sleep(randomtg())
    click_co_ban(i,"thoat.png")
    time.sleep(randomtg())
    click_co_ban(i,"thoat.png")
    time.sleep(randomtg())
    click_co_ban(i,"qua_tang.png")
    time.sleep(randomtg())
    click_co_ban(i,"nhan_tat.png")
    time.sleep(randomtg())
    click_co_ban(i,"xac_nhan.png")
    time.sleep(randomtg())
    click_co_ban(i,"thoat.png")
    time.sleep(randomtg())
    click_co_ban(i,"thoat.png")
    time.sleep(randomtg())

def giup_lm(i):
    #======== KIEM TRA GIUP DO =============
    click_co_ban(i,"giup_do.png")
    time.sleep(randomtg())

def mo_vip(i):
    click_theo_toa_do(i,0.125,0.095)
    time.sleep(randomtg())
    if kiem_tra_nut(i,"nut_nhan_vip1.png"):
        click_co_ban(i,"nut_nhan_vip1.png")
        time.sleep(randomtg())
        click_co_ban(i,"nut_thoat.png")
        time.sleep(randomtg())
    else:
        print(f"nhan vip so 1 cua vung {i} dang hoi")
        time.sleep(randomtg())
    if kiem_tra_nut(i,"nut_nhan_vip2.png"):
        click_co_ban(i,"nut_nhan_vip2.png")
        time.sleep(randomtg())
        click_co_ban(i,"nut_thoat.png")
        time.sleep(randomtg())
        click_co_ban(i,"thoat.png")
        time.sleep(randomtg())
    else:
         print(f"nhan vip so 2 cua vung {i} dang hoi")
         time.sleep(randomtg())
         click_co_ban(i,"thoat.png")
         time.sleep(randomtg())

def tac_vu_thong_thuong(i):
    time.sleep(2)
    if kiem_tra_nut(i,"lien_minh.png"):
        pass
    else:
        click_co_ban(i,"mo_rong.png")
        time.sleep(randomtg())
    giup_lm(i)
    gop_lm(i)
    mo_vip(i)
    click_co_ban(i,"mo_rong.png")
    time.sleep(randomtg())
    print(f"Da Ket Thuc Tac Vu Co Ban Cua Vung {i}")
    time.sleep(1)


def trinh_sat(i):
    while click_co_ban(i,"xac_nhan_ket_noi.png"):
        time.sleep(7)
        if not click_co_ban(i,"xac_nhan_ket_noi.png"):
            break
    time.sleep(randomtg())
    if kiem_tra_nut(i,"lien_minh.png"):
        click_co_ban(i,"mo_rong.png")
        time.sleep(randomtg())
    time.sleep(randomtg())
    click_co_ban(i,"leu_ts.png")
    time.sleep(randomtg())
    click_co_ban(i,"trinh_sat.png")
    time.sleep(randomtg())
    giay_con_lai=tx_thoi_gian(i,(0.624,0.315,0.35,0.59))

    if giay_con_lai>0:
        click_co_ban(i,"thoat.png")
        return giay_con_lai
    else:
        click_co_ban(i,"tham_do1.png")
        time.sleep(randomtg(2,4))
        click_co_ban(i,"tham_do2.png")
        time.sleep(randomtg())
        giay_di_toi=tx_tg_khung(i,"khung_ts.png",(0.3,0.3,0.45,0.42))
        time.sleep(randomtg())
        click_co_ban(i,"gui_ts.png")
        time.sleep(randomtg())
        giay_di_toi+=280
        click_co_ban(i,"ve_thanh.png")
        time.sleep(randomtg(2,4))
        return giay_di_toi
    

def chay_gems(i):
    #ngang +12 doc +12
    global toa_do_x,toa_do_y,id_vung
    click_co_ban(i,"mo_map.png")
    time.sleep(randomtg())
    click_theo_toa_do(i,0.5,0.5)
    time.sleep(randomtg())
    x_goc,y_goc=tach_chuoi_toa_do(tx_gems(i,"khung_nha_chinh.png",2,(0.05,0.88,0.38,0.375)))
    x_goc = int(x_goc)
    y_goc = int(y_goc)

    print(f"x_goc = {x_goc}, type = {type(x_goc)}")
    print(f"y_goc = {y_goc}, type = {type(y_goc)}")
    ban_kinh=lay_thong_tin_gems(i)
    ban_kinh=int(ban_kinh)
    print(f"ban kinh la {ban_kinh}")
    print(f"ban_kinh={ban_kinh}, type={type(ban_kinh)}")
    bien_trai = int(x_goc) - int(ban_kinh)
    if bien_trai<20:
        bien_trai=20
    bien_phai = int(x_goc) + int(ban_kinh)
    if bien_phai>1180:
        bien_phai=1180
    bien_tren = int(y_goc) + int(ban_kinh)
    if bien_tren>1180:
        bien_tren=1180
    bien_duoi = int(y_goc) - int(ban_kinh)
    if bien_duoi<20:
        bien_duoi=20
    click_theo_toa_do(i,0.5,0.5)
    click_co_ban(i,"ve_thanh.png")
    time.sleep(0.5)
    click_co_ban(i,"mo_map.png")
    time.sleep(0.6)
    click_theo_toa_do(i,0.5,0.5)
    time.sleep(1)
    click_theo_toa_do(i,0.5,0.5)
    pyautogui.keyDown("ctrl")
    time.sleep(0.25)
    pyautogui.scroll(-800)
    time.sleep(0.2)
    pyautogui.keyUp("ctrl")
    time.sleep(3)
    if id_vung!=i:
        id_vung=i
        toa_do_x=bien_trai
        toa_do_y=bien_duoi
    while True:
        nhap_toa_do(i, toa_do_x, toa_do_y)
        time.sleep(1)
        if click_co_ban(i,"gems1.png",0.75) or click_co_ban(i,"gems2.png",0.75):
            time.sleep(1)
            gems_tx=int(tx_gems(i,"khung.png",1,(0.27,0.562,0.75,0.05)))
            if click_co_ban(i,"thu_thap.png"):
                time.sleep(randomtg())
                tong_tg=gems_tx*120
                click_co_ban(i,"thu_thap.png")
                time.sleep(randomtg())
                click_co_ban(i,"quan_moi.png")
                time.sleep(randomtg())
                tong_tg+=2*tx_hanh_quan(i)
                click_co_ban(i,"hanh_quan.png")
                time.sleep(randomtg())
                click_co_ban(i,"ve_thanh.png")
                time.sleep(0.5)
                return tong_tg
            else:
                click_theo_toa_do(i,0.5,0.5)
                pyautogui.keyDown("ctrl")
                time.sleep(0.25)
                pyautogui.scroll(-800)
                time.sleep(0.2)
                pyautogui.keyUp("ctrl")
                nhap_toa_do(i, toa_do_x, toa_do_y)
                time.sleep(randomtg())
        print(f"da duyet toa do X:{toa_do_x} Y:{toa_do_y}")
        toa_do_x += 12
        if toa_do_x > bien_phai:
            toa_do_x = bien_trai
            toa_do_y += 12
        if toa_do_y > bien_tren:
            toa_do_x = bien_trai
            toa_do_y = bien_duoi

def chay_do_hang(i):
    global mang_co_do_hang
    time.sleep(1)
    if not click_co_ban(i,"thu.png"):
        click_co_ban(i,"mo_rong.png")
        time.sleep(1)
        click_co_ban(i,"thu.png")
    time.sleep(1)
    click_co_ban(i,"bao_cao.png")
    time.sleep(randomtg())
    click_co_ban(i,"nhan_tat_thu.png")
    time.sleep(randomtg())
    click_co_ban(i,"xac_nhan_thu.png")
    time.sleep(randomtg())
    click_co_ban(i,"tham_do.png",0.75)
    time.sleep(randomtg())

    mang_co_do_hang = [0,0,0]
    count=0
    for spot in range(3):
        if click_vung_con(i,"dang_tham_do1.png",spot+1) or click_vung_con(i,"dang_tham_do2.png",spot+1):
            mang_co_do_hang[spot]=1
        elif not click_vung_con(i,"dang_tham_do1.png",spot+1) and not click_vung_con(i,"dang_tham_do2.png",spot+1):
            count+=1
    for item in mang_co_do_hang:
        print(f" {item}")
    if count==3:
        return 100
    #time.sleep(5000)
    vi_tri_che_do=None
    for g,val in enumerate(mang_co_do_hang):
        if val==1:
            vi_tri_che_do=g
            break
    if click_vung_con(i,"hang.png",vi_tri_che_do+1):
        if click_vung_con(i,"an_de_do.png",vi_tri_che_do+1):
            time.sleep(randomtg(3,4))
            click_co_ban(i,"nut_tham_do.png")
            time.sleep(randomtg())
            giay_di_toi=tx_tg_khung(i,"khung_ts.png",(0.3,0.3,0.45,0.42))
            giay_di_toi+=90
            click_co_ban(i,"gui_ts.png")
            time.sleep(randomtg())
            click_co_ban(i,"ve_thanh.png")
            time.sleep(2)
            mang_co_do_hang[vi_tri_che_do]=0
            return giay_di_toi
        else:
            return 10000000
    elif click_vung_con(i,"trai.png",vi_tri_che_do+1):
        if click_vung_con(i,"an_de_do.png",vi_tri_che_do+1):
            time.sleep(randomtg(5,6))
            click_co_ban(i,"ve_thanh.png")
            time.sleep(2)
            mang_co_do_hang[vi_tri_che_do]=0
            return 10
        else:
            return 10000000