import pandas as pd
import plotly.express as px
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    table_html = None
    graph_html = None
    stats_html = None

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

            # Preview table
            table_html = df.head().to_html(classes="table table-striped", index=False)

            # Stats
            stats_html = df.describe().to_html()

            # Graph creation based on form input
            graph_type = request.form.get('graph_type', 'Bar')
            x_col = request.form.get('x_axis', df.columns[0])
            y_col = request.form.get('y_axis', df.columns[1])

            if graph_type == 'Line':
                fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
            elif graph_type == 'Scatter':
                fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
            elif graph_type == 'Pie':
                fig = px.pie(df, names=x_col, values=y_col, title=f"{y_col} Distribution")
            else:  # Bar
                fig = px.bar(df, x=x_col, y=y_col, color=y_col, title=f"{y_col} vs {x_col}")

            # Animation and hover effects
            fig.update_layout(
                hovermode='closest',
                transition={'duration': 300, 'easing': 'cubic-in-out'},
                template='plotly_white'
            )
            fig.update_traces(hovertemplate='%{x}: %{y}', marker_line_width=1)

            graph_html = fig.to_html(full_html=False)

    return render_template("upload.html", table_html=table_html, graph_html=graph_html, stats_html=stats_html)

@app.route("/download_graph")
def download_graph():
    # Placeholder - implement session or temp file storage
    return "Download not implemented yet"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
