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

            # Generate multiple graphs with animations
            graphs = []

            # Basic Bar with Lift-Up Animation
            if len(df.columns) >= 2:
                x_col, y_col = df.columns[0], df.columns[1]
                # Create frames for animation (start at 0, animate to real values)
                frames = [go.Frame(data=[go.Bar(x=df[x_col], y=[0] * len(df))], name='frame0')]
                bar_data = go.Bar(x=df[x_col], y=df[y_col], marker_color=df[y_col], name='frame1')
                frames.append(go.Frame(data=[bar_data], name='frame1'))
                fig_bar = go.Figure(data=[bar_data], frames=frames,
                                  layout=go.Layout(
                                      title=f"{y_col} vs {x_col}",
                                      xaxis=dict(title=x_col),
                                      yaxis=dict(title=y_col, range=[0, df[y_col].max() * 1.1]),
                                      updatemenus=[dict(
                                          type="buttons",
                                          buttons=[dict(label="Play",
                                                        method="animate",
                                                        args=[None, {"frame": {"duration": 1000, "redraw": True}}])]
                                      )]))
                fig_bar.update_layout(transition_duration=500)
                graphs.append((fig_bar.to_html(full_html=False), "Bar Chart: Basic Overview"))

            # Donut Chart with Fill Animation
            if len(df) <= 10:  # Small data for pie
                fig_donut = px.pie(df, names=df.columns[0], values=df.columns[1], hole=0.3, title="Donut Distribution")
                # Convert to Graph Objects for animation
                donut_data = [go.Pie(labels=df[df.columns[0]], values=[0] * len(df), hole=0.3, name='frame0')]
                for i in range(len(df)):
                    donut_data.append(go.Pie(labels=df[df.columns[0]], values=[df.iloc[i, 1] if j == i else 0 for j in range(len(df))], hole=0.3, name=f'frame{i+1}'))
                frames = [go.Frame(data=[donut_data[0]], name='frame0')]
                for i in range(1, len(donut_data)):
                    frames.append(go.Frame(data=[donut_data[i]], name=f'frame{i}'))
                fig_donut = go.Figure(data=donut_data[0:1], frames=frames,
                                    layout=go.Layout(title="Donut Distribution"))
                fig_donut.update_layout(updatemenus=[dict(
                    type="buttons",
                    buttons=[dict(label="Play",
                                  method="animate",
                                  args=[None, {"frame": {"duration": 800, "redraw": True}, "transition": {"duration": 500}}])]
                )])
                graphs.append((fig_donut.to_html(full_html=False), "Donut Chart: 3 Parts Style"))

            # Sleep Tracker Bar with Lift-Up Animation
            if 'Duration' in df.columns or 'Marks' in df.columns:
                y_col = 'Duration' if 'Duration' in df.columns else 'Marks'
                frames = [go.Frame(data=[go.Bar(y=df[df.columns[0]], x=[0] * len(df), orientation='h')], name='frame0')]
                bar_data = go.Bar(y=df[df.columns[0]], x=df[y_col], orientation='h', marker_color=df[y_col], name='frame1')
                frames.append(go.Frame(data=[bar_data], name='frame1'))
                fig_sleep = go.Figure(data=[bar_data], frames=frames,
                                    layout=go.Layout(
                                        title="Bar Chart: Sleep Tracker Style",
                                        xaxis=dict(title="Hours" if 'Duration' in df.columns else y_col),
                                        yaxis=dict(title=df.columns[0]),
                                        updatemenus=[dict(
                                            type="buttons",
                                            buttons=[dict(label="Play",
                                                          method="animate",
                                                          args=[None, {"frame": {"duration": 1000, "redraw": True}}])]
                                        )]))
                fig_sleep.update_layout(transition_duration=500)
                graphs.append((fig_sleep.to_html(full_html=False), "Bar Chart: Sleep Tracker"))

            # Multiple Bar Chart (grouped, if multi-numeric cols)
            if len(df.select_dtypes(include='number').columns) > 1:
                fig_multi = px.bar(df.melt(id_vars=df.columns[0]), x=df.columns[0], y='value', color='variable',
                                   barmode='group', title="Multiple Bar Chart")
                fig_multi.update_layout(transition_duration=300)
                graphs.append((fig_multi.to_html(full_html=False), "Multiple Bar Chart"))

            # Morph Line to Radar (advanced animation with frames)
            if len(df.columns) >= 3:
                frame1 = go.Frame(data=[go.Scatter(x=df.iloc[:,0], y=df.iloc[:,1], mode='lines')],
                                 layout=go.Layout(title_text="Line Chart"))
                frame2 = go.Frame(data=[go.Scatterpolar(r=df.iloc[:,1], theta=df.iloc[:,0], fill='toself')],
                                 layout=go.Layout(title_text="Radar Chart", polar=dict(radialaxis=dict(visible=True))))
                fig_morph = go.Figure(data=frame1.data, layout=frame1.layout,
                                      frames=[frame1, frame2])
                fig_morph.update_layout(updatemenus=[dict(type="buttons", buttons=[dict(label="Play",
                                     method="animate", args=[None, {"frame": {"duration": 1000}}])])])
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
