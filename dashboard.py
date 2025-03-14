import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


st.title('Brazilian e-Commerce Public Dashboard')
st.write('Welcome to Brazil\'s e-commerce public dahsboard from 2016 to 2018!')


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

def create_monthly_trend_df(df):
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['year_month'] = df['order_purchase_timestamp'].dt.to_period('M')
    monthly_trend_df = df.groupby('year_month').agg({'order_id': 'count'}).reset_index()
    monthly_trend_df.rename(columns={"order_id": "total_orders"}, inplace=True)
    return monthly_trend_df

def create_product_revenue_df(df):
    revenue_df = df.groupby("product_category_name").agg({"price": "sum"}).reset_index()
    revenue_df.rename(columns={"price": "total_revenue"}, inplace=True)
    return revenue_df

#memanggil data
file_id = "1pg5bHTFNdO7EdkWePKhmln8M8glrZFqM"
url = f"https://drive.google.com/uc?id={file_id}"
all_df = pd.read_csv(url)

#filtering kota
st.sidebar.image("https://i.imgur.com/7BkWydt.png", use_container_width=True)
st.sidebar.markdown("<h3 style='text-align: center;'>Brazil City</h3>", unsafe_allow_html=True)
city_sales_df = all_df.groupby("customer_city").agg({"customer_id": "count"}).reset_index()
city_sales_df.rename(columns={"customer_id": "total_transactions"}, inplace=True)
selected_city = st.sidebar.selectbox("Select a City:", ["All"] + city_sales_df["customer_city"].unique().tolist())

#data berdasarkan filter kota
if selected_city != "All":
    filtered_df = all_df[all_df["customer_city"] == selected_city]
else:
    filtered_df = all_df


####Visualisasi Best & Worst Performing Product Categories
st.markdown("<h3 style='text-align: center;'>Best and Worst Performing Product Categories by Number of Sales</h3>", unsafe_allow_html=True)
translate = {
    "beleza_saude": "Beauty & Health",
    "informatica_acessorios": "Computers & Accessories",
    "automotivo": "Automotive",
    "cama_mesa_banho": "Bed, Table, & Bath",
    "moveis_decoracao": "Furniture & Decoration",
    "esporte_lazer": "Sports & Leisure",
    "perfumaria": "Perfumery",
    "utilidades_domesticas": "Home Utilities",
    "telefonia": "Telephony",
    "relogios_presentes": "Watches & Gifts",
    "alimentos_bebidas": "Food & Beverages",
    "bebes": "Babies",
    "papelaria": "Stationery",
    "tablets_impressao_imagem": "Tablets, Printing & Imaging",
    "brinquedos": "Toys",
    "telefonia_fixa": "Fixed Telephony",
    "ferramentas_jardim": "Tools & Gardening",
    "fashion_bolsas_e_acessorios": "Fashion Bags & Accessories",
    "eletroportateis": "Portable Electronics",
    "consoles_games": "Consoles & Games",
    "audio": "Audio",
    "fashion_calcados": "Fashion Shoes",
    "cool_stuff": "Cool Stuff",
    "malas_acessorios": "Luggage & Accessories",
    "climatizacao": "Air Conditioning & Climate Control",
    "construcao_ferramentas_construcao": "Construction Tools",
    "moveis_cozinha_area_de_servico_jantar_e_jardim": "Kitchen, Laundry, Dining & Garden Furniture",
    "construcao_ferramentas_jardim": "Construction & Garden Tools",
    "fashion_roupa_masculina": "Men's Fashion",
    "pet_shop": "Pet Shop",
    "moveis_escritorio": "Office Furniture",
    "market_place": "Marketplace",
    "eletronicos": "Electronics",
    "eletrodomesticos": "Home Appliances",
    "artigos_de_festas": "Party Supplies",
    "casa_conforto": "Home Comfort",
    "construcao_ferramentas_ferramentas": "Construction & Tools",
    "agro_industria_e_comercio": "Agriculture, Industry & Commerce",
    "moveis_colchao_e_estofado": "Mattresses & Upholstered Furniture",
    "livros_tecnicos": "Technical Books",
    "casa_construcao": "Home & Construction",
    "instrumentos_musicais": "Musical Instruments",
    "moveis_sala": "Living Room Furniture",
    "construcao_ferramentas_iluminacao": "Construction & Lighting Tools",
    "industria_comercio_e_negocios": "Industry, Commerce & Business",
    "alimentos": "Food",
    "artes": "Arts",
    "moveis_quarto": "Bedroom Furniture",
    "livros_interesse_geral": "General Interest Books",
    "construcao_ferramentas_seguranca": "Construction & Safety Tools",
    "fashion_underwear_e_moda_praia": "Underwear & Beachwear",
    "fashion_esporte": "Sports Fashion",
    "sinalizacao_e_seguranca": "Signage & Safety",
    "pcs": "PCs",
    "artigos_de_natal": "Christmas Items",
    "fashion_roupa_feminina": "Women's Fashion",
    "eletrodomesticos_2": "Home Appliances 2",
    "livros_importados": "Imported Books",
    "bebidas": "Drinks",
    "cine_foto": "Cinema & Photography",
    "la_cuisine": "Kitchen & Cooking",
    "musica": "Music",
    "casa_conforto_2": "Home Comfort 2",
    "portateis_casa_forno_e_cafe": "Portable Home, Oven & Coffee",
    "cds_dvds_musicais": "Music CDs & DVDs",
    "dvds_blu_ray": "DVDs & Blu-ray",
    "flores": "Flowers",
    "artes_e_artesanato": "Arts & Crafts",
    "fraldas_higiene": "Diapers & Hygiene",
    "fashion_roupa_infanto_juvenil": "Kids & Teen Fashion",
    "seguros_e_servicos": "Insurance & Services"
}

#kategori produk dengan jumlah penjualan tertinggi dan terendah
tertinggi_products = filtered_df['product_category_name'].value_counts().head(5).rename(index=translate)
terendah_products = filtered_df['product_category_name'].value_counts().tail(5).rename(index=translate)

#visualisasi
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#5865f2"] + ["#c6deff"] * 4

#performa terbaik
sns.barplot(x=tertinggi_products.values, y=tertinggi_products.index, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product Categories", loc="center", fontsize=60)
ax[0].tick_params(axis='y', labelsize=50)
ax[0].tick_params(axis='x', labelsize=35)

#performa terendah
sns.barplot(x=terendah_products.values, y=terendah_products.index, palette=colors[::-1], ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product Categories", loc="center", fontsize=60)
ax[1].tick_params(axis='y', labelsize=50)
ax[1].tick_params(axis='x', labelsize=35)

#plot di Streamlit
st.pyplot(fig)

####Visualisasi Top Product Categories by Revenue
st.markdown("<h3 style='text-align: left;'>Top Product Categories by Revenue</h3>", unsafe_allow_html=True)

product_revenue_df = create_product_revenue_df(filtered_df)

#kategori dengan revenue tertinggi
tertinggi_product_revenue = product_revenue_df.nlargest(10, "total_revenue")
tertinggi_product_revenue["product_category_name"] = tertinggi_product_revenue["product_category_name"].replace(translate)

#Pie Chart
fig, ax = plt.subplots(figsize=(15,7))
colors = ["#5865f2"] + ["#c6deff"] * (len(tertinggi_product_revenue) - 1)
explode = [0.1] + [0] * (len(tertinggi_product_revenue) - 1)

ax.pie(
    tertinggi_product_revenue["total_revenue"],
    labels=tertinggi_product_revenue["product_category_name"],
    autopct='%1.1f%%',
    colors=colors,
    startangle=120,
    wedgeprops={'edgecolor': 'black'},
    explode=explode
)

st.pyplot(fig)

#seller_reviews processing
seller_reviews = process_seller_reviews(filtered_df)
tertinggi_sellers = seller_reviews.head(5)

#Rata-rata review score per kota dari seller terbaik
tertinggi_cities_review = tertinggi_sellers.groupby("seller_city")["avg_review_score"].mean().sort_values(ascending=False)

#Visualisasi jumlah transaksi per kota
city_sales_filtered = create_city_sales_df(filtered_df)
tertinggi_cities = city_sales_filtered.sort_values(by="total_transactions", ascending=False).head(5)

st.markdown("<h3 style='text-align: left;'>Seller Demographics</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h5 style='text-align: center;'>Top Cities with Best Seller Reviews</h5>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#5865f2"] + ["#c6deff"] * 4
    sns.barplot(x=tertinggi_cities_review.values, y=tertinggi_cities_review.index, palette=colors, ax=ax)
    ax.set_xlabel("Average Review Score", fontsize=12)
    ax.set_ylabel("City", fontsize=12)
    ax.set_title("Top 5 Cities with Best Seller Reviews", fontsize=14)
    ax.tick_params(axis='x', labelsize=10)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

with col2:
    st.markdown("<h5 style='text-align: center;'>Top Cities with the Highest Number of Transactions</h5>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=tertinggi_cities, x="total_transactions", y="customer_city", palette=["#5865f2"]*5, ax=ax)
    ax.set_title("5 Cities with the Highest Number of Transactions", fontsize=14)
    ax.set_xlabel("Total Transactions", fontsize=12)
    ax.set_ylabel("City", fontsize=12)
    ax.tick_params(axis='x', labelsize=10)
    ax.tick_params(axis='y', labelsize=12)
    ax.grid(False)
    st.pyplot(fig)
    
#preprocessing data setelah filtering
order_trend = preprocess_orders(filtered_df)

###Visualisasi tren pemesanan per bulan
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

#perhitungan RFM setelah filtering
rfm_df = filtered_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": "max",      # Tanggal order terakhir
    "order_id": "nunique",    # Total order yang unik (Frequency)
    "price": "sum"      # Total revenue yang dihasilkan (Monetary)
})
rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

orders_df = filtered_df.copy()
orders_df["order_purchase_timestamp"] = pd.to_datetime(orders_df["order_purchase_timestamp"])
recent_date = orders_df["order_purchase_timestamp"].max().date()

#Recency
rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x.date()).days)

#kolom baru untuk customer_id yang lebih ringkas
rfm_df["customer_label"] = ["CUST" + str(i+1).zfill(3) for i in range(len(rfm_df))]
rfm_dashboard = rfm_df[["customer_label", "frequency", "monetary", "recency"]]

#buang kolom max_order_timestamp karena tidak dipakai
rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
rfm_df["customer_label"] = rfm_df["customer_label"].astype(str)

#visualisasi 
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

plt.suptitle("Best Customer Based on RFM Parameters", fontsize=0)
st.pyplot(fig)
