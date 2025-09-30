import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, render_template, request, redirect, url_for
import io  # For temp downloads

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            filename = file.filename
            if filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                return "Unsupported file type!"

            # Generate multiple graphs with animations and auto-play
            graphs = []

            # Basic Bar with Lift-Up Animation and Auto-Play
            if len(df.columns) >= 2:
                x_col, y_col = df.columns[0], df.columns[1]
                frames = []
                for i in range(len(df) + 1):
                    y_values = df[y_col][:i].tolist() + [0] * (len(df) - i)
                    # Use a colorscale based on y_values if numeric, else default color
                    colors = [f'rgb({int(255*(v/max(y_values, default=1)))},{int(255*(1-v/max(y_values, default=1)))},128)' if pd.to_numeric(v, errors='coerce') == v else '#888888' for v in y_values]
                    frames.append(go.Frame(data=[go.Bar(x=df[x_col], y=y_values, marker=dict(color=colors))], name=f'frame{i}'))
                fig_bar = go.Figure(data=[go.Bar(x=df[x_col], y=[0]*len(df), marker=dict(color=['#888888']*len(df)))], frames=frames)
                fig_bar.update_layout(
                    title=f"{y_col} vs {x_col}",
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    yaxis_range=[0, df[y_col].max() * 1.1 if pd.api.types.is_numeric_dtype(df[y_col]) else 100],
                    updatemenus=[dict(
                        type="buttons",
                        buttons=[dict(
                            label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 300, "redraw": True}, "transition": {"duration": 200}, "fromcurrent": True, "mode": "immediate"}]
                        )]
                    )]
                )
                graphs.append((fig_bar.to_html(full_html=False), "Bar Chart: Basic Overview"))

            # Donut Chart with Sequential Fill Animation and Auto-Play
            if len(df) <= 10:
                frames = []
                cumulative_values = [0] * len(df)
                for i in range(len(df) + 1):
                    if i > 0:
                        cumulative_values[i-1] = df.iloc[i-1, 1] if pd.api.types.is_numeric_dtype(df.iloc[:, 1]) else 1
                    frames.append(go.Frame(data=[go.Pie(labels=df[df.columns[0]], values=cumulative_values, hole=0.3)], name=f'frame{i}'))
                fig_donut = go.Figure(data=[go.Pie(labels=df[df.columns[0]], values=[0]*len(df), hole=0.3)], frames=frames)
                fig_donut.update_layout(
                    title="Donut Distribution",
                    updatemenus=[dict(
                        type="buttons",
                        buttons=[dict(
                            label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 500, "redraw": True}, "transition": {"duration": 300}, "fromcurrent": True, "mode": "immediate"}]
                        )]
                    )]
                )
                graphs.append((fig_donut.to_html(full_html=False), "Donut Chart: 3 Parts Style"))

            # Sleep Tracker Bar with Lift-Up Animation and Auto-Play
            if 'Duration' in df.columns or 'Marks' in df.columns:
                y_col = 'Duration' if 'Duration' in df.columns else 'Marks'
                frames = []
                for i in range(len(df) + 1):
                    x_values = df[y_col][:i].tolist() + [0] * (len(df) - i)
                    # Use a colorscale based on x_values if numeric, else default color
                    colors = [f'rgb({int(255*(v/max(x_values, default=1)))},{int(255*(1-v/max(x_values, default=1)))},128)' if pd.to_numeric(v, errors='coerce') == v else '#888888' for v in x_values]
                    frames.append(go.Frame(data=[go.Bar(y=df[df.columns[0]], x=x_values, orientation='h', marker=dict(color=colors))], name=f'frame{i}'))
                fig_sleep = go.Figure(data=[go.Bar(y=df[df.columns[0]], x=[0]*len(df), orientation='h', marker=dict(color=['#888888']*len(df)))], frames=frames)
                fig_sleep.update_layout(
                    title="Bar Chart: Sleep Tracker Style",
                    xaxis_title="Hours" if 'Duration' in df.columns else y_col,
                    yaxis_title=df.columns[0],
                    xaxis_range=[0, df[y_col].max() * 1.1 if pd.api.types.is_numeric_dtype(df[y_col]) else 100],
                    updatemenus=[dict(
                        type="buttons",
                        buttons=[dict(
                            label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 300, "redraw": True}, "transition": {"duration": 200}, "fromcurrent": True, "mode": "immediate"}]
                        )]
                    )]
                )
                graphs.append((fig_sleep.to_html(full_html=False), "Bar Chart: Sleep Tracker"))

            # Multiple Bar Chart with Lift-Up Animation and Auto-Play
            if len(df.select_dtypes(include='number').columns) > 1:
                melted = df.melt(id_vars=df.columns[0], var_name='variable', value_name='value')
                unique_vars = melted['variable'].unique()
                frames = []
                for i in range(len(melted) + 1):
                    partial_df = melted.iloc[:i]
                    data = [go.Bar(x=partial_df[partial_df['variable'] == var][df.columns[0]], y=partial_df[partial_df['variable'] == var]['value'], name=var, marker=dict(color='blue')) for var in unique_vars]
                    frames.append(go.Frame(data=data, name=f'frame{i}'))
                fig_multi = go.Figure(data=[], frames=frames)
                fig_multi.update_layout(
                    title="Multiple Bar Chart",
                    barmode='group',
                    updatemenus=[dict(
                        type="buttons",
                        buttons=[dict(
                            label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 200, "redraw": True}, "transition": {"duration": 100}, "fromcurrent": True, "mode": "immediate"}]
                        )]
                    )]
                )
                graphs.append((fig_multi.to_html(full_html=False), "Multiple Bar Chart"))

            # Line Chart with Point-by-Point Animation and Auto-Play
            if len(df.columns) >= 2:
                x_col, y_col = df.columns[0], df.columns[1]
                frames = []
                for i in range(len(df) + 1):
                    frames.append(go.Frame(data=[go.Scatter(x=df[x_col][:i], y=df[y_col][:i], mode='lines+markers')], name=f'frame{i}'))
                fig_line = go.Figure(data=[go.Scatter(x=[], y=[], mode='lines+markers')], frames=frames)
                fig_line.update_layout(
                    title=f"Line: {y_col} vs {x_col}",
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    updatemenus=[dict(
                        type="buttons",
                        buttons=[dict(
                            label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 300, "redraw": True}, "transition": {"duration": 200}, "fromcurrent": True, "mode": "immediate"}]
                        )]
                    )]
                )
                graphs.append((fig_line.to_html(full_html=False), "Line Chart: Point by Point"))

            # Scatter Chart with Pop-In Animation and Auto-Play
            if len(df.columns) >= 2:
                x_col, y_col = df.columns[0], df.columns[1]
                frames = []
                for i in range(len(df) + 1):
                    frames.append(go.Frame(data=[go.Scatter(x=df[x_col][:i], y=df[y_col][:i], mode='markers')], name=f'frame{i}'))
                fig_scatter = go.Figure(data=[go.Scatter(x=[], y=[], mode='markers')], frames=frames)
                fig_scatter.update_layout(
                    title=f"Scatter: {y_col} vs {x_col}",
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    updatemenus=[dict(
                        type="buttons",
                        buttons=[dict(
                            label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 300, "redraw": True}, "transition": {"duration": 200}, "fromcurrent": True, "mode": "immediate"}]
                        )]
                    )]
                )
                graphs.append((fig_scatter.to_html(full_html=False), "Scatter Chart: Pop Dots"))

            # Morph Line to Radar with Enhanced Transition and Auto-Play
            if len(df.columns) >= 3:
                frame1 = go.Frame(data=[go.Scatter(x=df.iloc[:,0], y=df.iloc[:,1], mode='lines')],
                                 layout=go.Layout(title_text="Line Chart"))
                frame2 = go.Frame(data=[go.Scatterpolar(r=df.iloc[:,1], theta=df.iloc[:,0], fill='toself')],
                                 layout=go.Layout(title_text="Radar Chart", polar=dict(radialaxis=dict(visible=True))))
                fig_morph = go.Figure(data=frame1.data, layout=frame1.layout, frames=[frame1, frame2])
                fig_morph.update_layout(
                    transition_duration=500,
                    updatemenus=[dict(
                        type="buttons",
                        buttons=[dict(
                            label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 1000, "redraw": True}, "transition": {"duration": 500}, "fromcurrent": True, "mode": "immediate"}]
                        )]
                    )]
                )
                graphs.append((fig_morph.to_html(full_html=False), "Morph: Line to Radar Chart"))

            return render_template("results.html", graphs=graphs)

    return render_template("upload.html")

@app.route("/download_graph")
def download_graph():
    return "Download coming soon!"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
