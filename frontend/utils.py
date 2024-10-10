import base64
import streamlit as st
def render_svg(svg, width=100):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,{}" style="width: {}%; border: 1px solid black"/>'.format(b64, width)
    st.write(html, unsafe_allow_html=True)