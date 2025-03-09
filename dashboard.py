import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

st.title('Brazilian ecommerce public Dashboard')
st.write('Welcome to Brazil\'s ecommerce public dahsboard from 2016 to 2018!')

###membuat helper function
def create_category_summary_df(df):
    category_summary_df = df.groupby(by=["product_category_name"]).agg({
        "order_id": "count",
        "price": "sum"
    }).reset_index()
    category_summary_df.rename(columns={
        "order_id": "order_count",
        "price": "total_revenue"
    }, inplace=True)
    return category_summary_df

def create_top_products_df(df):
    top_products_df = df.groupby("product_category_name").agg({
        "order_id": "count",
        "price": "sum"
    }).reset_index().rename(columns={
        "order_id": "total_orders", 
        "price": "total_pendapatan"
    })
    
    return top_products_df

def create_product_revenue_df(df):
    product_revenue_df = df.groupby("product_category_name")["price"].sum().reset_index()
    product_revenue_df.rename(columns={"price": "total_revenue"}, inplace=True)
    return product_revenue_df

def process_seller_reviews(all_df):
    seller_reviews = all_df.groupby("seller_id").agg({
        "order_id": "count",
        "price": "sum",
        "review_score": "mean"
    }).reset_index().rename(columns={
        "order_id": "total_orders",
        "price": "total_pendapatan",
        "review_score": "avg_review_score"
    })
    
    seller_reviews = seller_reviews.merge(
        all_df[["seller_id", "seller_city"]].drop_duplicates(),
        on="seller_id",
        how="left"
    )
    
    return seller_reviews.sort_values(by=["total_orders", "avg_review_score"], ascending=[False, False])

def create_city_sales_df(customers_df):
    city_sales_df = customers_df.groupby("customer_city")["customer_id"].count().reset_index()
    city_sales_df.rename(columns={"customer_id": "total_transactions"}, inplace=True)
    return city_sales_df

def preprocess_orders(all_df):
    """Mengonversi timestamp dan menghitung jumlah pesanan per bulan."""
    all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
    all_df["month_year"] = all_df["order_purchase_timestamp"].dt.to_period("M")
    order_trend = all_df.groupby("month_year")["order_id"].count().reset_index()
    order_trend["month_year"] = order_trend["month_year"].astype(str)
    return order_trend

#memanggil data
file_id = "1pg5bHTFNdO7EdkWePKhmln8M8glrZFqM"
url = f"https://drive.google.com/uc?id={file_id}"
all_df = pd.read_csv(url)

####Visualisasi Best & Worst Performing Product Categories
st.markdown("<h3 style='text-align: center;'>Best and Worst Performing Product Categories by Number of Sales</h3>", unsafe_allow_html=True)
translate = {
    "cama_mesa_banho": "Bed, Table, & Bath",
    "beleza_saude": "Beauty & Health",
    "esporte_lazer": "Sports & Leisure",
    "moveis_decoracao": "Furniture & Decoration",
    "informatica_acessorios": "Computers & Accessories",
    "cds_dvds_musicais": "Music CDs & DVDs",
    "la_cuisine": "Kitchen & Cooking",
    "pc_gamer": "Gaming PC",
    "fashion_roupa_infanto_juvenil": "Kids & Teen Fashion",
    "seguros_e_servicos": "Insurance & Services",
}

tertinggi_products = all_df['product_category_name'].value_counts().head(5).rename(index=translate)
terendah_products = all_df['product_category_name'].value_counts().tail(5).rename(index=translate)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#5865f2"] + ["#c6deff"] * 4

sns.barplot(x=tertinggi_products.values, y=tertinggi_products.index, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product Categories", loc="center", fontsize=60)
ax[0].tick_params(axis='y', labelsize=50)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(x=terendah_products.values, y=terendah_products.index, palette=colors[::-1], ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product Categories", loc="center", fontsize=60)
ax[1].tick_params(axis='y', labelsize=50)
ax[1].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

####Visualisasi Top 10 Product Categories by Revenue
st.markdown("<h3 style='text-align: left;'>Top 10 Product Categories by Revenue</h3>", unsafe_allow_html=True)
translate = {
    "beleza_saude": "Beauty & Health",
    "cama_mesa_banho": "Bed, Table & Bath",
    "relogios_presentes": "Watches & Gifts",
    "esporte_lazer": "Sports & Leisure",
    "informatica_acessorios": "Computers & Accessories",
    "moveis_decoracao": "Furniture & Decoration",
    "cool_stuff": "Cool Stuff",
    "utilidades_domesticas": "Home Utilities",
    "automotivo": "Automotive",
    "ferramentas_jardim": "Tools & Garden",
}

product_revenue_df = create_product_revenue_df(all_df)

#10 kategori dengan revenue tertinggi
tertinggi_product_revenue = product_revenue_df.nlargest(10, "total_revenue")
# Ganti label ke bahasa Inggris menggunakan `.replace()` berdasarkan`translate`
tertinggi_product_revenue["product_category_name"] = tertinggi_product_revenue["product_category_name"].replace(translate)

#Pie Chart
fig, ax = plt.subplots(figsize=(15,7))
colors = ["#5865f2"] + ["#c6deff"] * (len(tertinggi_product_revenue) - 1)
explode = [0.1] + [0] * (len(tertinggi_product_revenue) - 1)

ax.pie(
    tertinggi_product_revenue["total_revenue"],  # Pastikan hanya kolom angka yang dikirimkan
    labels=tertinggi_product_revenue["product_category_name"],  # Label harus berupa kategori produk
    autopct='%1.1f%%',
    colors=colors,
    startangle=120,
    wedgeprops={'edgecolor': 'black'},
    explode=explode
)

st.pyplot(fig)

#seller_reviews processing
seller_reviews = process_seller_reviews(all_df)
tertinggi_sellers = seller_reviews.head(5)
#Rata-rata review score per kota dari seller terbaik
tertinggi_cities_review = tertinggi_sellers.groupby("seller_city")["avg_review_score"].mean().sort_values(ascending=False)

###Visualisasi jumlah transaksi per kota
city_sales_df = create_city_sales_df(all_df)
tertinggi_cities = city_sales_df.sort_values(by="total_transactions", ascending=False).head(5)


st.markdown("<h3 style='text-align: left;'>Seller Demographics</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h5 style='text-align: center;'>Top 5 Cities with Best Seller Reviews</h5>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#5865f2"] + ["#c6deff"] * 4
    sns.barplot(x=tertinggi_cities_review.values, y=tertinggi_cities_review.index, palette=colors, ax=ax)
    ax.set_xlabel("Average Review Score", fontsize = 0)
    ax.set_ylabel("City", fontsize = 0)
    ax.set_title("Top 5 Cities with Best Seller Reviews", fontsize = 0)
    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=20)
    st.pyplot(fig)

with col2:
    st.markdown("<h5 style='text-align: center;'>Top 5 Cities with the Highest Number of Transactionss</h5>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=tertinggi_cities, x="total_transactions", y="customer_city", palette=["#5865f2"]*5, ax=ax)
    ax.set_title("5 Cities with the Highest Number of Transactions", fontsize=0)
    ax.set_xlabel("Total Transactions", fontsize=0)
    ax.set_ylabel("City", fontsize=0)
    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=20)
    ax.grid(False)
    st.pyplot(fig)

# Preprocessing data
order_trend = preprocess_orders(all_df)
####visualisasi tren pemesanan per bulan
st.markdown("<h3 style='text-align: left;'>Order Trend per Month</h3>", unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=order_trend, x="month_year", y="order_id", marker="o", color="#5865f2", linewidth=2.5)
ax.set_title("Order Trend per Month", fontsize=0, loc="center")
ax.set_xlabel("Month", fontsize=0)
ax.set_ylabel("Total Order", fontsize=0)
ax.tick_params(axis='x', rotation=45, labelsize=12)
ax.tick_params(axis='y', labelsize=15)
ax.grid(True, which='major', linestyle='--', linewidth=0.5, axis='y')
ax.grid(True, which='major', linestyle='--', linewidth=0.5, axis='x')

st.pyplot(fig)

#Konversi order_purchase_timestamp date ke datetime
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])

#perhitungan RFM
rfm_df = all_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": "max",      # Tanggal order terakhir
    "order_id": "nunique",    # Total order yang unik (Frequency)
    "price": "sum"      # Total revenue yang dihasilkan (Monetary)
})
rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]


orders_df = all_df.copy()
orders_df["order_purchase_timestamp"] = pd.to_datetime(orders_df["order_purchase_timestamp"])
recent_date = orders_df["order_purchase_timestamp"].max().date()

#recency
rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x.date()).days)

#kolom baru untuk customer_id yang lebih ringkas
rfm_df["customer_label"] = ["CUST" + str(i+1).zfill(3) for i in range(len(rfm_df))]
rfm_dashboard = rfm_df[["customer_label", "frequency", "monetary", "recency"]]

#buang kolom max_order_timestamp karena tidak dipakai
rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
rfm_df["customer_label"] = rfm_df["customer_label"].astype(str)

###visualisasi RFM ANALYSIS
st.markdown("<h3 style='text-align: left;'>Best Customer Based on RFM Parameters</h3>", unsafe_allow_html=True)
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 6))
colors = ["#5865f2"] * 5

#Recency
sns.barplot(y="recency", x="customer_label", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=45)
ax[0].tick_params(axis='x', labelsize=15)

#Frequency
sns.barplot(y="frequency", x="customer_label", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=45)
ax[1].tick_params(axis='x', labelsize=15)

#Monetary
sns.barplot(y="monetary", x="customer_label", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=45)
ax[2].tick_params(axis='x', labelsize=15)

plt.suptitle("Best Customer Based on RFM Parameters (customer_label)", fontsize=0)
st.pyplot(fig)

