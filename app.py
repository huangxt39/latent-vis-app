import streamlit as st
import pickle
import os
import random

st.set_page_config(layout="wide")


def span_maker(token: str, color_value: float, norm_term: float):
    # bg_color = "40,116,166"
    bg_color = "238,75,43"
    if color_value/norm_term > 0.6:
        txt_color = "white"
    else:
        txt_color = "black"
    hover_text = 'title="%.3f"'%color_value
    
    return '<span style="background-color:rgba(%s,%.2f); color: %s" %s>'%(bg_color, color_value/norm_term, txt_color, hover_text) + token + '</span>' 

def click_random(examples):
    st.session_state.sel_example_idx = random.randint(0, len(examples)-1)


root_path = "./organized"

examples = os.listdir(root_path)
examples = [file.rstrip(".pkl") for file in examples]

if ("sel_example_idx" not in st.session_state):
    st.session_state.sel_example_idx = random.randint(0, len(examples)-1)
st.session_state.sel_example = st.sidebar.selectbox("select a latent", examples, index=st.session_state.sel_example_idx)

st.sidebar.button("random example", type="primary", on_click=click_random, args=(examples,))


with open(os.path.join(root_path, st.session_state.sel_example+".pkl"), "rb") as f:
    cache_obj = pickle.load(f)  # ordereddict

with st.sidebar:
    # only_prev = st.toggle("only prev", value=False)
    # 5 25 No restriction
    prev_ctx = st.select_slider("# prev context", ["5", "25", "inf"], value="inf")
    futr_ctx = st.select_slider("# future context", ["5", "25", "inf"], value="5")

    sel_bin = st.radio("bin", ["All",] + list(cache_obj.keys()), index=0)
    num_sample_per_bin = st.slider("#sample", 1, 100, 10 if sel_bin == "All" else 100)

max_v = float(list(cache_obj.keys())[0].split(" - ")[1])
if sel_bin == "All":
    for bin_name, obj_list in cache_obj.items():
        obj_list = obj_list[:num_sample_per_bin]    # prioritize big v
        st.text("Bin:  "+bin_name)
        for str_tokens, score, max_idx in obj_list:
            shown_value = f"<span> {score[max_idx]:.3f} ; </span>"
            str_tokens[max_idx] = "<u>" + str_tokens[max_idx] + "</u>"

            length = len(str_tokens)
            s_idx = 0 if prev_ctx == "inf" else max(0, max_idx-int(prev_ctx))
            e_idx = length if futr_ctx == "inf" else min(length, max_idx+int(futr_ctx)+1)
            str_tokens = str_tokens[s_idx:e_idx]
            score = score[s_idx:e_idx]
            
            row = f'<div style="margin-bottom: 8px;">' + shown_value + "".join([span_maker(t, v, max_v) for t, v in zip(str_tokens, score)]) + '</div>'
            st.markdown(row, unsafe_allow_html=True)
        st.divider()
else:
    obj_list = cache_obj[sel_bin][:num_sample_per_bin]    # prioritize big v
    st.text("Bin:  "+sel_bin)
    for str_tokens, score, max_idx in obj_list:
        shown_value = f"<span> {score[max_idx]:.3f} ; </span>"
        str_tokens[max_idx] = "<u>" + str_tokens[max_idx] + "</u>"

        length = len(str_tokens)
        s_idx = 0 if prev_ctx == "inf" else max(0, max_idx-int(prev_ctx))
        e_idx = length if futr_ctx == "inf" else min(length, max_idx+int(futr_ctx)+1)
        str_tokens = str_tokens[s_idx:e_idx]
        score = score[s_idx:e_idx]
        
        row = f'<div style="margin-bottom: 8px;">' + shown_value + "".join([span_maker(t, v, max_v) for t, v in zip(str_tokens, score)]) + '</div>'
        st.markdown(row, unsafe_allow_html=True)

    