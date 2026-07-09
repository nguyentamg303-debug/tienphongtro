import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Quản lý phòng trọ",
    page_icon="🏠",
    layout="wide"
)

@st.cache_resource
def get_conn():
    conn = sqlite3.connect("rental.db", check_same_thread=False)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS rooms(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room TEXT UNIQUE,
        tenant TEXT,
        phone TEXT,
        rent INTEGER,
        wifi INTEGER,
        trash INTEGER,
        status TEXT
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS meter(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT,
        room TEXT,
        old_electric INTEGER,
        new_electric INTEGER,
        old_water INTEGER,
        new_water INTEGER,
        electric_money INTEGER,
        water_money INTEGER,
        total INTEGER,
        paid INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    return conn

conn = get_conn()

st.title("🏠 HỆ THỐNG QUẢN LÝ PHÒNG TRỌ")

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Quản lý phòng",
        "Nhập chỉ số",
        "Hóa đơn"
    ]
)

ELECTRIC_PRICE = st.sidebar.number_input(
    "Giá điện",
    value=3500
)

WATER_PRICE = st.sidebar.number_input(
    "Giá nước",
    value=15000
)
# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":

    room_df = pd.read_sql("SELECT * FROM rooms", conn)
    meter_df = pd.read_sql("SELECT * FROM meter", conn)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Tổng phòng", len(room_df))

    with col2:
        if len(room_df) > 0:
            st.metric(
                "Đã thuê",
                len(room_df[room_df["status"] == "Đang thuê"])
            )
        else:
            st.metric("Đã thuê", 0)

    with col3:
        if len(room_df) > 0:
            st.metric(
                "Phòng trống",
                len(room_df[room_df["status"] == "Trống"])
            )
        else:
            st.metric("Phòng trống", 0)

    with col4:
        if len(meter_df):
            st.metric(
                "Doanh thu",
                f"{meter_df['total'].sum():,.0f} VNĐ"
            )
        else:
            st.metric(
                "Doanh thu",
                "0 VNĐ"
            )

    st.divider()

    st.subheader("Danh sách phòng")

    st.dataframe(
        room_df,
        use_container_width=True
    )

# =========================
# QUẢN LÝ PHÒNG
# =========================
elif menu == "Quản lý phòng":

    st.subheader("Thêm phòng")

    c1, c2 = st.columns(2)

    with c1:

        room = st.text_input("Tên phòng")

        tenant = st.text_input("Người thuê")

        phone = st.text_input("Số điện thoại")

        rent = st.number_input(
            "Giá phòng",
            value=2500000
        )

    with c2:

        wifi = st.number_input(
            "Wifi",
            value=100000
        )

        trash = st.number_input(
            "Rác",
            value=50000
        )

        status = st.selectbox(
            "Trạng thái",
            [
                "Đang thuê",
                "Trống"
            ]
        )

    if st.button("Lưu phòng"):

        conn.execute("""
        INSERT INTO rooms(
            room,
            tenant,
            phone,
            rent,
            wifi,
            trash,
            status
        )
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            room,
            tenant,
            phone,
            rent,
            wifi,
            trash,
            status
        ))

        conn.commit()

        st.success("Đã thêm phòng.")

    st.divider()

    df = pd.read_sql(
        "SELECT * FROM rooms",
        conn
    )

    st.dataframe(
        df,
        use_container_width=True
                 )# =========================
# NHẬP CHỈ SỐ
# =========================
elif menu == "Nhập chỉ số":

    st.subheader("Nhập chỉ số tháng")

    month = st.text_input(
        "Tháng",
        value=datetime.now().strftime("%m/%Y")
    )

    rooms = pd.read_sql(
        "SELECT * FROM rooms WHERE status='Đang thuê'",
        conn
    )

    if len(rooms) == 0:
        st.warning("Chưa có phòng đang thuê.")
        st.stop()

    for _, r in rooms.iterrows():

        room = r["room"]

        st.divider()
        st.markdown(f"### 🏠 {room}")

        last = conn.execute("""
            SELECT new_electric,new_water
            FROM meter
            WHERE room=?
            ORDER BY id DESC
            LIMIT 1
        """,(room,)).fetchone()

        if last:
            old_electric = last[0]
            old_water = last[1]
        else:
            old_electric = 0
            old_water = 0

        c1,c2 = st.columns(2)

        with c1:
            st.number_input(
                "Điện cũ",
                value=old_electric,
                disabled=True,
                key=f"oldE{room}"
            )

            new_electric = st.number_input(
                "Điện mới",
                min_value=old_electric,
                value=old_electric,
                key=f"newE{room}"
            )

        with c2:
            st.number_input(
                "Nước cũ",
                value=old_water,
                disabled=True,
                key=f"oldW{room}"
            )

            new_water = st.number_input(
                "Nước mới",
                min_value=old_water,
                value=old_water,
                key=f"newW{room}"
            )

        electric_use = new_electric-old_electric
        water_use = new_water-old_water

        electric_money = electric_use*ELECTRIC_PRICE
        water_money = water_use*WATER_PRICE

        total = (
            r["rent"]+
            electric_money+
            water_money+
            r["wifi"]+
            r["trash"]
        )

        st.info(
            f"Điện: {electric_use} kWh | "
            f"Nước: {water_use} m³ | "
            f"Tổng: {total:,.0f} VNĐ"
        )

        if st.button(
            f"Lưu {room}",
            key=f"save{room}"
        ):

            conn.execute("""
            INSERT INTO meter(
                month,
                room,
                old_electric,
                new_electric,
                old_water,
                new_water,
                electric_money,
                water_money,
                total
            )
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                month,
                room,
                old_electric,
                new_electric,
                old_water,
                new_water,
                electric_money,
                water_money,
                total
            ))

            conn.commit()

            st.success(f"Đã lưu {room}")# =========================
# HÓA ĐƠN
# =========================
elif menu == "Hóa đơn":

    st.subheader("📄 Hóa đơn tháng")

    month = st.text_input(
        "Tháng cần xem",
        value=datetime.now().strftime("%m/%Y"),
        key="invoice_month"
    )

    df = pd.read_sql(
        """
        SELECT
            room,
            old_electric,
            new_electric,
            electric_money,
            old_water,
            new_water,
            water_money,
            total,
            paid
        FROM meter
        WHERE month=?
        ORDER BY room
        """,
        conn,
        params=(month,)
    )

    if len(df)==0:
        st.info("Chưa có dữ liệu.")
        st.stop()

    st.dataframe(
        df,
        use_container_width=True
    )

    st.divider()

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        st.metric(
            "Số phòng",
            len(df)
        )

    with col2:
        st.metric(
            "Doanh thu",
            f"{df['total'].sum():,.0f} VNĐ"
        )

    with col3:
        st.metric(
            "Đã thanh toán",
            len(df[df["paid"]==1])
        )

    with col4:
        st.metric(
            "Chưa thanh toán",
            len(df[df["paid"]==0])
        )

    st.divider()

    st.subheader("Đánh dấu thanh toán")

    room = st.selectbox(
        "Chọn phòng",
        df["room"]
    )

    if st.button("Đã thanh toán"):

        conn.execute(
            """
            UPDATE meter
            SET paid=1
            WHERE month=? AND room=?
            """,
            (month,room)
        )

        conn.commit()

        st.success("Đã cập nhật.")

    st.divider()

    st.subheader("📱 Tin nhắn")

    row = df[df["room"]==room].iloc[0]

    message = f"""
🏠 PHÒNG {room}

Điện:
{row['old_electric']} → {row['new_electric']}
Tiền điện: {row['electric_money']:,.0f}đ

Nước:
{row['old_water']} → {row['new_water']}
Tiền nước: {row['water_money']:,.0f}đ

💰 Tổng thanh toán:
{row['total']:,.0f}đ

Vui lòng chuyển khoản đúng hạn.
Xin cảm ơn!
"""

    st.text_area(
        "Copy gửi Zalo",
        value=message,
        height=220
    )

    st.divider()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "📥 Xuất Excel (CSV)",
        csv,
        file_name=f"HoaDon_{month}.csv",
        mime="text/csv"
  )# =========================
# LỊCH SỬ & SAO LƯU
# =========================

elif menu == "Lịch sử":

    st.subheader("📜 Lịch sử hóa đơn")

    months = pd.read_sql(
        "SELECT DISTINCT month FROM meter ORDER BY month DESC",
        conn
    )

    if len(months) == 0:
        st.info("Chưa có dữ liệu.")
        st.stop()

    selected = st.selectbox(
        "Chọn tháng",
        months["month"]
    )

    history = pd.read_sql(
        """
        SELECT *
        FROM meter
        WHERE month=?
        ORDER BY room
        """,
        conn,
        params=(selected,)
    )

    st.dataframe(
        history,
        use_container_width=True
    )

    st.metric(
        "Tổng doanh thu",
        f"{history['total'].sum():,.0f} VNĐ"
    )

    csv = history.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 Xuất CSV",
        csv,
        file_name=f"LichSu_{selected}.csv",
        mime="text/csv"
    )

# =========================
# SAO LƯU DATABASE
# =========================

elif menu == "Sao lưu":

    st.subheader("💾 Sao lưu dữ liệu")

    with open("rental.db","rb") as f:

        st.download_button(
            "Tải database",
            data=f,
            file_name="rental.db",
            mime="application/octet-stream"
        )

    st.success("Nên sao lưu dữ liệu mỗi tháng.")

# =========================
# XÓA PHÒNG
# =========================

elif menu == "Xóa phòng":

    rooms = pd.read_sql(
        "SELECT room FROM rooms",
        conn
    )

    room = st.selectbox(
        "Chọn phòng",
        rooms["room"]
    )

    if st.button("🗑️ Xóa"):

        conn.execute(
            "DELETE FROM rooms WHERE room=?",
            (room,)
        )

        conn.commit()

        st.success("Đã xóa phòng.")

# --- 1. PHẦN MENU (Đặt ở trên cùng, ngoài các khối if) ---
st.sidebar.title("📋 Điều hướng")
menu = st.sidebar.radio(
    "Menu", 
    ["Dashboard", "Quản lý phòng", "Nhập chỉ số", "Hóa đơn", "Lịch sử", "Sao lưu", "Cài đặt"]
)

# --- 1. CÁC HÀM XỬ LÝ (Đặt tách biệt) ---
@st.cache_data(ttl=60)
def load_rooms():
    return pd.read_sql("SELECT * FROM rooms", conn)

@st.cache_data(ttl=60)
def load_meter():
    return pd.read_sql("SELECT * FROM meter", conn)

# --- 2. XỬ LÝ LOGIC CHÍNH ---
# Nên load dữ liệu trước khi dùng
rooms_df = load_rooms()

# --- 3. PHẦN NỘI DUNG (Sử dụng các khối if/elif) ---

if menu == "Cài đặt":
    st.subheader("⚙️ Cấu hình")
    st.info("""
        Giá điện, nước được thay đổi ở Sidebar.
        Dữ liệu lưu trong SQLite.
        Chương trình tự ghi nhớ số điện và nước tháng trước.
    """)

elif menu == "Nhập chỉ số":
    st.subheader("📝 Nhập chỉ số điện nước")
    room_input = st.text_input("Nhập số phòng cần kiểm tra:")
    
    if room_input:
        # Thực hiện truy vấn để tìm phòng
        exist = conn.execute("SELECT room FROM rooms WHERE room=?", (room_input,)).fetchone()
        
        # Bây giờ 'exist' đã được định nghĩa, an toàn để kiểm tra
        if exist:
            st.success(f"Phòng {room_input} đã tồn tại trong hệ thống.")
            # Thực hiện các logic nhập chỉ số tại đây...
        else:
            st.warning("Không tìm thấy phòng này trong cơ sở dữ liệu.")
    else:
        st.info("Vui lòng nhập số phòng để bắt đầu.")

# Nếu menu khác, bạn tiếp tục với các elif tiếp theo...
# ... các phần menu khác ...
elif menu == "Nhập chỉ số":
    st.subheader("📝 Nhập chỉ số điện nước")
    room_input = st.text_input("Nhập số phòng:")
    
    if room_input:
        # Truy vấn trực tiếp tại đây
        exist = conn.execute("SELECT room FROM rooms WHERE room=?", (room_input,)).fetchone()
        
        # Kiểm tra ngay sau khi truy vấn
        if exist:
            st.success(f"Phòng {room_input} tồn tại.")
            # ... xử lý tiếp theo ...
        else:
            st.warning("Phòng này không tồn tại.")
    else:
        st.info("Vui lòng nhập số phòng.")
# --- 1. PHẦN ĐỊNH NGHĨA HÀM (Luôn đặt trên cùng) ---
def export_excel(df):
    wb = Workbook()
    ws = wb.active
    ws.title = "HoaDon"
    ws.append(list(df.columns))
    for row in df.values.tolist():
        ws.append(row)
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# --- 2. PHẦN HIỂN THỊ DỮ LIỆU ---
st.plotly_chart(fig)
if total > 0:
    st.toast(f"Đã tính tiền {room}")
# Hiển thị VietQR
bank, account = "970422", "0123456789"
vietqr = f"https://img.vietqr.io/image/{bank}-{account}-compact.png?amount={total}&addInfo={room}"
st.image(vietqr, width=250)
# Hiển thị số liệu thống kê
st.metric("Tổng doanh thu", f"{meter_df['total'].sum():,.0f} VNĐ")
st.metric("Đã thu", f"{meter_df[meter_df.paid==1]['total'].sum():,.0f}")
st.metric("Chưa thu", f"{meter_df[meter_df.paid==0]['total'].sum():,.0f}")

# --- 3. CÁC TÁC VỤ (Xuất file, tin nhắn, tìm kiếm) ---
excel_data = export_excel(df)
st.download_button(
    "📥 Xuất Excel",
    data=excel_data,
    file_name=f"HoaDon_{month}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

messages = [f"🏠 {row['room']}\nTổng tiền: {row['total']:,.0f}đ" for _, row in df.iterrows()]
st.text_area("Tin nhắn tổng hợp", "\n\n".join(messages), height=300)

keyword = st.text_input("🔍 Tìm phòng")
df_display = df[df["room"].str.contains(keyword, case=False)] if keyword else df
st.dataframe(df_display, use_container_width=True)

# --- 4. PHẦN CẬP NHẬT DỮ LIỆU ---
st.subheader("⚙️ Quản lý và Cấu hình")
room_select = st.selectbox("Chọn phòng", rooms["room"])
new_name = st.text_input("Người thuê")
new_phone = st.text_input("SĐT")

if st.button("Cập nhật"):
    conn.execute("UPDATE rooms SET tenant=?, phone=? WHERE room=?", (new_name, new_phone, room_select))
    conn.commit()
    st.success("Đã cập nhật.")

st.divider()
month_select = st.selectbox("Tháng", months["month"])
if st.button("Xóa dữ liệu tháng"):
    conn.execute("DELETE FROM meter WHERE month=?", (month_select,))
    conn.commit()
    st.success("Đã xóa.")

st.divider()
st.caption("🏠 Hệ thống quản lý phòng trọ - Streamlit Edition")
