# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# ---------------------------
#  TITLE
# ---------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# ---------------------------
#  API CALL (FIXED)
# ---------------------------
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
api_json = smoothiefroot_response.json()

# Convert to DataFrame properly
api_df = pd.DataFrame([api_json])

# Display API Data
st.subheader("Fruit Info from SmoothieFroot API")
st.dataframe(api_df, use_container_width=True)

# ---------------------------
#  NAME ON ORDER
# ---------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# ---------------------------
#  SNOWFLAKE CONNECTION
# ---------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# Read fruit list from Snowflake
fruit_table = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row["FRUIT_NAME"] for row in fruit_table.collect()]   # Convert to Python list

# ---------------------------
#  MULTISELECT FOR INGREDIENTS
# ---------------------------
ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_list, max_selections=5)

if ingredients_list:
    # Join selected fruits into string
    ingredients_string = " ".join(ingredients_list)

    # SQL Insert (corrected spacing)
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit Button
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered! ✅")

    # Show SQL for debugging
    st.code(my_insert_stmt)
