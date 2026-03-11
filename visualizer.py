import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def generate_chart(df: pd.DataFrame, user_question: str):
    """
    Automatically pick the best chart type based on the data shape.
    Returns a Plotly figure or None.
    """
    if df is None or df.empty or len(df.columns) < 2:
        return None

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    text_cols = df.select_dtypes(exclude='number').columns.tolist()

    if not numeric_cols:
        return None

    q = user_question.lower()
    num_col = numeric_cols[0]
    label_col = text_cols[0] if text_cols else df.columns[0]

    # Time series detection
    date_cols = [c for c in df.columns if any(
        word in c.lower() for word in ['date', 'month', 'year', 'day']
    )]

    try:
        if date_cols and len(numeric_cols) >= 1:
            fig = px.line(
                df,
                x=date_cols[0],
                y=num_col,
                title=user_question.capitalize(),
                markers=True
            )

        elif any(word in q for word in ['top', 'most', 'highest', 'best', 'rank']):
            fig = px.bar(
                df,
                x=label_col,
                y=num_col,
                title=user_question.capitalize(),
                color=num_col,
                color_continuous_scale='Blues'
            )

        elif any(word in q for word in ['distribution', 'breakdown', 'percentage', 'share', 'sector']):
            fig = px.pie(
                df,
                names=label_col,
                values=num_col,
                title=user_question.capitalize()
            )

        elif len(df) <= 15 and text_cols:
            fig = px.bar(
                df,
                x=label_col,
                y=num_col,
                title=user_question.capitalize(),
                color=num_col,
                color_continuous_scale='Teal'
            )

        else:
            fig = px.scatter(
                df,
                x=df.columns[0],
                y=num_col,
                title=user_question.capitalize()
            )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font_size=14
        )
        return fig

    except Exception:
        return None