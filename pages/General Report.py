import streamlit as st
from functions import *
import matplotlib.pyplot as plt


st.set_page_config(page_title="Gen Report")
st.markdown("# Fake visits report")
st.write("""In this page you can see the amount of red and yellow flags that a rep have.
- A rep get a yellow flag if the visit location doesnt match with the account location by a ratio of more than 250m and less than 500m
- A rep get a red flag if the visit location doesnt match with the account location by a ratio of more than  500m
""")


data = uploading_data()

graficas = data.groupby('name').sum()[['Yellow flag','Red flag']].sort_values('Red flag',ascending=False)
st.dataframe(graficas)
st.write("## Top red flags ")
fig, ax = plt.subplots()
plt.barh(graficas.sort_values('Red flag').index,graficas['Red flag'].sort_values())
st.pyplot(fig)

st.write("## Top yellow flags ")
fig, ax = plt.subplots()
plt.barh(graficas.sort_values('Yellow flag').index,graficas['Yellow flag'].sort_values())
st.pyplot(fig)