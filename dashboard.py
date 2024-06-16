import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from collections import defaultdict
from sqlalchemy import create_engine

# def create_connection():
#     connection = mysql.connector.connect(
#         host='kubela.id',
#         port=3306,
#         user='davis2024irwan',
#         password='wh451n9m@ch1n3',
#         database='aw'
#     )
#     return connection

# Konfigurasi koneksi untuk SQLAlchemy
# db_username = 'davis2024irwan'
# db_password = 'wh451n9m@ch1n3'
# db_host = 'kubela.id'
# db_name = 'aw'

# def create_connection():
#     connection = mysql.connector.connect(
#         host='localhost',  # Ubah ke 'localhost'
#         port=3306,  # Tetap port 3306
#         user='root',  # Sesuaikan dengan user lokal Anda
#         password='',  # Sesuaikan dengan password lokal Anda
#         database='dw_aw'  # Nama database lokal Anda
#     )
#     return connection

# Konfigurasi koneksi untuk SQLAlchemy
db_username = 'root'
db_password = ''
db_host = 'localhost'
db_name = 'dw_aw'

# Membuat URL koneksi menggunakan SQLAlchemy
connection_string = f'mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}'
engine = create_engine(connection_string)

# Sidebar
with st.sidebar:
    st.title('Final Project Data Visualisasi 2024')
    st.write('Select the data below to see the visualization. This data visualization project consists of 2 data, Adventure Work and IMDb Most Popular Film Data.')
    db_choice = st.selectbox("Select Database :", ["Database AW", "Database Scraping IMDb"])

# DATABASE AW
if db_choice == "Database AW":
    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <img src="{"https://dcassetcdn.com/design_img/2623047/545341/545341_14124078_2623047_9f9971b7_image.png"}" width="200">
        </div>
    """, unsafe_allow_html=True)
    
    # SECTION SALES DAN ORDER
    st.header('Sales and Order')
    # Pesanan Antar Wilayah dari Waktu ke Waktu (line chart)
    # SQL query to retrieve sales data over time by region
    query = """
    SELECT 
        t.CalendarYear AS Years,
        g.EnglishCountryRegionName AS Region,
        SUM(fs.OrderQuantity) AS TotalOrder
    FROM 
        factinternetsales fs
    JOIN 
        dimcustomer c ON fs.CustomerKey = c.CustomerKey
    JOIN 
        dimgeography g ON c.GeographyKey = g.GeographyKey
    JOIN 
        dimtime t ON fs.OrderDateKey = t.TimeKey
    GROUP BY 
        t.CalendarYear, g.EnglishCountryRegionName
    ORDER BY 
        t.CalendarYear, TotalOrder DESC;
    """
    data_aw = pd.read_sql(query, engine)
    data_aw['Years'] = data_aw['Years'].astype(str)
    chart = alt.Chart(data_aw).mark_line(point=True).encode(
        x='Years:O',
        y='TotalOrder:Q',
        color='Region:N',
        tooltip=['Years', 'Region', 'TotalOrder']
    ).properties(
        title='Comparison of Orders Regions by Year',
        width=800,
        height=400
    ).configure_title(
        fontSize=20,
        # anchor='middle'
    )
    st.altair_chart(chart, use_container_width=True)

    # Tren jumlah penjualan tiap tahun
    query = """
    SELECT 
        t.CalendarYear AS Years, 
        COUNT(sf.OrderQuantity) AS 'Order Count'
    FROM  
        dw_aw.factinternetsales sf
    JOIN 
        dw_aw.dimtime t ON sf.OrderDateKey = t.TimeKey
    GROUP BY 
        t.CalendarYear
    ORDER BY 
        t.CalendarYear;
    """
    data = pd.read_sql(query, engine)
    data['Years'] = data['Years'].astype(str)
    line_chart = alt.Chart(data).mark_line().encode(
        x='Years',
        y='Order Count',
        tooltip=['Years', 'Order Count']
    ).properties(
        title='Trend of Order Count by Years',
        width=600,
        height=400
    ).configure_title(
        fontSize=20,
        # anchor='middle'
    )
    st.altair_chart(line_chart, use_container_width=True)

    # Perbandingan pendapatan berdasarkan kategori barang
    query = """
    SELECT 
        pc.EnglishProductCategoryName AS ProductCategory,
        SUM(fs.SalesAmount) AS TotalSales
    FROM 
        dimproduct p
    JOIN 
        dimproductsubcategory ps ON p.ProductSubcategoryKey = ps.ProductSubcategoryKey
    JOIN 
        dimproductcategory pc ON ps.ProductCategoryKey = pc.ProductCategoryKey
    JOIN 
        factinternetsales fs ON p.ProductKey = fs.ProductKey
    GROUP BY 
        pc.EnglishProductCategoryName
    ORDER BY 
        TotalSales DESC;
    """
    data_aw = pd.read_sql(query, engine)
    bar_chart = alt.Chart(data_aw).mark_bar().encode(
        x=alt.X('ProductCategory', sort='-y', title='Product Category'),
        y=alt.Y('TotalSales', title='Total Sales Amount'),
        tooltip=['ProductCategory', 'TotalSales']
    ).properties(
        title='Comparison of Revenue by Product Categories',
        width=800,
        height=400
    ).configure_axisX(
        labelAngle=45
    ).configure_title(
        fontSize=20,
        # anchor='middle'
    )
    st.altair_chart(bar_chart, use_container_width=True)

    # Perbandingan pendapatan di seluruh wilayah
    query = """
    SELECT 
        st.SalesTerritoryRegion AS SalesTerritory,
        st.SalesTerritoryCountry AS Country,
        SUM(fs.SalesAmount) AS TotalSales
    FROM 
        dimsalesterritory st
    JOIN 
        factinternetsales fs ON st.SalesTerritoryKey = fs.SalesTerritoryKey
    GROUP BY 
        st.SalesTerritoryRegion, st.SalesTerritoryCountry
    ORDER BY 
        TotalSales DESC;
    """
    data_aw = pd.read_sql(query, engine)
    fig = px.choropleth(
        data_aw,
        locations="Country",
        locationmode="country names",
        color="TotalSales",
        hover_name="SalesTerritory",
        color_continuous_scale=px.colors.sequential.Plasma
    )
    fig.update_layout(
        title_text='Revenue by Sales Region',
        title_font_size=20
    )
    st.plotly_chart(fig)

    # Pendapatan Berdasarkan Tahun (bar chart)
    query = """
    SELECT 
        t.CalendarYear, 
        SUM(sf.SalesAmount) AS TotalRevenue
    FROM  
        dw_aw.factinternetsales sf
    JOIN 
        dw_aw.dimtime t ON sf.OrderDateKey = t.TimeKey
    GROUP BY 
        t.CalendarYear
    ORDER BY 
        t.CalendarYear;
    """
    data_aw = pd.read_sql(query, engine)
    total_sales_by_year = data_aw.groupby('CalendarYear')['TotalRevenue'].sum().reset_index()
    fig = px.bar(total_sales_by_year, x='CalendarYear', y='TotalRevenue', 
                labels={'CalendarYear': 'Year', 'TotalRevenue': 'Total Revenue'},
                title='Distribution of Revenue by Year')
    fig.update_layout(
        title_x=0.5,  # Mengatur posisi judul secara horizontal di tengah
        title_font_size=20  # Mengatur ukuran font judul
    )

    # pendapatan berdasarkan promosi
    query = """
    SELECT 
        dp.EnglishPromotionName AS PromotionName,
        SUM(fs.SalesAmount) AS TotalSales
    FROM 
        factinternetsales fs
    JOIN 
        dimpromotion dp ON fs.PromotionKey = dp.PromotionKey
    GROUP BY 
        dp.EnglishPromotionName
    ORDER BY 
        TotalSales DESC;
    """
    data_aw = pd.read_sql(query, engine)
    bar_chart = alt.Chart(data_aw).mark_bar(color='skyblue').encode(
        x=alt.X('PromotionName', sort='-y', title='Promotion'),
        y=alt.Y('TotalSales', title='Total Sales'),
        tooltip=['PromotionName', 'TotalSales']
    ).properties(
        title='Distribution of Revenue by Promotion',
        width=800,
        height=400
    ).configure_axisX(
        labelAngle=45
    ).configure_title(
        fontSize=20,
        # anchor='middle'
    )
    st.altair_chart(bar_chart, use_container_width=True)

    # SECTION CUSTOMER
    st.header('Customer')
    # Pelanggan Berdasarkan Negara (treemap)
    query = """
    SELECT 
        g.EnglishCountryRegionName AS Country,
        COUNT(c.CustomerKey) AS CustomerCount
    FROM 
        dimcustomer c
    JOIN 
        dimgeography g ON c.GeographyKey = g.GeographyKey
    GROUP BY 
        Country
    ORDER BY 
        CustomerCount DESC;
    """
    data_aw = pd.read_sql(query, engine)
    data_aw['label'] = data_aw['Country'] + '<br>' + '(' + data_aw['CustomerCount'].astype(str) + ' customers)'
    fig = px.treemap(data_aw, 
                    path=['label'], 
                    values='CustomerCount')
    fig.update_traces(textinfo='label')
    fig.update_layout(
        title='Distribution of Customers by Country',
        title_font_size=20
    )
    st.plotly_chart(fig)

    # total revenue by customer segment
    query = """
    SELECT 
        t.CalendarYear,
        c.EnglishEducation AS CustomerSegment,
        SUM(fs.SalesAmount) AS TotalSales
    FROM 
        factinternetsales fs
    JOIN 
        dimcustomer c ON fs.CustomerKey = c.CustomerKey
    JOIN 
        dimtime t ON fs.OrderDateKey = t.TimeKey
    GROUP BY 
        t.CalendarYear, c.EnglishEducation
    ORDER BY 
        t.CalendarYear, TotalSales DESC;
    """
    data_aw = pd.read_sql(query, engine)
    chart = alt.Chart(data_aw).mark_line().encode(
        x='CalendarYear:O',  # Menentukan sumbu X sebagai CalendarYear dengan tipe data ordinal
        y='TotalSales:Q',  # Menentukan sumbu Y sebagai TotalSales dengan tipe data kuantitatif
        color='CustomerSegment:N',  # Menentukan warna garis berdasarkan CustomerSegment
        tooltip=['CalendarYear:O', 'CustomerSegment:N', 'TotalSales:Q'],  # Menambahkan tooltip
    ).properties(
        title='Comparison of Sales Performance Across Customer Segments Over Time',
        width=800,
        height=500
    ).configure_title(
        fontSize=20,
        # anchor='middle'
    )
    st.altair_chart(chart, use_container_width=True)

    # SECTION PRODUCT
    st.header('Product')
    # Harga jual dan biaya produksi
    query = """
    SELECT 
        ListPrice,
        StandardCost
    FROM 
        dimproduct;
    """
    data_aw = pd.read_sql(query, engine)
    data_aw['Margin'] = data_aw['ListPrice'] - data_aw['StandardCost']
    average_margin = data_aw['Margin'].mean()
    scatter_plot = alt.Chart(data_aw).mark_circle().encode(
        x='ListPrice',
        y='Margin',
        tooltip=['ListPrice', 'StandardCost', 'Margin']
    ).properties(
        title='Margin between List Price and Standard Cost',
        width=700,
        height=400
    ).interactive()
    average_line = alt.Chart(pd.DataFrame({'average_margin': [average_margin]})).mark_rule(color='red', strokeDash=[3, 3]).encode(
        y=alt.Y('average_margin:Q', title='Average Margin')
    )
    chart = (scatter_plot + average_line)
    st.altair_chart(chart)

    # distribusi harga produk
    query = """
    SELECT 
        p.EnglishProductName AS ProductName,
        p.ListPrice
    FROM 
        dimproduct p
    """
    data_aw = pd.read_sql(query, engine)
    histogram = alt.Chart(data_aw).mark_bar().encode(
        alt.X('ListPrice:Q', bin=alt.Bin(maxbins=30), title='List Price'),
        alt.Y('count():Q', title='Count'),
        tooltip=['ListPrice:Q', 'count():Q']
    ).properties(
        width=700,
        height=400,
        title='Distribution of Product Prices'
    ).configure_title(
        fontSize=20,
        # anchor='middle'
    )
    st.altair_chart(histogram, use_container_width=True)



# DATABASE IMDB
elif db_choice == "Database Scraping IMDb":
    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <img src="{"https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/IMDB_Logo_2016.svg/1150px-IMDB_Logo_2016.svg.png"}" width="200">
        </div>
    """, unsafe_allow_html=True)

    data_imdb = pd.read_csv('imdb_mostpopular_clean.csv')
    
    # COMPARISON
    # Comparison between Gross_US and Gross_World by Open_Week_Date 
    data_imdb['Open_Week_Date'] = pd.to_datetime(data_imdb['Open_Week_Date'])
    data_imdb = data_imdb.sort_values('Open_Week_Date')
    st.subheader('Comparison of Gross US and Gross World over Time')
    chart_gross = alt.Chart(data_imdb).mark_line().encode(
        x='Open_Week_Date:T',
        y=alt.Y('value:Q', title='Gross (in millions)'),
        color='variable:N'
    ).transform_fold(
        ['Gross_US', 'Gross_World'],
        as_=['variable', 'value']
    ).properties(
        width=700,
        height=400
    ).interactive()
    st.altair_chart(chart_gross, use_container_width=True)

    # Comparison sound mix
    def count_sound_mix(data):
        sound_mix_counts = defaultdict(int)
        for sound_mix_str in data['Sound_Mix']:
            if isinstance(sound_mix_str, str):
                sound_mixes = sound_mix_str.split(';')
                for sound_mix in sound_mixes:
                    sound_mix_counts[sound_mix.strip()] += 1
        return sound_mix_counts
    sound_mix_counts = count_sound_mix(data_imdb)
    st.subheader('Number of Films Based on Sound Mix Type')
    st.bar_chart(pd.Series(sound_mix_counts))

    # RELATIONSHIP
    st.subheader('Relationship between Budget and Gross World')
    scatter_plot = alt.Chart(data_imdb).mark_circle().encode(
        x='Budget',
        y='Gross_World',
        tooltip=['Budget', 'Gross_World']
    ).properties(
        width=680,
        height=560
    )
    st.altair_chart(scatter_plot)

    # COMPOSITION
    st.subheader('Aspect Ratio Composition of Most Popular IMDb Films')
    aspect_ratio_counts = data_imdb['Aspect_Ratio'].value_counts().reset_index()
    aspect_ratio_counts.columns = ['Aspect Ratio', 'Count']
    fig = px.pie(aspect_ratio_counts, values='Count', names='Aspect Ratio')
    st.plotly_chart(fig)

    # DISTRIBUTION
    # Distribution most popular movie by runtime
    st.subheader('Distribution of IMDb\'s Most Popular Movie Runtime')
    fig = px.histogram(data_imdb, x='Runtime', nbins=20)
    fig.update_layout(xaxis_title='Runtime (Minutes)', yaxis_title='Frequency')
    st.plotly_chart(fig)

    # Distribution opening week gross by opening date
    st.subheader("Opening Week Gross by Open_Week_Date")
    data_imdb['Open_Week_Date'] = pd.to_datetime(data_imdb['Open_Week_Date'])
    data_imdb = data_imdb.sort_values('Open_Week_Date')
    st.bar_chart(data_imdb.set_index('Open_Week_Date')['Opening_Week'])


st.caption('© Devilia Dwi Candra - 21082010098')