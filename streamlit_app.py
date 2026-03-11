# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests


# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")


# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()


# User input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)


# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Convert Snowflake dataframe to list
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()


# Ingredient selector
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)


# Process order
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + " "

        # Call SmoothieFroot API for each selected fruit
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}"
        )

        # Display nutrition data
        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )


    # Insert order into Snowflake
    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """


    # Submit order button
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success(
            "Your Smoothie is ordered, " + name_on_order + "!",
            icon="✅"
        )
