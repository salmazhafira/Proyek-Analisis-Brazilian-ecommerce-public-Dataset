# Brazilian E-commerce Public Dashboard

Dashboard ini dikembangkan menggunakan Streamlit untuk menampilkan analisis data e-commerce di Brazil.

## Cara Menjalankan Dashboard

### 1. Persyaratan

Pastikan Python dan pip sudah terinstal. Setelah itu, install dependensi yang dibutuhkan dengan perintah berikut:

```bash
pip install streamlit pandas matplotlib seaborn
```

### 2. Jalankan Dashboard

Jika menggunakan Conda, aktifkan environment terlebih dahulu:

```bash
conda activate main-ds
```

Gunakan perintah berikut untuk menjalankan dashboard:

```bash
streamlit run dashboard.py
```

Pastikan berada di direktori yang berisi file `dashboard.py` sebelum menjalankan perintah ini.

## Fitur Dashboard

- **Order Trend per Month**
- **Best and Worst Performing Product Categories by Number of Sales**
- **Top 10 Product Categories by Revenue**
- **Seller Demographics**
- **Top 5 Cities with Best Seller Reviews**
- **Top 5 Cities with the Highest Number of Transactions**
- **Best Customer Based on RFM Parameters**

## Struktur Proyek

```
📂 project-folder
├── 📄 dashboard.py  # File utama dashboard
├── 📄 README.md  # Panduan ini
├── 📄 all_data.csv  # Data utama
```
