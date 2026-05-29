# Olist E-Commerce Dashboard

Interactive analytics dashboard built with Streamlit, DuckDB and Plotly
on the Brazilian Olist e-commerce dataset (100k+ orders).

Live app : https://olist-dashboard-ex2np7xznr8zqeba6n2fgp.streamlit.app/

---

## Overview

This dashboard provides interactive business intelligence on the Olist
Brazilian e-commerce platform, covering revenue trends, state performance,
seller segmentation and order conversion analysis.

---

## Features

- Dynamic date filters and quick year selector
- 4 real-time KPIs : total orders, revenue, average basket, active sellers
- Monthly revenue evolution (area chart)
- Top 10 states by revenue with payment method breakdown
- Seller RFM segmentation : Champions, Loyal, New, At Risk, Average
- Order conversion funnel with conversion rates

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=flat&logo=duckdb&logoColor=black)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)

---

## Dataset

[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

- 100,000+ orders from 2016 to 2018
- 4 tables used : orders, customers, order_payments, order_items

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## SQL Analysis

The SQL queries behind this dashboard are available in a separate repository :
[sql-ecommerce-analysis](https://github.com/callmejuniorrr/sql-ecommerce-analysis)

---

## Author

**Patrick Camy**
Data Analyst Student | Polytech Clermont-Ferrand
3rd year — Mathematical Engineering & Data Science

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/patrick-c-5267b4265)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github)](https://github.com/callmejuniorrr)
