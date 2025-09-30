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

            # Generate multiple graphs
            graphs = []

            # Basic Bar (like your original)
            if len(df.columns) >= 2:
                x_col, y_col = df.columns[0], df.columns[1]
                fig_bar = px.bar(df, x=x_col, y=y_col, color=y_col, title=f"{y_col} vs {x_col}")
                fig_bar.update_layout(transition_duration=300)
                graphs.append((fig_bar.to_html(full_html=False), "Bar Chart: Basic Overview"))

            # Donut Chart (if categorical/numeric, like 3 parts in image)
            if len(df) <= 10:  # Small data for pie
                fig_donut = px.pie(df, names=df.columns[0], values=df.columns[1], hole=0.3, title="Donut Distribution")
                fig_donut.update_layout(transition_duration=300)
                graphs.append((fig_donut.to_html(full_html=False), "Donut Chart: 3 Parts Style"))

            # Sleep Tracker Bar (assume 'Duration' col; horizontal for timeline)
            if 'Duration' in df.columns or 'Marks' in df.columns:  # Adapt 'Marks' as duration
                y_col = 'Duration' if 'Duration' in df.columns else 'Marks'
                fig_sleep = px.bar(df, y=df.columns[0], x=y_col, orientation='h', color=y_col,
                                   title="Bar Chart: Sleep Tracker Style")
                fig_sleep.update_layout(transition_duration=300, xaxis_title="Hours")
                graphs.append((fig_sleep.to_html(full_html=False), "Bar Chart: Sleep Tracker"))

            # Multiple Bar Chart (grouped, if multi-numeric cols)
            if len(df.select_dtypes(include='number').columns) > 1:
                fig_multi = px.bar(df.melt(id_vars=df.columns[0]), x=df.columns[0], y='value', color='variable',
                                   barmode='group', title="Multiple Bar Chart")
                fig_multi.update_layout(transition_duration=300)
                graphs.append((fig_multi.to_html(full_html=False), "Multiple Bar Chart"))

            # Morph Line to Radar (advanced animation with frames)
            if len(df.columns) >= 3:  # Need categories for radar
                # Line frame
                frame1 = go.Frame(data=[go.Scatter(x=df.iloc[:,0], y=df.iloc[:,1], mode='lines')],
                                 layout=go.Layout(title_text="Line Chart"))
                # Radar frame
                frame2 = go.Frame(data=[go.Scatterpolar(r=df.iloc[:,1], theta=df.iloc[:,0], fill='toself')],
                                 layout=go.Layout(title_text="Radar Chart", polar=dict(radialaxis=dict(visible=True))))
                fig_morph = go.Figure(data=frame1.data, layout=frame1.layout,
                                      frames=[frame1, frame2])
                fig_morph.update_layout(updatemenus=[dict(type="buttons", buttons=[dict(label="Play",
                                     method="animate", args=[None, {"frame": {"duration": 1000}}])])])
                graphs.append((fig_morph.to_html(full_html=False), "Morph: Line to Radar Chart"))

            return render_template("results.html", graphs=graphs)

    return render_template("upload.html")  # Or your original form

@app.route("/download_graph")
def download_graph():
    # TODO: Use session to store figs, then fig.write_image(io.BytesIO()), return send_file
    return "Download coming soon!"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
