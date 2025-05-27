import streamlit as st
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns

# Thiết lập giao diện
st.set_page_config(page_title="Heart Disease Dashboard", layout="wide")
st.title("📊 Dashboard Dự đoán Bệnh Tim")

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["health_db"]
collection = db["heart_data"]

# Lấy dữ liệu từ MongoDB
df = pd.DataFrame(list(collection.find({}, {"_id": 0})))
if df.empty:
    st.warning("⚠️ Dữ liệu trống. Kiểm tra lại import MongoDB.")
    st.stop()

# Làm sạch tên cột
df.columns = [col.strip().lower() for col in df.columns]

# Sidebar - Bộ lọc
sex_filter = st.sidebar.selectbox("Giới tính", options=["Tất cả"] + sorted(df["sex"].unique().tolist()))
age_filter = st.sidebar.selectbox("Nhóm tuổi", options=["Tất cả"] + sorted(df["agecategory"].unique().tolist()))

# Áp dụng bộ lọc
filtered_df = df.copy()
if sex_filter != "Tất cả":
    filtered_df = filtered_df[filtered_df["sex"] == sex_filter]
if age_filter != "Tất cả":
    filtered_df = filtered_df[filtered_df["agecategory"] == age_filter]

# Bộ lọc hút thuốc
smoke_options = ["Tất cả"] + sorted(df["smoking"].dropna().unique().tolist())
smoking_filter = st.sidebar.selectbox("Hút thuốc", options=smoke_options)

# Bộ lọc BMI (chỉ số cơ thể)
min_bmi = float(df["bmi"].min())
max_bmi = float(df["bmi"].max())
bmi_filter = st.sidebar.slider("Chỉ số BMI", min_value=min_bmi, max_value=max_bmi, value=(min_bmi, max_bmi))

# Áp dụng bộ lọc
if smoking_filter != "Tất cả":
    filtered_df = filtered_df[filtered_df["smoking"] == smoking_filter]
filtered_df = filtered_df[(filtered_df["bmi"] >= bmi_filter[0]) & (filtered_df["bmi"] <= bmi_filter[1])]


# Thống kê tổng quát
col1, col2, col3 = st.columns(3)
col1.metric("Tổng số người", len(filtered_df))
col2.metric("Người bị bệnh tim", filtered_df["heartdisease"].value_counts().get("Yes", 0))
col3.metric("Tỷ lệ mắc bệnh", f"{(filtered_df['heartdisease'].value_counts(normalize=True).get('Yes', 0)*100):.2f}%")

st.markdown("---")

# Biểu đồ 1: HeartDisease theo giới tính
st.subheader("🧑‍🤝‍🧑 Biểu đồ 1: Phân bố bệnh tim theo giới tính")
fig1, ax1 = plt.subplots()
sns.countplot(data=filtered_df, x="sex", hue="heartdisease", palette="Set2", ax=ax1)
ax1.set_xlabel("Giới tính")
ax1.set_ylabel("Số lượng")
ax1.legend(title="Bệnh tim", labels=["Không", "Có"])
st.pyplot(fig1)

# Biểu đồ 2: Phân bố theo độ tuổi
st.subheader("🎂 Biểu đồ 2: Tỷ lệ bệnh tim theo nhóm tuổi")
fig2, ax2 = plt.subplots(figsize=(10, 4))
age_order = sorted(df["agecategory"].unique())  # Giữ thứ tự độ tuổi
sns.countplot(data=filtered_df, x="agecategory", hue="heartdisease", order=age_order, palette="coolwarm", ax=ax2)
ax2.set_xlabel("Nhóm tuổi")
ax2.set_ylabel("Số lượng")
ax2.legend(title="Bệnh tim", labels=["Không", "Có"])
plt.xticks(rotation=45)
st.pyplot(fig2)

# Biểu đồ 3: Tương quan BMI và bệnh tim
st.subheader("⚖️ Biểu đồ 3: Phân phối chỉ số BMI theo tình trạng bệnh tim")
fig3, ax3 = plt.subplots()
sns.histplot(data=filtered_df, x="bmi", hue="heartdisease", kde=True, palette="pastel", bins=30, ax=ax3)
ax3.set_xlabel("Chỉ số BMI")
ax3.set_ylabel("Số lượng")
ax3.legend(title="Bệnh tim", labels=["Không", "Có"])
st.pyplot(fig3)

# Biểu đồ 4: Tình trạng bệnh tiểu đường và bệnh tim
st.subheader("🩸 Biểu đồ 4: Tỷ lệ bệnh tim theo tình trạng tiểu đường")
fig4, ax4 = plt.subplots()
sns.countplot(data=filtered_df, x="diabetic", hue="heartdisease", palette="Set2", ax=ax4)
ax4.set_xlabel("Tình trạng Tiểu đường")
ax4.set_ylabel("Số lượng")
ax4.legend(title="Bệnh tim", labels=["Không", "Có"])
st.pyplot(fig4)

# Biểu đồ 5: Hút thuốc và bệnh tim
st.subheader("🚬 Biểu đồ 5: Tỷ lệ bệnh tim theo thói quen hút thuốc")
fig5, ax5 = plt.subplots()
sns.histplot(
    data=filtered_df,
    x="smoking",
    hue="heartdisease",
    multiple="fill",
    shrink=0.8,
    palette="pastel",
    ax=ax5
)
ax5.set_xlabel("Thói quen hút thuốc")
ax5.set_ylabel("Tỷ lệ (%)")
ax5.set_yticklabels(['{:.0%}'.format(x) for x in ax5.get_yticks()])
ax5.legend(title="Bệnh tim", labels=["Không", "Có"])
st.pyplot(fig5)

# Biểu đồ 6: Hoạt động thể chất và bệnh tim
st.subheader("🏃‍♂️ Biểu đồ 6: Tác động của hoạt động thể chất tới bệnh tim")
fig6, ax6 = plt.subplots()
sns.countplot(data=filtered_df, x="physicalactivity", hue="heartdisease", palette="coolwarm", ax=ax6)
ax6.set_xlabel("Hoạt động thể chất")
ax6.set_ylabel("Số lượng")
ax6.legend(title="Bệnh tim", labels=["Không", "Có"])
st.pyplot(fig6)
