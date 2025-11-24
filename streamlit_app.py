# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# NEW: Use Streamlit Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("CHOOSE THE FRUITS YOU WANT IN YOUR CUSTOM SMOOTHIE!")

# Ask for name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Load fruits from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options") \
                      .select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert Snowpark DF → Pandas DF so we can use .loc[]
pd_df = my_dataframe.to_pandas()

# Debug view if needed
# st.dataframe(pd_df)
# st.stop()

# Let user pick fruits
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = " ".join(ingredients_list)

    # For each selected fruit...
    for fruit_chosen in ingredients_list:

        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].iloc[0]

        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        # API Call
        st.subheader(f"{fruit_chosen} Nutrition Information")

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Add ORDER_FILLED selection
    order_filled = st.checkbox("Mark order as FILLED?")

    # Insert order SQL
    insert_sql = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order, order_filled)
        VALUES ('{ingredients_string}', '{name_on_order}', {str(order_filled).upper()})
    """

    if st.button("Submit Order"):
        session.sql(insert_sql).collect()
        st.success("Your Smoothie is ordered!", icon="✅")

    st.write(insert_sql)
