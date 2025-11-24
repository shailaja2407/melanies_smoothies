# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# ---------------------------
#  PAGE TITLE
# ---------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")


# ---------------------------
#  API CALL TO SMOOTHIEFROOT
# ---------------------------
smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

# Convert API JSON into a DataFrame
api_json = smoothiefroot_response.json()
api_df = pd.DataFrame([api_json])

# Display API Data
st.subheader("Fruit Info from SmoothieFroot API")
st.dataframe(api_df, use_container_width=True)


# ---------------------------
#  GET NAME ON ORDER
# ---------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)


# ---------------------------
#  SNOWFLAKE CONNECTION
# ---------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options from Snowflake table
fruit_table = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

# Convert Snowflake result to list
fruit_options = [row["FRUIT_NAME"] for row in fruit_table.collect()]


# ---------------------------
#  MULTISELECT FOR INGREDIENTS
# ---------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# If the user selected ingredients
if ingredients_list:

    # Convert list → space-separated string
    ingredients_string = " ".join(ingredients_list)

    # Safe INSERT statement using Snowpark parameters (no SQL injection)
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES (:ingredients, :name)
    """

    # Submit button
    if st.button("Submit Order"):
        session.sql(
            my_insert_stmt,
            {
                "ingredients": ingredients_string,
                "name": name_on_order
            }
        ).collect()

        st.success("Your Smoothie is ordered! ✅")

    # Display the SQL for debugging
    st.code(
        f"INSERT INTO smoothies.public.orders(ingredients, name_on_order)\n"
        f"VALUES ('{ingredients_string}', '{name_on_order}')"
    )
