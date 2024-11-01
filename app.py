import streamlit as st
import pickle
import os
import random
from utils import *

st.set_page_config(layout="wide")


def span_maker(token: str, color_value: float, norm_term: float, bg_color: str):
    if color_value/norm_term > 0.6:
        txt_color = "white"
    else:
        txt_color = "black"
    hover_text = 'title="%.3f"'%color_value
    
    return '<span style="background-color:rgba(%s,%.2f); color: %s" %s>'%(bg_color, color_value/norm_term, txt_color, hover_text) + token + '</span>' 

def click_random(examples):
    st.session_state.sel_example_idx = random.randint(0, len(examples)-1)

def show_one_sample(str_tokens, score, max_idx, max_act, prev_ctx, futr_ctx, bg_color, normalizer):
    shown_value = f"<span> {max_act:.3f} ; </span>"
    str_tokens[max_idx] = "<u>" + str_tokens[max_idx] + "</u>"

    length = len(str_tokens)
    s_idx = 0 if prev_ctx == "inf" else max(0, max_idx-int(prev_ctx))
    e_idx = length if futr_ctx == "inf" else min(length, max_idx+int(futr_ctx)+1)
    str_tokens = str_tokens[s_idx:e_idx]
    score = score[s_idx:e_idx]

    row = f'<div style="margin-bottom: 8px;">' + shown_value + "".join([span_maker(t, v, normalizer, bg_color) for t, v in zip(str_tokens, score)]) + '</div>'
    st.markdown(row, unsafe_allow_html=True)


root_path = "./latent_acts"  

selected_cc = st.sidebar.selectbox("Crosscoder", os.listdir(root_path), index=os.listdir(root_path).index("v2_17"))  
st.session_state.selected_cc = selected_cc
cc_path = os.path.join(root_path, selected_cc)

examples = os.listdir(cc_path)
examples = [file.rstrip(".pkl") for file in examples]

if ("sel_example_idx" not in st.session_state) or st.session_state.sel_example_idx >= len(examples):
    st.session_state.sel_example_idx = random.randint(0, len(examples)-1)
st.session_state.sel_example = st.sidebar.selectbox("select a latent", examples, index=st.session_state.sel_example_idx)

st.sidebar.button("random latent", type="primary", on_click=click_random, args=(examples,))


with open(os.path.join(cc_path, st.session_state.sel_example+".pkl"), "rb") as f:
    saved_obj = pickle.load(f)  # ordereddict
    decoder_vec, cache_obj = saved_obj["decoder_vec"], saved_obj["latent_acts"]

with st.sidebar:
    prev_ctx = st.select_slider("# prev context", ["5", "25", "100", "inf"], value="100")
    futr_ctx = st.select_slider("# future context", ["5", "25", "100", "inf"], value="5")

    show_attr = st.toggle("show attribution", value=False)
    sel_bin = st.radio("bin", ["All",] + list(cache_obj.keys()), index=0)
    num_sample_per_bin = st.slider("#sample", 1, 100, 10 if sel_bin == "All" else 100)
    unnormalize = st.toggle("unnormalize decoder")

    show_info = st.toggle("show info", value=False)

# show figures
if unnormalize:
    # the term that is used to normalize activations when training crosscoder
    normalisation_factor = np.array([ 1.8281, 2.0781, 2.2031, 2.4062, 2.5781, 2.8281, 3.1562, 3.6875, 4.3125, 5.4062, 7.8750, 16.5000,])
    decoder_vec = decoder_vec * normalisation_factor[:, None]
show_figures_per_latent(decoder_vec)

if show_info:
    st.caption("""
            50 latents are sampled uniformly from each Crosscoder
               
            The underscored token is the position where the latent is activated most strongly across the whole sequence. 
            The number at the begining of each sequence shows this latent activation value. 
            
            The first bin's upper bound is the highest activation of this latent we found.
            Each bin is showing the top-k samples inside the bin range, instead of showing data uniformly sampled from the bin. So they are usually close to upper bound. 
            
            Color indicates how much the latent is activated in each token position. Hover to see the exact value.
            
            The prev/future context on the left side bar is to adjust the number of tokens shown before/after the underscored token.
               
            The input attribution shows how the activation of the latent at the underscored token can be attributed to previous tokens. 
            In other words, it's only for the peak value in the sequence.
               
            When training crosscoder, the activations are normalized, and the crosscoder is reconstructing the normalized version. 
            "unnormalized decoder" means to multiply decoder vector with the normalizatioin term.
            """)

# max_v = float(list(cache_obj.keys())[0].split(" - ")[1])
max_v = max([float(k.split(" - ")[1]) for k in cache_obj.keys()])
if sel_bin == "All":
    for bin_name, obj_list in cache_obj.items():
        obj_list = obj_list[:num_sample_per_bin]    # prioritize big v
        st.text("Bin:  "+bin_name)
        for str_tokens, score, max_idx, _, attribution in obj_list:
            if not show_attr:
                values = score
                bg_color = "238,75,43"
                normalizer = max_v
            else:
                attribution = list(map(lambda x: abs(x), attribution))  # take abs?
                values = attribution
                bg_color = "40,116,166"
                normalizer = max(max(attribution), 1e-6)
            show_one_sample(str_tokens, values, max_idx, score[max_idx], prev_ctx, futr_ctx, bg_color, normalizer)
        st.divider()
else:
    obj_list = cache_obj[sel_bin][:num_sample_per_bin]    # prioritize big v
    st.text("Bin:  "+sel_bin)
    for str_tokens, score, max_idx, _, attribution in obj_list:
        if not show_attr:
            values = score
            bg_color = "238,75,43"
            normalizer = max_v
        else:
            attribution = list(map(lambda x: abs(x), attribution))  # take abs?
            values = attribution
            bg_color = "40,116,166"
            normalizer = max(max(attribution), 1e-6)
        show_one_sample(str_tokens, values, max_idx, score[max_idx], prev_ctx, futr_ctx, bg_color, normalizer)
    