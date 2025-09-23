from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file.filename == "":
            return "No file selected"

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Load CSV into DataFrame
        df = pd.read_csv(filepath)

        # If user chose columns and chart type
        if "x_column" in request.form and "y_column" in request.form:
            x_col = request.form["x_column"]
            y_col = request.form["y_column"]
            chart_type = request.form["chart_type"]

            # Create chart dynamically
            if chart_type == "line":
                fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
            elif chart_type == "bar":
                fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
            elif chart_type == "scatter":
                fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
            elif chart_type == "pie":
                fig = px.pie(df, names=x_col, values=y_col, title=f"{y_col} by {x_col}")
            else:
                fig = None

            graph_html = fig.to_html(full_html=False) if fig else ""

            # Show numeric column stats
            stats = df.describe().to_html(classes="table table-bordered")

            return render_template(
                "upload.html",
                tables=[df.head().to_html(classes="table table-striped", index=False)],
                columns=df.columns,
                graph_html=graph_html,
                stats=stats
            )

        # First upload → just show preview
        return render_template(
            "upload.html",
            tables=[df.head().to_html(classes="table table-striped", index=False)],
            columns=df.columns,
            graph_html=None,
            stats=None
        )

    return render_template("upload.html", tables=None, columns=None, graph_html=None, stats=None)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
