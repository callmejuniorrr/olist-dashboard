import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================
# Configuration
# ============================================
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    layout="wide"
)

st.markdown("""
<style>
    .stPlotlyChart {
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    iframe {
        border: none !important;
    }
    div[data-testid="metric-container"] {
        background-color: #F8F9FA;
        border: 1px solid #DEE2E6;
        border-radius: 8px;
        padding: 16px;
    }
    div[data-testid="metric-container"] label {
        color: #6C757D;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #212529;
        font-size: 22px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# Connexion DuckDB
# ============================================
@st.cache_resource
def get_conn():
    return duckdb.connect("/tmp/olist.duckdb") if not __import__("os").name == "nt" else duckdb.connect("olist.duckdb")

conn = get_conn()

# ============================================
# Sidebar — Filtres
# ============================================
st.sidebar.title("Filters")
st.sidebar.markdown("---")

date_range = conn.execute("""
    SELECT
        MIN(order_purchase_timestamp)::DATE AS min_date,
        MAX(order_purchase_timestamp)::DATE AS max_date
    FROM orders
""").df()

dataset_min = date_range["min_date"][0]
dataset_max = date_range["max_date"][0]

min_date, max_date = st.sidebar.date_input(
    "Date range",
    value=(dataset_min, dataset_max),
    min_value=dataset_min,
    max_value=dataset_max
)

st.sidebar.markdown("**Quick year filter**")
col_y1, col_y2, col_y3, col_y4 = st.sidebar.columns(4)
all_years = col_y1.button("All")
y2016 = col_y2.button("2016")
y2017 = col_y3.button("2017")
y2018 = col_y4.button("2018")

if y2016:
    min_date = pd.Timestamp("2016-01-01").date()
    max_date = pd.Timestamp("2016-12-31").date()
elif y2017:
    min_date = pd.Timestamp("2017-01-01").date()
    max_date = pd.Timestamp("2017-12-31").date()
elif y2018:
    min_date = pd.Timestamp("2018-01-01").date()
    max_date = pd.Timestamp("2018-12-31").date()
elif all_years:
    min_date = None
    max_date = None

st.sidebar.markdown("---")
st.sidebar.markdown("**Patrick Camy**")
st.sidebar.markdown("Data Analyst Student | Polytech Clermont-Ferrand")
st.sidebar.markdown("[GitHub](https://github.com/callmejuniorrr) | [LinkedIn](https://www.linkedin.com/in/patrick-c-5267b4265)")

# ============================================
# Filtre date dynamique
# ============================================
date_filter = ""
if min_date and max_date:
    date_filter = f"WHERE o.order_purchase_timestamp BETWEEN '{min_date}' AND '{max_date}'"

# ============================================
# Titre
# ============================================
st.title("Olist E-Commerce Dashboard")
if min_date and max_date:
    st.markdown(f"Showing data from **{min_date}** to **{max_date}**")
else:
    st.markdown("Showing **all data** — 2016 to 2018")
st.markdown("---")

# ============================================
# KPIs
# ============================================
df_orders = conn.execute(f"""
    SELECT COUNT(DISTINCT order_id) AS nb_orders
    FROM orders o
    {date_filter}
""").df()

df_ca = conn.execute(f"""
    SELECT ROUND(SUM(p.payment_value), 2) AS total_ca
    FROM order_payments p
    JOIN orders o ON o.order_id = p.order_id
    {date_filter}
""").df()

df_aov = conn.execute(f"""
    SELECT ROUND(SUM(p.payment_value) / COUNT(DISTINCT o.order_id), 2) AS panier_moyen
    FROM order_payments p
    JOIN orders o ON o.order_id = p.order_id
    {date_filter}
""").df()

df_sellers = conn.execute(f"""
    SELECT COUNT(DISTINCT oi.seller_id) AS nb_sellers
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    {date_filter}
""").df()

col1, col2, col3, col4 = st.columns([1.5, 2, 1.5, 1.5], gap="large")
col1.metric("Total Orders", f"{int(df_orders['nb_orders'][0]):,}")
col2.metric("Total Revenue", f"R$ {df_ca['total_ca'][0]:,}")
col3.metric("Average Basket", f"R$ {df_aov['panier_moyen'][0]}")
col4.metric("Active Sellers", f"{int(df_sellers['nb_sellers'][0]):,}")

st.markdown("---")

# ============================================
# Layout graphiques — template propre
# ============================================
LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=40, b=20),
    font=dict(family="sans-serif", size=13, color="#262730"),
)

# ============================================
# Graphique 1 — Evolution CA mensuel
# ============================================
st.subheader("Monthly Revenue Evolution")

df_monthly = conn.execute(f"""
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS mois,
        ROUND(SUM(p.payment_value), 2) AS ca
    FROM orders o
    JOIN order_payments p ON o.order_id = p.order_id
    {date_filter}
    GROUP BY mois
    ORDER BY mois
""").df()
df_monthly["mois"] = pd.to_datetime(df_monthly["mois"]).dt.strftime("%Y-%m")

fig1 = px.line(
    df_monthly,
    x='mois',
    y='ca',
    labels={'mois': 'Month', 'ca': 'Revenue (R$)'},
    color_discrete_sequence=['#1976D2']
)
fig1.update_traces(line_width=4)
fig1.update_layout(**LAYOUT, showlegend=False)
fig1.update_xaxes(showgrid=False)
fig1.update_yaxes(showgrid=True, gridcolor='#F0F0F0')
st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# ============================================
# Graphique 2 — Top états + paiements
# ============================================
col_g1, col_g2 = st.columns(2)

df_state = conn.execute(f"""
    SELECT
        c.customer_state,
        ROUND(SUM(p.payment_value), 2) AS ca
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_payments p ON o.order_id = p.order_id
    {date_filter}
    GROUP BY c.customer_state
    ORDER BY ca DESC
    LIMIT 10
""").df()

fig2 = px.bar(
    df_state,
    x='customer_state',
    y='ca',
    title='Top 10 States by Revenue',
    labels={'customer_state': 'State', 'ca': 'Revenue (R$)'},
    color='ca',
    color_continuous_scale='Blues'
)
fig2.update_layout(**LAYOUT, coloraxis_showscale=False)
fig2.update_xaxes(showgrid=False)
fig2.update_yaxes(showgrid=True, gridcolor='#F0F0F0')
col_g1.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

df_payment = conn.execute(f"""
    SELECT
        CASE
            WHEN payment_type = 'credit_card' THEN 'Credit Card'
            WHEN payment_type = 'debit_card' THEN 'Debit Card'
            WHEN payment_type = 'boleto' THEN 'Boleto'
            WHEN payment_type = 'voucher' THEN 'Voucher'
            ELSE 'Not defined'
        END AS payment_method,
        COUNT(*) AS nb_transactions
    FROM order_payments p
    JOIN orders o ON o.order_id = p.order_id
    {date_filter}
    GROUP BY payment_method
""").df()

names='payment_type'

fig3 = px.pie(
    df_payment,
    values='nb_transactions',
    names='payment_method',
    title='Payment Methods',
    color_discrete_sequence=px.colors.sequential.Blues_r,
    hole=0.4
)
fig3.update_layout(**LAYOUT)
col_g2.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# ============================================
# Graphique 3 — RFM
# ============================================
st.subheader("Seller RFM Segmentation")

rfm = conn.execute("""
    WITH rfm_brut AS (
        SELECT
            oi.seller_id,
            DATEDIFF('day',
                MAX(o.order_purchase_timestamp),
                (SELECT MAX(order_purchase_timestamp) FROM orders)
            ) AS recence,
            COUNT(oi.order_id) AS frequence,
            ROUND(SUM(p.payment_value), 2) AS montant
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN order_payments p ON oi.order_id = p.order_id
        GROUP BY oi.seller_id
    ),
    rfm_scores AS (
        SELECT
            seller_id, recence, frequence, montant,
            NTILE(5) OVER (ORDER BY recence DESC) AS r_score,
            NTILE(5) OVER (ORDER BY frequence DESC) AS f_score,
            NTILE(5) OVER (ORDER BY montant DESC) AS m_score
        FROM rfm_brut
    )
    SELECT
        seller_id, recence, frequence, montant,
        r_score, f_score, m_score,
        r_score + f_score + m_score AS rfm_total,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            ELSE 'Average'
        END AS segment
    FROM rfm_scores
    ORDER BY rfm_total DESC
""").df()

color_map = {
    'Champions': '#1565C0',
    'Loyal': '#1976D2',
    'New': '#42A5F5',
    'At Risk': '#EF5350',
    'Average': '#90A4AE'
}

col_rfm1, col_rfm2 = st.columns(2)

segments = rfm['segment'].value_counts().reset_index()
segments.columns = ['segment', 'count']

fig4 = px.pie(
    segments,
    values='count',
    names='segment',
    title='Seller Segments',
    color='segment',
    color_discrete_map=color_map,
    hole=0.4
)
fig4.update_layout(**LAYOUT)
col_rfm1.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

fig5 = px.scatter(
    rfm,
    x='frequence',
    y='montant',
    color='segment',
    color_discrete_map=color_map,
    hover_data=['seller_id', 'recence'],
    title='Frequency vs Revenue',
    labels={'frequence': 'Order Frequency', 'montant': 'Revenue (R$)'},
    size='montant',
    size_max=20
)
fig5.update_layout(**LAYOUT)
fig5.update_xaxes(showgrid=True, gridcolor='#F0F0F0')
fig5.update_yaxes(showgrid=True, gridcolor='#F0F0F0')
col_rfm2.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})

with st.expander("View RFM Data Table"):
    segment_filter = st.selectbox(
        "Filter by segment",
        options=['All'] + list(rfm['segment'].unique())
    )
    if segment_filter != 'All':
        st.dataframe(rfm[rfm['segment'] == segment_filter], use_container_width=True)
    else:
        st.dataframe(rfm, use_container_width=True)

st.markdown("---")

# ============================================
# Graphique 4 — Funnel
# ============================================
st.subheader("Order Conversion Funnel")

funnel = conn.execute(f"""
    WITH etapes AS (
        SELECT
            COUNT(DISTINCT o.order_id) AS nb_commandes,
            COUNT(DISTINCT CASE WHEN o.order_status != 'canceled'
                THEN o.order_id END) AS nb_approuvees,
            COUNT(DISTINCT CASE WHEN o.order_status = 'delivered'
                THEN o.order_id END) AS nb_livrees,
            COUNT(DISTINCT CASE WHEN p.payment_value > 0
                THEN o.order_id END) AS nb_payees
        FROM orders o
        LEFT JOIN order_payments p ON o.order_id = p.order_id
        {date_filter}
    )
    SELECT * FROM etapes
""").df()

col_f1, col_f2 = st.columns([2, 1])

fig6 = go.Figure(go.Funnel(
    y=['Orders Placed', 'Orders Approved', 'Orders Delivered', 'Orders Paid'],
    x=[
        funnel['nb_commandes'][0],
        funnel['nb_approuvees'][0],
        funnel['nb_livrees'][0],
        funnel['nb_payees'][0]
    ],
    textinfo='value+percent initial',
    marker=dict(
        color=['#1565C0', '#1976D2', '#42A5F5', '#90CAF9'],
        line=dict(width=1, color='white')
    )
))
fig6.update_layout(**LAYOUT, height=400)
col_f1.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})

total = funnel['nb_commandes'][0]
col_f2.markdown("### Conversion Rates")
col_f2.metric("Approval Rate",
    f"{round(funnel['nb_approuvees'][0] * 100 / total, 1)}%")
col_f2.metric("Delivery Rate",
    f"{round(funnel['nb_livrees'][0] * 100 / funnel['nb_approuvees'][0], 1)}%")
col_f2.metric("Payment Rate",
    f"{round(funnel['nb_payees'][0] * 100 / total, 1)}%")

st.markdown("---")

with st.expander("View Raw Monthly Data"):
    st.dataframe(df_monthly, use_container_width=True)
