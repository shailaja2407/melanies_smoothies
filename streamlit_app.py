# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake connection (SniS version)
cnx = st.connection("snowflake")
session = cnx.session()

# Customer name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Convert to list for multiselect
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

# Ingredient selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Create order
if ingredients_list:

    ingredients_string = " ".join(ingredients_list)

    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered, " + name_on_order + "!", icon="✅")


# ---------------------------
# SmoothieFroot API Section
# ---------------------------

st.header("Fruit Nutrition Information")

fruit_choice = st.text_input("Enter a fruit to see nutrition info", "watermelon")

if fruit_choice:

    api_url = f"https://my.smoothiefroot.com/api/fruit/{fruit_choice}"

    smoothiefroot_response = requests.get(api_url)

    if smoothiefroot_response.status_code == 200:

        data = smoothiefroot_response.json()

        st.dataframe(
            data=data,
            use_container_width=True
        )

    else:
        st.error("Could not retrieve fruit information.")
