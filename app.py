import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Quản lý phòng trọ",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Hệ thống quản lý phòng trọ")

# ===== Sidebar =====
st.sidebar.header("⚙️ Bảng giá")

gia_phong_mac_dinh = st.sidebar.number_input(
    "Tiền phòng",
    min_value=0,
    value=2500000
)

gia_dien = st.sidebar.number_input(
    "Giá điện (VNĐ/kWh)",
    min_value=0,
    value=3500
)

gia_nuoc = st.sidebar.number_input(
    "Giá nước (VNĐ/m³)",
    min_value=0,
    value=15000
)

wifi = st.sidebar.number_input(
    "Wifi",
    min_value=0,
    value=100000
)

rac = st.sidebar.number_input(
    "Rác",
    min_value=0,
    value=50000
)

so_phong = st.number_input(
    "Số lượng phòng",
    min_value=1,
    value=10
)

du_lieu = []

for i in range(1, so_phong + 1):

    st.subheader(f"🏠 Phòng {i}")

    c1, c2, c3 = st.columns(3)

    with c1:
        gia_phong = st.number_input(
            "Giá phòng",
            value=gia_phong_mac_dinh,
            key=f"gia{i}"
        )

        dien_cu = st.number_input(
            "Điện cũ",
            value=0,
            key=f"dc{i}"
        )

        dien_moi = st.number_input(
            "Điện mới",
            value=0,
            key=f"dm{i}"
        )

    with c2:
        nuoc_cu = st.number_input(
            "Nước cũ",
            value=0,
            key=f"nc{i}"
        )

        nuoc_moi = st.number_input(
            "Nước mới",
            value=0,
            key=f"nm{i}"
        )

    dien = max(0, dien_moi - dien_cu)
    nuoc = max(0, nuoc_moi - nuoc_cu)

    tien_dien = dien * gia_dien
    tien_nuoc = nuoc * gia_nuoc

    tong = gia_phong + tien_dien + tien_nuoc + wifi + rac

    du_lieu.append({
        "Phòng": i,
        "Điện cũ": dien_cu,
        "Điện mới": dien_moi,
        "Điện dùng": dien,
        "Tiền điện": tien_dien,
        "Nước cũ": nuoc_cu,
        "Nước mới": nuoc_moi,
        "Nước dùng": nuoc,
        "Tiền nước": tien_nuoc,
        "Phụ phí": wifi + rac,
        "Tổng tiền": tong
    })

st.divider()

st.header("📊 Bảng tổng hợp")

df = pd.DataFrame(du_lieu)

st.dataframe(df, use_container_width=True)

tong_doanh_thu = df["Tổng tiền"].sum()

st.metric(
    "💰 Tổng doanh thu",
    f"{tong_doanh_thu:,.0f} VNĐ"
)
