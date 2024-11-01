import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def show_figures_per_latent(decoder_vec: np.ndarray):
    # n_layers, d_model
    n_layers, d_model = decoder_vec.shape

    # norm
    norms = np.linalg.norm(decoder_vec, axis=-1)

    # cos sim
    max_idx = norms.argmax()
    peak_vec = decoder_vec[max_idx]
    cos_sim = (decoder_vec * peak_vec[None, :]).sum(axis=1) / (norms * norms[max_idx])

    # projection
    projected = (decoder_vec[None, :, :] * decoder_vec[:, None, :]).sum(axis=-1) / norms[None, :]

    fig = make_subplots(rows=1, cols=3, column_widths=[0.375, 0.375, 0.25], subplot_titles=("Decoder vec norm magnitude", "Cosine sim of dec vec to peak", "Projection"))

    fig.add_trace(go.Scatter(x=list(range(n_layers)), y=norms, mode='lines+markers', showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=list(range(n_layers)), y=cos_sim, mode='lines+markers', showlegend=False), row=1, col=2)
    fig.add_trace(go.Heatmap(z=projected, coloraxis="coloraxis"), row=1, col=3)

    # Update layout for titles and spacing
    fig.update_layout(
        height=350, width=900,
        coloraxis={'colorscale': 'Viridis'}, 
    )

    cossim_min_y = min(0, cos_sim.min()-0.05)
    cossim_max_y = 1+0.1
    fig.update_yaxes(range=[cossim_min_y, cossim_max_y], row=1, col=2)  # Extend range a bit above max for clarity
    fig.update_yaxes(range=[0, norms.max()+0.05], row=1, col=1)  # Extend range a bit above max for clarity

    fig.add_shape(
        type="line",
        x0=max_idx, x1=max_idx,  
        y0=cossim_min_y, y1=1, 
        xref="x2", yref="y2",  # Reference for the second subplot
        line=dict(color="Red", width=2, dash="dash")
    )

    fig.add_annotation(
        x=max_idx,  # Position of the label on the x-axis
        y=cossim_min_y,  # Position of the label on the y-axis (adjusted to be within the plot)
        text="Peak",  # Text label
        showarrow=False,        # Show arrow pointing to the line
        xref="x2", yref="y2"  # Reference for the second subplot
    )

    fig.update_xaxes(title_text="Onto decoder direction in this layer", title_font=dict(size=12), title_standoff=5, row=1, col=3)  # X-axis label for heatmap
    fig.update_yaxes(title_text="Project of decoder vector in this layer", title_font=dict(size=12), title_standoff=5, row=1, col=3)  # Y-axis label for heatmap
    fig.update_yaxes(autorange="reversed", row=1, col=3)
    
  
    st.plotly_chart(fig)