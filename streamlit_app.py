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
#  API CALL (example fruit)
# ---------------------------
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
api_json = smoothiefroot_response.json()
api_df = pd.DataFrame([api_json])

st.subheader("Fruit Info Example (Watermelon)")
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

fruit_table = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row["FRUIT_NAME"] for row in fruit_table.collect()]

# ---------------------------
#  MULTISELECT FOR INGREDIENTS
# ---------------------------
ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_list, max_selections=5)

if ingredients_list:

    ingredients_string = ""

    # ---------------------------
    #  ADDING YOUR SNIPPET HERE
    # ---------------------------
    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + " "

        # SHOW CATEGORY HEADER
        st.subheader(f"{fruit_chosen} • Nutrition Information")

        # CALL API FOR EACH FRUIT
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)

        # CONVERT JSON TO DATAFRAME
        fruit_df = pd.DataFrame([smoothiefroot_response.json()])

        # SHOW NUTRITION TABLE
        st.dataframe(fruit_df, use_container_width=True)

    # ---------------------------
    #  INSERT SQL
    # ---------------------------
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered! ✅")

    st.code(my_insert_stmt)
