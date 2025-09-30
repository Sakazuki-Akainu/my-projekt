import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, render_template, request, redirect, url_for
import io
import json

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

            # Clean DataFrame for JSON (replace NaN with null)
            df = df.replace({pd.NA: None})
            df_json = df.to_json(orient='records')

            # Auto-detect and generate initial graphs
            graphs = []

            numeric_cols = df.select_dtypes(include='number').columns
            categorical_cols = df.select_dtypes(include='object').columns

            # Initial Bar (categorical x, numeric y)
            if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                x_col, y_col = categorical_cols[0], numeric_cols[0]
                frames = []
                for i in range(len(df) + 1):
                    y_values = df[y_col][:i].tolist() + [0] * (len(df) - i)
                    max_val = max(y_values) if max(y_values) > 0 else 1e-10
                    colors = [f'rgb({int(255*(v/max_val))},{int(255*(1-v/max_val))},128)' if isinstance(v, (int, float)) else '#888888' for v in y_values]
                    frames.append(go.Frame(data=[go.Bar(x=df[x_col], y=y_values, marker=dict(color=colors))], name=f'frame{i}'))
                fig_bar = go.Figure(data=[go.Bar(x=df[x_col], y=[0]*len(df), marker=dict(color=['#888888']*len(df)))], frames=frames)
                fig_bar.update_layout(title=f"{y_col} vs {x_col}", xaxis_title=x_col, yaxis_title=y_col, yaxis_range=[0, df[y_col].max() * 1.1])
                fig_bar.update_layout(updatemenus=[dict(type="buttons", buttons=[dict(label="Play", method="animate", args=[None, {"frame": {"duration": 300}, "transition": {"duration": 200}, "fromcurrent": True, "mode": "immediate"}])])])
                graphs.append((fig_bar.to_html(full_html=False), "Bar Chart"))

            # Initial Donut (categorical distribution)
            if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                fig_donut = px.pie(df, names=categorical_cols[0], values=numeric_cols[0], hole=0.3, title="Donut Distribution")
                fig_donut.update_layout(updatemenus=[dict(type="buttons", buttons=[dict(label="Play", method="animate", args=[None, {"frame": {"duration": 500}, "transition": {"duration": 300}, "fromcurrent": True, "mode": "immediate"}])])])
                graphs.append((fig_donut.to_html(full_html=False), "Donut Chart"))

            return render_template("results.html", graphs=graphs, df_json=df_json)

    return render_template("upload.html")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
