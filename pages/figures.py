import numpy as np
import os
import streamlit as st
import pickle
import plotly.graph_objects as go
import plotly

# given decoder_vec: [n_latent, n_layers, d_model]
def norm_vs_layer_all_latent(decoder_vec: np.ndarray, latents: list[str]):

    norms = np.linalg.norm(decoder_vec, axis=-1) 
    n_latents, n_layers = norms.shape

    norms = norms / norms.max(axis=1, keepdims=True)

    fig = go.Figure()

    # Add traces for each line with color depending on its index
    colors = plotly.colors.sample_colorscale("Jet", norms.argmax(axis=1)/(n_layers-1)) # Bluered
    for i in range(n_latents):
        fig.add_trace(
            go.Scatter(
                x=list(range(n_layers)),
                y=norms[i],
                mode="lines",
                line=dict(color=colors[i]),
                showlegend=False,
                opacity=0.5,
                name=latents[i],
            )
        )

    # Update layout with color bar
    fig.update_layout(
        xaxis_title="Layer",
        yaxis_title="Latent decoder norm (normalized)",
        height=600,
        coloraxis_colorbar=dict(
            title="Peak Layer",
            tickvals=list(range(0, n_layers))
        )
    )

    st.plotly_chart(fig, use_container_width=True)


root_path = "./latent_acts"

selected_cc = st.sidebar.selectbox("Crosscoder", os.listdir(root_path), index=(0 if "selected_cc" not in st.session_state else os.listdir(root_path).index(st.session_state.selected_cc)))
st.subheader("Crosscoder: "+selected_cc)
cc_path = os.path.join(root_path, selected_cc)

latent_paths = os.listdir(cc_path)

all_decoder_vec = []
for latent_path in latent_paths:
    with open(os.path.join(cc_path, latent_path), "rb") as f:
        decoder_vec = pickle.load(f)["decoder_vec"]
    all_decoder_vec.append(decoder_vec)
all_decoder_vec = np.stack(all_decoder_vec, axis=0)
all_latents = [p[:-4] for p in latent_paths]
norm_vs_layer_all_latent(all_decoder_vec, all_latents)