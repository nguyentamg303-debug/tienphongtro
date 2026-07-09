import streamlit as st

st.set_page_config(
    page_title="Quản lý phòng trọ",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 HỆ THỐNG QUẢN LÝ PHÒNG TRỌ")

# ==========================
# Cấu hình bảng giá
# ==========================
st.sidebar.header("⚙️ Bảng giá")

gia_dien = st.sidebar.number_input("Giá điện (VNĐ/kWh)", value=3500)
gia_nuoc = st.sidebar.number_input("Giá nước (VNĐ/m³)", value=15000)
wifi = st.sidebar.number_input("Wifi", value=100000)
rac = st.sidebar.number_input("Rác", value=50000)

so_phong = st.number_input(
    "Số lượng phòng",
    min_value=1,
    value=10,
    step=1
)

ket_qua = []

st.header("Nhập dữ liệu")

for i in range(1, so_phong + 1):

    with st.expander(f"🏠 Phòng {i}"):

        gia_phong = st.number_input(
            "Giá phòng",
            value=2500000,
            key=f"gia{i}"
        )

        dien_cu = st.number_input(
            "Số điện cũ",
            value=0,
            key=f"dc{i}"
        )

        dien_moi = st.number_input(
            "Số điện mới",
            value=0,
            key=f"dm{i}"
        )

        nuoc_cu = st.number_input(
            "Số
