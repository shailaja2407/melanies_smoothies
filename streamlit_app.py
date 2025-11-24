# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# ---------------------------
#  TITLE
# ---------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")


# ---------------------------
#  API EXAMPLE (WATERMELON DEMO)
# ---------------------------
try:
    example_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
    example_df = pd.DataFrame([example_response.json()])
    st.subheader("Example Nutrition Data (Watermelon)")
    st.dataframe(example_df, use_container_width=True)
except:
    st.warning("SmoothieFroot API not reachable right now.")


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

# Read GUI name + API name from Snowflake
fruit_table = session.table("smoothies.public.fruit_options").select(
    "FRUIT_NAME", "SEARCH_ON"
)

rows = fruit_table.collect()

# Lookup dictionary: GUI name → API search value
fruit_lookup = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in rows}

# GUI list
fruit_names = list(fruit_lookup.keys())


# ---------------------------
#  MULTISELECT
# ---------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_names,
    max_selections=5
)


# ---------------------------
#  SHOW NUTRITION INFO FOR EACH SELECTED FRUIT
# ---------------------------
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        # Build the string for inserting into Snowflake
        ingredients_string += fruit_chosen + " "

        api_name = fruit_lookup[fruit_chosen]    # <- fixes Strawberries → Strawberry

        st.subheader(f"{fruit_chosen} • Nutrition Information")

        try:
            response = requests.get("https://my.smoothiefroot.com/api/fruit/" + api_name)

            if response.status_code == 200:
                fruit_df = pd.DataFrame([response.json()])
                st.dataframe(fruit_df, use_container_width=True)
            else:
                st.error(f"No data found in SmoothieFroot for: {api_name}")

        except Exception as e:
            st.error(f"Error retrieving data for {api_name}: {e}")


    # ---------------------------
    #  INSERT ORDER INTO SNOWFLAKE
    # ---------------------------
    insert_sql = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(insert_sql).collect()
        st.success("Your Smoothie is ordered! 🎉")

    st.code(insert_sql)
