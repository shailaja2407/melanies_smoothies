# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# NEW: Use Streamlit Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """cHOOSE THE FRUTS YOU WANT IN YOUR CUSTOM SMOOTHIE!
  """
)

name_on_order = st.text_input("Name on Smoothi:")
st.write("the name on your smoothie will be:", name_on_order)

# Load fruits
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Let user pick fruits
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe
)

if ingredients_list:

    ingredients_string = ''
    for each_fruit in ingredients_list:
        ingredients_string += each_fruit + ' '

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

    st.write(my_insert_stmt)
