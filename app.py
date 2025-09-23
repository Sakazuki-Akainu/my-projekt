from flask import Flask, render_template, request, session
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for session

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    df = None

    if request.method == "POST":
        # Case 1: File upload
        if "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Save file path in session
            session["uploaded_file"] = filepath

            df = pd.read_csv(filepath)

            return render_template(
                "upload.html",
                tables=[df.head().to_html(classes="table table-striped", index=False)],
                columns=df.columns,
                graph_html=None,
                stats=None
            )

        # Case 2: Column selection form
        elif "x_column" in request.form and "y_column" in request.form:
            filepath = session.get("uploaded_file")
            if not filepath:
                return "Error: No file uploaded yet!"

            df = pd.read_csv(filepath)
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
            stats = df.describe().to_html(classes="table table-bordered")

            return render_template(
                "upload.html",
                tables=[df.head().to_html(classes="table table-striped", index=False)],
                columns=df.columns,
                graph_html=graph_html,
                stats=stats
            )

    return render_template("upload.html", tables=None, columns=None, graph_html=None, stats=None)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
