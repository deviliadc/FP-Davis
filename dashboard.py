import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import toml
from collections import defaultdict
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Membaca file config.toml
config = toml.load('config.toml')

# Mendapatkan informasi koneksi dari file
db_username = config['database']['username']
db_password = config['database']['password']
db_host = config['database']['host']
db_name = config['database']['name']

encoded_password = quote_plus(db_password)

# Membuat URL koneksi menggunakan SQLAlchemy
connection_string = f'mysql+mysqlconnector://{db_username}:{encoded_password}@{db_host}/{db_name}'
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
    st.write('Berdasarkan visualisai diatas dapat dilihat perbandingan jumlah pemesanan dari tiap-tiap negara. ' 
            'Hasil visualisasi menunjukkan negara dengan total pesanan tertinggi ada pada United States dengan jumlah 11631 '
            'dan negara dengan total pesanan terendah ada pada France dengan jumlah 2975.')

    # Tren jumlah penjualan tiap tahun
    query = """
    SELECT 
        t.CalendarYear AS Years, 
        COUNT(sf.OrderQuantity) AS 'Order Count'
    FROM  
        factinternetsales sf
    JOIN 
        dimtime t ON sf.OrderDateKey = t.TimeKey
    GROUP BY 
        t.CalendarYear
    ORDER BY 
        t.CalendarYear;
    """
    data_aw = pd.read_sql(query, engine)
    data_aw['Years'] = data_aw['Years'].astype(str)
    line_chart = alt.Chart(data_aw).mark_line().encode(
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
    st.write('Berdasarkan visualisasi diatas dapat dilihat trend jumlah penjualan tiap tahun. '
            'Tren tersebut menunjukkan perubahan secara positif, dimana tiap tahun jumlah pesanan semakin bertambah. '
            'Pada tahun 2001 jumlah pesanan sebanyak 1013 pesanan, tahun 2002 sebanyak 2677 pesanan, tahun 2003 sebanyak 24443 pesanan, '
            'dan pada tahun 2004 sebanyak 32265 pesanan')

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
    st.write('Dari hasil visualisasi tersebut dapat dilihat bahwa pendapatan paling banyak berasal dari '
            'kategori produk sepeda, lalu aksesoris, dan yang terakhir pakaian.')

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
    st.write('Visualisasi tersebut menunjukkan hasil pendapatan berdasarkan wilayah penjualan. Dimana '
            'dapat diketahui bahwa pendapatan yang tinggi ditandai dengan warna kuning terang dan pendapatan rendah dengan warna ungu gelap. '
            'Pada visualisasi ini yang ditandai dengan warna kuning adalah wilayah Australia artinya wilayah tersebut memiliki pendapatan yang tinggi '
            'dan untuk wilayah dengan warna ungu gelap yang artinya memiliki pendapatan yang rendah yaitu daerah Southwest.')

    # Pendapatan Berdasarkan Tahun (bar chart)
    query = """
    SELECT 
        t.CalendarYear, 
        SUM(sf.SalesAmount) AS TotalRevenue
    FROM  
        factinternetsales sf
    JOIN 
        dimtime t ON sf.OrderDateKey = t.TimeKey
    GROUP BY 
        t.CalendarYear
    ORDER BY 
        t.CalendarYear;
    """
    data_aw = pd.read_sql(query, engine)
    total_sales_by_year = data_aw.groupby('CalendarYear')['TotalRevenue'].sum().reset_index()
    total_sales_by_year['CalendarYear'] = total_sales_by_year['CalendarYear'].astype(int)
    fig = px.bar(total_sales_by_year, x='CalendarYear', y='TotalRevenue', 
                labels={'CalendarYear': 'Year', 'TotalRevenue': 'Total Revenue'},
                title='Distribution of Revenue by Year')
    fig.update_layout(
        title_font_size=20, 
        xaxis = dict(
        tickmode = 'linear',
        tick0 = total_sales_by_year['CalendarYear'].min(),
        dtick = 1
        )
    )
    st.plotly_chart(fig)
    st.write('Visualisasi tersebut menunjukkan distribusi pendapatan berdasarkan tahun, dimana dapat dilihat bahwa pendapatan '
            'naik setiap tahunnya. Pada tahun 2001 pendapatan berkisar di 3M, di tahun 2002 pendapatan naik ke 5M dan pada tahun '
            '2003 dan 2004 pendapatan mencapai 10M.')

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
    st.write('Visualisasi tersebut menunjukkan pendapatan perusahaan berdasarkan promosi. Dapat dilihat bahwa pendapatan paling banyak didapatkan '
            'dengan tidak melakukan promosi. Jadi meskipun perusahaan tidak melakukan promosi pendapatan tetap akan masuk. Dan hal ini juga membuktikan '
            'bahwa promosi tidak terlalu mempengaruhi hasil pendapatan perusahaan.')

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
    st.write('Visualisasi tersebut menunjukkan distribusi pelanggan. Jumlah pelanggan paling banyak terdapat di wilayah United States, '
            'selanjutnya Australia, United Kingdom, France, Germany dan terakhir Canada.')

    # pendapatan berdasarkan customer segment
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
        x='CalendarYear:O', 
        y='TotalSales:Q', 
        color='CustomerSegment:N', 
        tooltip=['CalendarYear:O', 'CustomerSegment:N', 'TotalSales:Q'],  
    ).properties(
        title='Comparison of Sales Performance Across Customer Segments Over Time',
        width=800,
        height=500
    ).configure_title(
        fontSize=20,
        # anchor='middle'
    )
    st.altair_chart(chart, use_container_width=True)
    st.write('Grafik tersebut menunjukkan perbandingan kinerja penjualan di berbagai segmen customer tiap tahun. '
            'Customer paling banyak di dominasi oleh Bachelors di setiap tahunnya. Dan yang paling rendah dari Partial High School.')

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
    st.write('Pada hasil visualisasi tersebut dapat dilihat hubungan antara Standart Cost (harga bahan baku) dan List Price (harga jual). '
            'Garis putus-putus merah pada visualisasi tersebut menunjukkan rata-rata List Price dikurangi Standard Cost. Dapat dilihat bahwa '
            'masih banyak harga jual yang dibawah rata-rata tersebut, namun tidak sedikit juga harga jual yang lebih tinggi dari rata-rata tersebut.')


# DATABASE IMDB
elif db_choice == "Database Scraping IMDb":
    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <img src="{"https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/IMDB_Logo_2016.svg/1150px-IMDB_Logo_2016.svg.png"}" width="200">
        </div>
    """, unsafe_allow_html=True)

    data_imdb = pd.read_csv('imdb_mostpopular_clean.csv')
    
    # perbandingan Budget, Gross_US and Gross_World berdasarkan Open_Week_Date 
    data_imdb['Open_Week_Date'] = pd.to_datetime(data_imdb['Open_Week_Date'])
    data_imdb = data_imdb.sort_values('Open_Week_Date')
    st.subheader('Comparison of Gross US and Gross World over Time')
    chart_gross = alt.Chart(data_imdb).mark_line().encode(
        x='Open_Week_Date:T',
        y=alt.Y('value:Q', title='Gross (in millions)'),
        color='variable:N'
    ).transform_fold(
        ['Budget', 'Gross_US', 'Gross_World'],
        as_=['variable', 'value']
    ).properties(
        width=700,
        height=400
    ).interactive()
    st.altair_chart(chart_gross, use_container_width=True)
    st.write('Dari visualisasi tersebut. dapat dilihat perbandingan antara Budget, Gross US dam Gross World. Dimana hasil menunjukkan bahwa '
            'tiap tahun pendapatan dan budget selalu mengalami kenaikan dan dapat dilihat pula bahwa banyak sekali pendapatan yang diatas budget.')

    # hubungan Budget dan Gross World
    st.subheader('Margin between Budget and Gross World')
    data_imdb['Margin'] = data_imdb['Gross_World'] - data_imdb['Budget']
    average_margin = data_imdb['Margin'].mean()
    scatter_plot = alt.Chart(data_imdb).mark_circle().encode(
        x='Gross_World',
        y='Margin',
        tooltip=['Gross_World', 'Budget', 'Margin']
    ).properties(
        width=700,
        height=400
    ).interactive()
    average_line = alt.Chart(pd.DataFrame({'average_margin': [average_margin]})).mark_rule(color='red', strokeDash=[3, 3]).encode(
        y=alt.Y('average_margin:Q', title='Average Margin')
    )
    chart = (scatter_plot + average_line)
    st.altair_chart(chart)
    st.write('Pada hasil visualisasi tersebut dapat dilihat hubungan antara anggaran (budget) dan pendapatan kotor (gross income) secara global. '
            'Garis putus-putus merah pada visualisasi tersebut menunjukkan rata-rata pendapatan dikurangi budget. '
            'Hasilnya menunjukkan bahwa, banyak sekali film-film yang pendapatannya dibawah rata-rata tersebut, bahkan ada film yang budgetnya tinggi, namun ternyata'
            'pendapatannya minus. Namun disisi lain ada juga film yang pendapatannya jauh melampaui rata-rata.')

    # distribusi opening week gross berdasarkan opening date
    st.subheader("Distribution of Opening Week Gross by Open Week Date")
    data_imdb['Open_Week_Date'] = pd.to_datetime(data_imdb['Open_Week_Date'])
    data_imdb = data_imdb.sort_values('Open_Week_Date')
    st.line_chart(data_imdb.set_index('Open_Week_Date')['Opening_Week'])
    st.write('Pada visualisasi tersebut dapat dilihat distribusi laba kotor minggu pembukaan berdasarkan tanggal pembukaan. '
            'Dapat terlihat fluktuasi naik turun dari visualisasi tersebut, namun dapat terlihat bahwa semakin hari, '
            'laba kotor semakin naik walaupun ada penurunan sekitar tahun 2015 sampai dengan 2020')

    # Aspect Ratio Composition of Most Popular IMDb Films
    st.subheader('Aspect Ratio Composition of Most Popular IMDb Films')
    aspect_ratio_counts = data_imdb['Aspect_Ratio'].value_counts().reset_index()
    aspect_ratio_counts.columns = ['Aspect Ratio', 'Count']
    fig = px.pie(aspect_ratio_counts, values='Count', names='Aspect Ratio')
    st.plotly_chart(fig)
    st.write('Visualisasi diatas menunjukkan komposisi Aspect Ratio yang sering digunakan dalam film yang ada di list most popular imdb. '
            'Dapat dilihat bahwa Aspect Ratio yang paling banyak digunakan yaitu 2.39:1 dengan total presentase 64.6%, '
            'selanjutnya Aspect Ratio 1.85:1 dengan presentase 22.9%, dan untuk Aspect Ratio lainnya memiliki jumlah persentase yang sama yaitu 2.08%.')

    # distribusi runtime film populer
    st.subheader('Distribution of IMDb\'s Most Popular Movie Runtime')
    fig = px.histogram(data_imdb, x='Runtime', nbins=20)
    fig.update_layout(
        xaxis_title='Runtime (Minutes)', 
        yaxis_title='Frequency')
    st.plotly_chart(fig)
    st.write('Dari visualisasi diatas dapat diketahui bahwa pada data film terpopuler IMDB, runtime yang memiliki jumlah film terbanyak yaitu pada 115-119 menit dengan total 7 film, '
            'yang kedua yaitu pada runtime 120-124 menit sebanyak 6 film, ketiga pada runtime 110-114 menit dengan total 5 film, pada runtime 130-134 menit dengan total 4 film, dan runtime lainnya antara 1-3 film')

    # perbandingan jumlah sound
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
    st.write('Pada visualisasi tersebut, dapat dilihat tipe sound yang paling sering digunakan oleh film populer IMDB. Peringkat pertama diduduki oleh Dolby Digital yaitu 36 film, lalu Dolby Atmos yaitu 33 film, '
            'IMAX6-Track yaitu 16 film, Dolby Surround 7.1yaitu 15 film dan untuk sound lainnya diantara 1-11 film yang menggunakan sound tersebut.')


st.caption('© Devilia Dwi Candra - 21082010098')