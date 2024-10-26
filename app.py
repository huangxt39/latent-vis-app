import streamlit as st
import pickle
import os
import random

st.set_page_config(layout="wide")


def span_maker(token: str, color_value: float):
    if color_value > 0:
        bg_color = "40,116,166"
    else:
        bg_color = "238,75,43"
    if abs(color_value) > 0.6:
        txt_color = "white"
    else:
        txt_color = "black"
    hover_text = 'title="%.3f"'%color_value
    
    return '<span style="background-color:rgba(%s,%.2f); color: %s" %s>'%(bg_color, abs(color_value), txt_color, hover_text) + token + '</span>' 

def click_random(examples):
    st.session_state.sel_example_idx = random.randint(0, len(examples)-1)


root_path = "./organized"

examples = os.listdir(root_path)

if ("sel_example_idx" not in st.session_state):
    st.session_state.sel_example_idx = random.randint(0, len(examples)-1)
st.session_state.sel_example = st.sidebar.selectbox("select a latent", examples, index=st.session_state.sel_example_idx)

st.sidebar.button("random example", type="primary", on_click=click_random, args=(examples))


with open(os.path.join(root_path, st.session_state.sel_example), "rb") as f:
    cache_obj = pickle.load(f)  # ordereddict

with st.sidebar:
    sel_bin = st.radio("bin", ["All",] + list(cache_obj.keys()), index=0)


# batch_size = 20
# s_idx = st.sidebar.slider("example batch", 0, (len(obj)-1)//batch_size*batch_size, 0, step=batch_size)
# for max_v, str_tokens, values, q_str_tokens, q_pos, _ in obj[s_idx: s_idx+batch_size]:
#     spliter = "&nbsp;"
#     q_str_tokens[q_pos] = "(" + q_str_tokens[q_pos] + ")"
#     row = f'<div style="margin-bottom: 4px;">' + \
#         f"<span> {max_v:.3f} ; </span>" + \
#             spliter.join([span_maker(*temp) for temp in zip(str_tokens, values)]) + \
#             "&nbsp;"*10 + spliter.join(q_str_tokens) + '</div>'
#     st.markdown(row, unsafe_allow_html=True)
    