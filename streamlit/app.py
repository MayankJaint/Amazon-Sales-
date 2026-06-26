import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.ticker as mtick
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


# ==========================================
# LAYER 2: DATA LOADING & CACHING
# ==========================================
@st.cache_data
def load_data():
    # Ensure 'amazon_EDA.csv' is in the exact same folder as this app.py file
    df = pd.read_csv("streamlit/amazon_EDA.csv")
    # Clean price and ratings
    df["discounted_price"] = pd.to_numeric(
        df["discounted_price"].astype(str).str.replace("₹", "").str.replace(",", ""),
        errors="coerce",
    )
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # Drop rows missing critical data
    return df.dropna(subset=["main_category", "discounted_price", "rating"])


def create_kpi_card(title, value, formula, description, color_hex):
    return f"""
    <div style="background-color: #232635; padding: 25px 20px; border-radius: 12px; text-align: center; height: 100%; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
        <p style="color: #8C92A4; font-size: 0.8rem; font-weight: 600; letter-spacing: 1px; margin-bottom: 15px; text-transform: uppercase;">
            {title}
        </p>
        <p style="color: {color_hex}; font-size: 2.8rem; font-weight: 700; margin: 0; line-height: 1.2;">
            {value}
        </p>
        <p style="color: #646A7E; font-size: 0.85rem; font-style: italic; margin-top: 15px; margin-bottom: 10px;">
            {formula}
        </p>
        <p style="color: #9AA0A6; font-size: 0.85rem; line-height: 1.5; margin-bottom: 0;">
            {description}
        </p>
    </div>
    """

# ==========================================
# LAYER 4: THE SIDEBAR (Filters)
# ==========================================

# 1. Add the Logo to the very top of the sidebar
# 'use_container_width=True' forces the image to fit perfectly inside your 350px sidebar!
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", use_container_width=True)
st.sidebar.header("⚙️ Dashboard Controls")

df = load_data() # Call the function to load the data into df

# 2. Category Dropdown
category_list = df['main_category'].unique().tolist()
category_list.sort() 
selected_cat = st.sidebar.selectbox("Select a Category:", ["All Categories"] + category_list)

st.sidebar.divider()

# 3. Price Range Slider
min_price = int(df['discounted_price'].min())
max_price = int(df['discounted_price'].max())
selected_price = st.sidebar.slider(
    "Select Price Range (₹):", 
    min_value=min_price, max_value=max_price, 
    value=(min_price, max_price) 
)

# 4. Minimum Rating Slider
min_rating = st.sidebar.slider("Minimum Rating ⭐:", min_value=1.0, max_value=5.0, value=1.0, step=0.5)

# --- APPLY ALL FILTERS MATHEMATICALLY ---
filtered_df = df.copy()
if selected_cat != "All Categories":
    filtered_df = filtered_df[filtered_df['main_category'] == selected_cat]
filtered_df = filtered_df[(filtered_df['discounted_price'] >= selected_price[0]) & (filtered_df['discounted_price'] <= selected_price[1]) & (filtered_df['rating'] >= min_rating)]

# ==========================================
# LAYER 5: MAIN UI & KPI METRICS
# ==========================================
st.title("Amazon India Market Analytics Dashboard")

st.markdown("""
🙌 Welcome to the interactive **Amazon India Market Explorer**. 
Use the control panel on the left to slice through thousands of products in real-time. 
Analyze pricing distributions, uncover market hierarchies, and extract customer sentiment instantly.
""")
st.divider()
# --- ROW 1: High-Level Metrics ---
col1, col2, col3 = st.columns(3)

with col1: 
    html_card = create_kpi_card(
        title="Total Products Listed",
        value=f"{len(filtered_df):,}",
        formula="count(Product_ID)",
        description="Current volume of items actively filtered in the dataset.",
        color_hex="#00E5FF" # Cyan
    )
    st.markdown(html_card, unsafe_allow_html=True)

with col2: 
    avg_rating = filtered_df['rating'].mean()
    html_card = create_kpi_card(
        title="Average Customer Rating",
        value=f"{avg_rating:.2f}",
        formula="sum(Ratings) / count(Products)",
        description="Aggregate satisfaction score across selected categories.",
        color_hex="#B388FF" # Purple
    )
    st.markdown(html_card, unsafe_allow_html=True)

with col3: 
    avg_price = filtered_df['discounted_price'].mean()
    html_card = create_kpi_card(
        title="Average Market Price",
        value=f"₹{avg_price:,.0f}",
        formula="mean(Discounted_Price)",
        description="The average purchasing cost after applied vendor discounts.",
        color_hex="#00E676" # Green
    )
    st.markdown(html_card, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- ROW 2: Deep EDA Metrics ---
col4, col5, col6 = st.columns(3)

with col4:
    unique_subcats = filtered_df['sub_category'].nunique()
    html_card = create_kpi_card(
        title="Market Segments",
        value=f"{unique_subcats:,}",
        formula="nunique(Sub_Category)",
        description="Total distinct product niches competing in this space.",
        color_hex="#FFCA28" # Yellow
    )
    st.markdown(html_card, unsafe_allow_html=True)

with col5:
    try:
        max_discount = filtered_df['discount_percentage'].max()
        val = f"{max_discount:.0f}%"
    except:
        val = "N/A"
    
    html_card = create_kpi_card(
        title="Maximum Discount",
        value=val,
        formula="max(Discount_Percentage)",
        description="The most aggressive price reduction currently offered.",
        color_hex="#00E5FF" # Cyan
    )
    st.markdown(html_card, unsafe_allow_html=True)

with col6:
    top_tier_count = len(filtered_df[filtered_df['rating'] >= 4.5])
    html_card = create_kpi_card(
        title="Top Tier Products",
        value=f"{top_tier_count:,}",
        formula="count(Products where Rating >= 4.5)",
        description="Volume of elite products maintaining near-perfect sentiment.",
        color_hex="#00E676" # Green
    )
    st.markdown(html_card, unsafe_allow_html=True)
    
    # ==========================================
    # LAYER 6: INTERACTIVE CHART TOGGLE
    # ==========================================
    # Create the radio button switch (horizontal design)
chart_choice = st.radio(
        "Select Chart to View:",
        [
            "Category Hierarchy",
            "Price distributions",
            "4D Market Map",
            "Customer Sentiment",
        ],
        horizontal=True,
    )
    
    # Sample data so the web browser doesn't freeze on heavy visuals
sample_df = filtered_df.sample(n=min(1500, len(filtered_df)), random_state=42)
    
    # --- The Logic Switch ---
    
if chart_choice == "Category Hierarchy":
    st.subheader("Category Hierarchy")
    # ==========================================
    # 1. PREPARE THE HIERARCHICAL DATA
    # ==========================================
    # We group by BOTH categories to count exactly how many items exist in each specific combination
    hierarchy_counts = (
        df.groupby(["main_category", "sub_category"]).size().reset_index(name="count")
    )

    # ==========================================
    # 2. FILTERING (To prevent browser lag)
    # ==========================================
    # Find the Top 5 Main Categories
    top_mains = df["main_category"].value_counts().nlargest(5).index

    # Keep only the rows that belong to those Top 5 Main Categories
    hierarchy_filtered = hierarchy_counts[
        hierarchy_counts["main_category"].isin(top_mains)
    ]

    # The Magic Trick: Keep only the Top 10 Subcategories WITHIN each Main Category
    hierarchy_final = (
        hierarchy_filtered.sort_values(
            ["main_category", "count"], ascending=[True, False]
        )
        .groupby("main_category")
        .head(10)
    )
    # ==========================================
    # 3. BUILD THE INTERACTIVE TREEMAP
    # ==========================================
    fig = px.treemap(
        hierarchy_final,
        path=[
            "main_category",
            "sub_category",
        ],  # <--- This tells Plotly who is the Parent and who is the Child!
        values="count",  # Box size is based on item count
        color="main_category",  # Color-code by the parent category
        title="Amazon Product Hierarchy: Main Category vs. Subcategory",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )

    # Make the labels clear and readable
    fig.update_traces(textinfo="label+value+percent parent")
    fig.update_layout(margin=dict(t=80, l=25, r=25, b=25))
    st.plotly_chart(fig, use_container_width=True)


elif chart_choice == "Rating Distributions":
    st.subheader("Category Rating Distributions")

    # Generate the Violin Plot with an embedded Box Plot
    fig_violin = px.violin(
        sample_df,
        x="main_category" ,
        y="rating",
        box=True,  # Embeds the statistical boxplot inside the violin
        points="all",  # Shows the underlying dots (jitter) to prove density
        color="main_category",
        hover_data=["discounted_price"],  # Shows the price when hovering over a dot!
    )

    # Clean up the layout and remove the redundant legend
    fig_violin.update_layout(
        template="plotly_dark", showlegend=False, margin=dict(l=0, r=0, b=0, t=30)
    )
    st.plotly_chart(fig_violin, use_container_width=True)

elif chart_choice == "4D Market Map":
    st.subheader("4D Market Mapping")

    fig_3d = px.scatter_3d(
        sample_df,
        x="actual_price",
        y="discount_percentage",
        z="rating",
        color="sub_category",
    )
    # Apply dark theme, shrink dots, and minimize margins
    fig_3d.update_layout(template="plotly_dark", margin=dict(l=0, r=0, b=0, t=0))
    fig_3d.update_traces(marker=dict(size=4))

    st.plotly_chart(fig_3d, use_container_width=True)

    
elif chart_choice == "Customer Sentiment":
    st.subheader("Word Cloud: Customer Sentiment & Keywords")

    # 1. Combine all the text from your chosen column into one giant string
    # Change 'product_name' to whatever column holds your text data!
    good_reviews = (
        sample_df[sample_df["rating"] > 4.2]["review_title"].dropna().astype(str)
    )
    bad_reviews = df[df["rating"] < 3.5]["review_title"].dropna().astype(str)

    # Combining all good reviews into a single string
    text_good = " ".join(review for review in good_reviews)
    text_bad = " ".join(review for review in bad_reviews)
    # Defining the Stopwords to filter out cloud
    custom_stopwords = set(STOPWORDS)
    custom_stopwords.update(["product", "amazon", "buy", "good", "bad", "item"])

    # =====================================
    #    DESIGNING THE  WORD CLOUDS
    # =====================================
    wordcloud_good = WordCloud(
        width=800,
        height=400,
        background_color="white",
        stopwords=custom_stopwords,
        colormap="Greens",
        max_words=100,
    ).generate(text_good)
    wordcloud_bad = WordCloud(
        width=800,
        height=400,
        background_color="white",
        stopwords=custom_stopwords,
        colormap="Reds",
        max_words=100,
    ).generate(text_bad)

    # =====================================
    #     PLOTTING THE WORD CLOUDS
    # =====================================
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    # PLOT GOOD REVIEWS
    axes[0].imshow(wordcloud_good, interpolation="bilinear")
    axes[0].set_title(
        "Top Words From Good Reviews",
        fontsize=16,
        fontweight="bold",
        color="green",
        pad=15,
    )
    axes[0].axis("off")

    # PLOT BAD REVIEWS
    axes[1].imshow(wordcloud_bad, interpolation="bilinear")
    axes[1].set_title(
        "Top Words From Bad Reviews",
        fontsize=16,
        fontweight="bold",
        color="red",
        pad=15,
    )
    axes[1].axis("off")

    # Notice we use st.pyplot() here instead of st.plotly_chart()!
    st.pyplot(fig, use_container_width=True)
elif chart_choice == "Price distributions":
    st.divider()
    # The screen is divided into 4 total parts (1 + 1). 
    # The left gets 75% of the space, the right gets 25%.
    # main_col, side_col = st.columns([1, 1])
    
    # with main_col:
    fig_actual = plt.figure(figsize =(10,6))
    sns.histplot(x=df['actual_price'], bins = 40,color = 'green', kde = True, log_scale = True)
    plt.title('Distribution of Actual Price', fontsize  = 15, fontweight = 'bold')
    st.pyplot(fig_actual, use_container_width=True)
    
    # with side_col:
    # st.plotly_chart(fig_tree, use_container_width=True)
    fig_discounted = plt.figure(figsize =(10,6)) # Assign the created figure to 'fig_discounted'
    sns.histplot(x=df['discounted_price'], bins = 40,color = 'green', kde = True, log_scale = True)
    plt.title('Distribution of Discounted Price',fontsize  = 15, fontweight = 'bold')
    st.pyplot(fig_discounted, use_container_width=True)
st.divider()
# ==========================================
# LAYER 3: CSS HACKS (Theme Adaptive)
# ==========================================
st.markdown(
    """
    <style>
    
    /* 1. The Logo "Sticker" Fix (Keep this!) */
    [data-testid="stSidebar"] img {
        background-color: white; 
        padding: 10px;
        border-radius: 8px;      
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.subheader("Multivariate Correlation Heatmap")

# 1. Isolate the numeric columns
# A correlation matrix will crash if it tries to do math on text columns like 'product_title'
numeric_df = filtered_df.select_dtypes(include=['float64', 'int64'])

# 2. Calculate the Pearson correlation matrix
corr_matrix = numeric_df.corr()

# 3. Generate the Heatmap using Plotly
fig_heatmap = px.imshow(
    corr_matrix,
    text_auto=".2f",               # Prints the exact correlation number to 2 decimal places
    color_continuous_scale="RdBu_r", # A professional Red-Blue diverging color scale
    zmin=-1, zmax=1,               # Locks the color scale perfectly between -1 and 1
    aspect="auto"                  # Forces the chart to stretch to fit the screen
)

# 4. Apply the dark theme to match your KPI cards
fig_heatmap.update_layout(
    template='plotly_dark', 
    margin=dict(l=0, r=0, b=0, t=30)
)

st.plotly_chart(fig_heatmap, use_container_width=True)
# ==========================================
# LAYER 7: EXECUTIVE INSIGHTS
# ==========================================
st.divider()
st.subheader("💡 Executive Summary & Insights")

st.info("**Market Concentration:** : The ecosystem is heavily dominated by three parent categories: Electronics, Computer & Accessories, and Home & Kitchen. Within these silos, monopolies exist; for example, Accessories & Peripherals control a staggering 84% of the Computer market")

st.success("**Pricing Dynamics:** The vast majority of product volume is pushed in the ₹100–₹1,000 tier, driven by aggressive 50-60% average discounts. However, premium products listed around the ₹10,000 mark show remarkable resilience, consistently maintaining 4-star averages with varied 20-80% discount strategies.")

st.warning("**Sentiment Drivers:** NLP text analysis reveals a highly price-sensitive consumer base. Both 5-star and 1-star reviews are heavily anchored by the exact same keywords: quality, money, and work. This indicates that the price-to-performance ratio, rather than brand loyalty, is the ultimate driver of customer satisfaction in the Indian e-commerce space..")
