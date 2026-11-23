"""
Cynbit AI - Plotly Visualization Helpers
Theme-matched interactive charts with dark navy aesthetics.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, List

# Cynbit Color Palette
CYNBIT_NAVY = "#0B132B"
CYNBIT_SLATE = "#1C2541"
CYNBIT_CYAN = "#48CAE4"
CYNBIT_BLUE = "#0077B6"
HOT_COLOR = "#EF476F"
WARM_COLOR = "#FFB703"
COLD_COLOR = "#8D99AE"

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#F8F9FA", size=12),
    margin=dict(l=20, r=20, t=35, b=20)
)

def create_priority_donut(priority_counts: Dict[str, int]) -> go.Figure:
    """Creates a donut chart for lead priority distribution."""
    labels = ["Hot", "Warm", "Cold"]
    values = [priority_counts.get(k, 0) for k in labels]
    colors = [HOT_COLOR, WARM_COLOR, COLD_COLOR]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors, line=dict(color="#0B132B", width=2)),
        textinfo="label+percent",
        textfont=dict(size=13, color="#FFFFFF"),
        hoverinfo="label+value+percent"
    )])
    
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        showlegend=False,
        annotations=[dict(
            text="PRIORITY",
            x=0.5, y=0.5,
            font_size=13,
            font_weight="bold",
            font_color="#8D99AE",
            showarrow=False
        )]
    )
    return fig

def create_category_bar(category_counts: Dict[str, int]) -> go.Figure:
    """Creates a horizontal bar chart of lead service categories."""
    df = pd.DataFrame(list(category_counts.items()), columns=["Category", "Count"])
    df = df.sort_values(by="Count", ascending=True)
    
    fig = go.Figure(go.Bar(
        x=df["Count"],
        y=df["Category"],
        orientation="h",
        marker=dict(
            color=df["Count"],
            colorscale=[[0, "#0077B6"], [1, "#48CAE4"]],
            line=dict(color="#0B132B", width=1)
        ),
        text=df["Count"],
        textposition="outside",
        textfont=dict(color="#FFFFFF", weight="bold")
    ))
    
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False),
        yaxis=dict(showgrid=False)
    )
    return fig

def create_conversion_funnel(funnel_data: List[Dict[str, Any]]) -> go.Figure:
    """Creates a CRM conversion funnel chart."""
    stages = [d["stage"] for d in funnel_data]
    counts = [d["cumulative_count"] for d in funnel_data]
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=counts,
        textinfo="value+percent initial",
        marker=dict(
            color=["#3A86FF", "#0096C7", "#00B4D8", "#48CAE4", "#90E0EF", "#06D6A0"],
            line=dict(color="#0B132B", width=2)
        ),
        connector=dict(line=dict(color="rgba(72, 202, 228, 0.4)", width=1))
    ))
    
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        funnelmode="stack"
    )
    return fig

def create_confusion_matrix_heatmap(labels: List[str], matrix: List[List[int]]) -> go.Figure:
    """Creates a confusion matrix heatmap for model evaluation."""
    # Shorten labels if necessary for clean rendering
    short_labels = [l.replace(" Development", "").replace("Business ", "") for l in labels]
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=short_labels,
        y=short_labels,
        colorscale="Blues",
        text=matrix,
        texttemplate="%{text}",
        textfont={"size": 14, "color": "#FFFFFF"},
        hoverongaps=False
    ))
    
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis_title="Predicted Label",
        yaxis_title="True Label",
        xaxis=dict(side="bottom"),
        yaxis=dict(autorange="reversed")
    )
    return fig

def create_score_breakdown_bar(breakdown: Dict[str, Any]) -> go.Figure:
    """Renders horizontal score contributor breakdown for a single lead."""
    factors = []
    scores = []
    max_scores = []
    
    labels_map = {
        "budget": "Budget Value",
        "urgency": "Project Urgency",
        "requirements": "Requirements Clarity",
        "timeline": "Timeline Alignment",
        "relevance": "Cynbit Relevance"
    }
    
    for k, v in breakdown.items():
        factors.append(labels_map.get(k, k.capitalize()))
        scores.append(v["score"])
        max_scores.append(v["max"])
        
    fig = go.Figure()
    # Background full bars
    fig.add_trace(go.Bar(
        y=factors,
        x=max_scores,
        orientation="h",
        name="Maximum",
        marker=dict(color="rgba(255, 255, 255, 0.08)")
    ))
    # Earned score bars
    fig.add_trace(go.Bar(
        y=factors,
        x=scores,
        orientation="h",
        name="Earned Points",
        marker=dict(color="#48CAE4"),
        text=[f"{s}/{m} pts" for s, m in zip(scores, max_scores)],
        textposition="inside",
        textfont=dict(color="#0B132B", weight="bold")
    ))
    
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        barmode="overlay",
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False)
    )
    return fig
