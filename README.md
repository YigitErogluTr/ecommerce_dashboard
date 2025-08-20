🛒 E-Commerce Multi-Marketplace Dashboard (Dash)

This project is a sample Dash application designed to consolidate metrics from multiple marketplaces such as Trendyol, Hepsiburada, Amazon, and N11 into a single interactive panel.
It visualizes sales, returns, stock, profitability, finance, and regional performance with filters and export options.

📂 Project Structure
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

📘 E-Commerce Dashboard User Guide
1. Getting Started

When you launch the application, the Login screen will appear.

Enter username and password to access the dashboard.

Upon successful login, you are automatically redirected to the Sales Performance page.

2. General Usage

Use the top navigation bar to switch between pages.

The “Print / PDF” button in the top right corner allows you to export the current page as a PDF report.

Each page includes filters (date range, marketplace, category, etc.) to customize the data view.

Graphs are interactive: hover over elements to see details.

3. Page Descriptions
🔑 Login

Enter your username and password.

✅ Successful login → redirects to the Sales Performance page.

❌ Wrong credentials → shows a red error alert.

📊 Sales Performance

This page shows overall sales performance.

How to use:

Select a date range.

Optionally filter by marketplace or category.

Switch between daily / weekly / monthly frequency.

Toggle between periodic totals or cumulative view.

Visuals & Metrics:

Total Sales (₺): Overall revenue in the selected period.

Total Quantity: Number of units sold.

Net Profit (₺): Profit after costs.

Return Rate (%): Percentage of returned items.

Marketplace Sales (Bar Chart): Compare revenue across platforms.

Category → Brand Ratio (Treemap): Visual share of revenue per category and brand.

Sales Over Time (Line Chart): Track revenue trends over time.

Top-Selling Products (Horizontal Bar): Displays top products with sales revenue and units sold.

🔄 Returns

Focuses on product returns.

Visuals & Metrics:

Total Returns: Number of returned items.

Return Rate (%): Percentage compared to sales.

Return Cost (₺): Financial cost of returned items.

Return Reasons (Pie Chart): Breakdown of why items were returned (e.g., defective, wrong item).

Marketplace Returns (Bar Chart): Which platform has the most returns.

📦 Stocks

Tracks inventory status and alerts for low stock.

Visuals & Metrics:

Total Stock: Current stock units.

Critical Stock Alerts: Items below reorder level.

Run-out Forecast: Estimated days until stock runs out.

Category Stock Distribution (Treemap): Share of stock per category.

Critical Stock List (Bar Chart): Items most at risk of running out.

💰 Profitability

Analyzes profitability by comparing sales and costs.

Visuals & Metrics:

Total Revenue

Total Cost

Net Profit

Profit Margin (%)

Category Profitability (Bar Chart): Profit per category.

Brand Profitability (Treemap): Contribution of brands to profit.

Profit Trend (Line Chart): Profit changes over time.

📑 Finance

Summarizes financial data including income and expenses.

Visuals & Metrics:

Income & Expenses Summary

Operational Costs (commissions, shipping, etc.)

Monthly Income vs Expense (Stacked Bar): Monthly overview.

Expense Breakdown (Pie Chart): Distribution of cost components.

🌍 Regional Sales

Analyzes sales geographically by region or city.

Visuals & Metrics:

City Sales (Bar Chart): Top cities by revenue.

Regional Heatmap: Density of sales across the country.

🗺️ Geographic Analysis

Visualizes sales at the coordinate level.

Visuals & Metrics:

Sales Points (Map): Each sale shown as a dot on the map.

Heatmap: High-demand areas highlighted visually.

4. Exporting Reports (PDF)

Click the “Print / PDF” button at the top right.

Your browser’s print dialog will appear.

Select “Save as PDF” as the destination.

The current page will be exported with clean formatting.

5. Example User Scenarios

Sales Manager → Reviews sales KPIs and trends in the Sales Performance page, exports PDF for reporting.

Finance Team → Uses Finance and Profitability pages to analyze costs and profit margins.

Operations Team → Tracks low stock alerts in the Stocks page.

Marketing Team → Uses Regional and Geographic pages for demand analysis.
