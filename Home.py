import streamlit as st
from functions import *
import matplotlib.pyplot as plt
import plotly.express as px
from PIL import Image
from streamlit.logger import get_logger

st.set_page_config(page_title="Home",page_icon="🔮")

LOGGER = get_logger(__name__)
add_logo('Imagenes/starlogo.png')

st.markdown("# Home")
st.write(
    """Go to the other pages to see the info!
""")