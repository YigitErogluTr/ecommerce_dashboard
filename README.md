
# E‑Ticaret Çoklu Pazar Yeri Dashboardu (Dash)

Bu proje, Trendyol / Hepsiburada / Amazon / N11 gibi pazar yerlerinden gelen **satış, iade, stok, kârlılık ve bölgesel** metrikleri tek bir panelde toplamak için hazırlanmış **örnek bir Dash uygulamasıdır**.

## İçerik
```
ecommerce_dashboard/
├─ app.py
├─ data/
│  ├─ sales_data.csv
│  ├─ stock_snapshot.csv
│  └─ products.csv
├─ pages/
│  ├─ sales_dashboard.py
│  ├─ returns_dashboard.py
│  ├─ stock_dashboard.py
│  ├─ regional_dashboard.py
│  └─ finance_dashboard.py
├─ utils/
│  ├─ __init__.py
│  └─ data.py
└─ assets/
   └─ style.css
```

## Kurulum
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Notlar
- Veri **sentetik** olarak son 1 yıla göre üretilmiştir.
- Kargo maliyeti satır başına **birim** maliyettir (adetle çarpılır).
- Komisyon oranı pazar yerine göre değişen bir aralıktan rastgele atanmıştır.
- Stok sayfasındaki **gauge**, seçilen ürünün stok/reorder seviyesini gösterir; basit bir **run‑out tahmini** grafiği de bulunur.
