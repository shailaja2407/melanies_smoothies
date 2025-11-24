# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("CHOOSE THE FRUITS YOU WANT IN YOUR CUSTOM SMOOTHIE!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect("Choose up to 5 ingredients:", my_dataframe)

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # SmoothieFroot API call for each chosen fruit
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/watermelon"
        )

        sf_df = pd.DataFrame([smoothiefroot_response.json()])
        st.dataframe(sf_df, use_container_width=True)

    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")

    st.write(my_insert_stmt)
