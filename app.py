import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px

# -----------------------------
# 1. Page Config + Styling
# -----------------------------
st.set_page_config(page_title="Food Wastage Management System", layout="wide")

# Big bold heading
st.markdown(
    "<h1 style='text-align: center; font-size:42px; font-weight: bold </h1>",
    unsafe_allow_html=True

)

# -----------------------------
# 2. SQL Connection
# -----------------------------
engine = create_engine(
    "mssql+pyodbc://@SURABHI\\MSSQLSERVER2022/FoodDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

# -----------------------------
# 3. App Title
# -----------------------------
st.title("🍲 Local Food Wastage Management System")
st.write("Manage food donations, claims, and analyze wastage trends.")

# -----------------------------
# 4. Load Data
# -----------------------------
@st.cache_data
def load_data():
    providers_df = pd.read_sql("SELECT * FROM Providers", engine)
    receivers_df = pd.read_sql("SELECT * FROM Receivers", engine)
    food_df = pd.read_sql("SELECT * FROM Food", engine)
    claims_df = pd.read_sql("SELECT * FROM Claims", engine)
    return providers_df, receivers_df, food_df, claims_df

providers_df, receivers_df, food_df, claims_df = load_data()

# -----------------------------
# 5. KPIs
# -----------------------------
st.subheader("Key Metrics")
total_food = food_df['Quantity'].sum()
completed_claims = claims_df[claims_df['Status'] == 'Completed'].shape[0]
pending_claims = claims_df[claims_df['Status'] == 'Pending'].shape[0]
cancelled_claims = claims_df[claims_df['Status'] == 'Cancelled'].shape[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Food Available", total_food)
col2.metric("Completed Claims", completed_claims)
col3.metric("Pending Claims", pending_claims)
col4.metric("Cancelled Claims", cancelled_claims)

# -----------------------------
# 6. Filters
# -----------------------------
st.subheader("Filters")
city_filter = st.selectbox(
    "Select City",
    pd.concat([providers_df['City'], receivers_df['City']]).unique()
)
provider_type_filter = st.selectbox("Select Provider Type", providers_df['Type'].unique())
meal_type_filter = st.selectbox("Select Meal Type", food_df['Meal_Type'].unique())

filtered_providers = providers_df[providers_df['City'] == city_filter]
filtered_food = food_df[
    (food_df['Location'] == city_filter) &
    (food_df['Meal_Type'] == meal_type_filter) &
    (food_df['Provider_Type'] == provider_type_filter)
]
filtered_claims = claims_df.merge(filtered_food, on='Food_ID', how='inner')

# -----------------------------
# 7. Display Tables
# -----------------------------
st.subheader("Providers in Selected City")
st.dataframe(filtered_providers, use_container_width=True)

st.subheader("Food Listings in Selected City & Meal Type")
st.dataframe(filtered_food, use_container_width=True)

st.subheader("Claims for Selected Filters")
st.dataframe(filtered_claims, use_container_width=True)

# -----------------------------
# 8. Charts
# -----------------------------
st.subheader("📈 Visualizations")

# Top Providers
top_providers = food_df.groupby('Provider_ID')['Quantity'].sum().reset_index()
top_providers = top_providers.merge(providers_df[['Provider_ID', 'Name']], on='Provider_ID')
top_providers = top_providers.sort_values(by='Quantity', ascending=False).head(5)
fig1 = px.bar(top_providers, x='Name', y='Quantity', title="Top 5 Providers by Donations")
st.plotly_chart(fig1, use_container_width=True)

# Claim Status Pie
claim_status = claims_df['Status'].value_counts().reset_index()
claim_status.columns = ['Status', 'Count']
fig2 = px.pie(claim_status, names='Status', values='Count', title="Claims Status")
st.plotly_chart(fig2, use_container_width=True)

# Meal Type Claims
meal_claims = claims_df.merge(food_df[['Food_ID', 'Meal_Type']], on='Food_ID')
meal_count = meal_claims['Meal_Type'].value_counts().reset_index()
meal_count.columns = ['Meal_Type', 'Count']
fig3 = px.bar(meal_count, x='Meal_Type', y='Count', title="Claims per Meal Type")
st.plotly_chart(fig3, use_container_width=True)

# Food by City
city_food = food_df.groupby('Location')['Quantity'].sum().reset_index()
fig4 = px.bar(city_food, x='Location', y='Quantity', title="Food Availability by City")
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# 9. CRUD Operations
# -----------------------------
st.subheader("Manage Data")

# ---- Add Provider ----
with st.expander(" Add New Provider"):
    with st.form("add_provider_form"):
        name = st.text_input("Name")
        type_ = st.text_input("Type")
        address = st.text_input("Address")
        city = st.text_input("City")
        contact = st.text_input("Contact")
        submitted = st.form_submit_button("Add Provider")

        if submitted:
            query = text("""
                INSERT INTO Providers (Name, Type, Address, City, Contact)
                VALUES (:name, :type, :address, :city, :contact)
            """)
            with engine.connect() as conn:
                conn.execute(query, {"name": name, "type": type_, "address": address, "city": city, "contact": contact})
                conn.commit()
            st.success(f"✅ Provider '{name}' added successfully!")

# ---- Update Provider ----
with st.expander(" Update Provider"):
    provider_id = st.selectbox("Select Provider ID", providers_df['Provider_ID'])
    new_contact = st.text_input("New Contact Info")
    if st.button("Update Provider Contact"):
        query = text("UPDATE Providers SET Contact = :contact WHERE Provider_ID = :pid")
        with engine.connect() as conn:
            conn.execute(query, {"contact": new_contact, "pid": provider_id})
            conn.commit()
        st.success("✅ Provider contact updated successfully!")

# ---- Delete Provider ----
with st.expander(" Delete Provider"):
    del_provider_id = st.selectbox("Select Provider ID to Delete", providers_df['Provider_ID'])
    if st.button("Delete Provider"):
        query = text("DELETE FROM Providers WHERE Provider_ID = :pid")
        with engine.connect() as conn:
            conn.execute(query, {"pid": del_provider_id})
            conn.commit()
        st.success("✅ Provider deleted successfully!")

# ---- Add Food Listing ----
with st.expander(" Add New Food Listing"):
    with st.form("add_food_form"):
        fname = st.text_input("Food Name")
        qty = st.number_input("Quantity", min_value=1)
        expiry = st.date_input("Expiry Date")
        prov_id = st.selectbox("Provider ID", providers_df['Provider_ID'])
        prov_type = st.selectbox("Provider Type", providers_df['Type'].unique())
        location = st.text_input("Location")
        food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
        submitted_food = st.form_submit_button("Add Food")

        if submitted_food:
            query = text("""
                INSERT INTO Food (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                VALUES (:fname, :qty, :expiry, :prov_id, :prov_type, :location, :food_type, :meal_type)
            """)
            with engine.connect() as conn:
                conn.execute(query, {
                    "fname": fname, "qty": qty, "expiry": expiry, "prov_id": prov_id,
                    "prov_type": prov_type, "location": location, "food_type": food_type, "meal_type": meal_type
                })
                conn.commit()
            st.success(f"✅ Food '{fname}' added successfully!")

# ---- Delete Food Listing ----
with st.expander(" Delete Food Listing"):
    del_food_id = st.selectbox("Select Food ID to Delete", food_df['Food_ID'])
    if st.button("Delete Food"):
        query = text("DELETE FROM Food WHERE Food_ID = :fid")
        with engine.connect() as conn:
            conn.execute(query, {"fid": del_food_id})
            conn.commit()
        st.success("✅ Food listing deleted successfully!")

# -----------------------------
# End of App
# -----------------------------
