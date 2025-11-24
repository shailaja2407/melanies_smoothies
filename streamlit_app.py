# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# NEW: Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Pull FRUIT_NAME + SEARCH_ON
my_dataframe = session.table('smoothies.public.fruit_options') \
                     .select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to pandas so we can use .loc[]
pd_df = my_dataframe.to_pandas()

# Show what we loaded (optional debugging)
# st.dataframe(pd_df)
# st.stop()

# Multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)

# If user selected fruits
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + " "

        # 💡 Get SEARCH_ON value using Pandas LOC
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        # 💡 SmoothieFroot API Call
        api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        response = requests.get(api_url)

        st.subheader(f"{fruit_chosen} Nutrition Information")
        st.dataframe(response.json())

    # Insert the order into Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie has been ordered!", icon="✅")

    st.write(my_insert_stmt)
