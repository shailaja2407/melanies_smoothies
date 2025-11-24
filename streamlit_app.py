# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
# from snowflake.snowpark.context import get_active_session

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
@@ -12,7 +12,9 @@
st.write("the name on your smoothie will be:",name_on_order )
from snowflake.snowpark.functions import col

session = get_active_session()
# session = get_active_session()
cnx= st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)
ingredients_list = st.multiselect('Choose up to 5 ingredients:'
                                ,my_dataframe)
if ingredients_list:
    # st.write(ingredients_list)
    # st.text(ingredients_list)

    ingredients_string =''
    for each_fruit in ingredients_list:
        ingredients_string+=each_fruit + ' '
    # st.write(ingredients_string)
 
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('"""  + ingredients_string + """',' """  + name_on_order + """')"""
    # st.write(my_insert_stmt)
    # st.stop()
    time_to_insert =st.button("Submit Order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
    st.write(my_insert_stmt)
    
