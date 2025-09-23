from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px

app = Flask(__name__)
df = None  # Global to hold uploaded dataframe


@app.route("/", methods=["GET", "POST"])
def upload_file():
    global df
    graph_html = None
    stats_html = None
    tables = None
    columns = []

    if request.method == "POST":
        if "file" in request.files:  # Handle file upload
            file = request.files["file"]
            if file.filename.endswith(".csv"):
                df = pd.read_csv(file)
                tables = [df.head().to_html(classes="table table-bordered table-striped", index=False)]
                columns = df.columns.tolist()

        elif df is not None:  # Handle graph generation
            x_column = request.form.get("x_column")
            y_column = request.form.get("y_column")
            chart_type = request.form.get("chart_type")

            if x_column and y_column:
                if chart_type == "line":
                    fig = px.line(df, x=x_column, y=y_column, title="Line Chart")
                elif chart_type == "bar":
                    fig = px.bar(df, x=x_column, y=y_column, title="Bar Chart")
                elif chart_type == "scatter":
                    fig = px.scatter(df, x=x_column, y=y_column, title="Scatter Plot")
                elif chart_type == "pie":
                    fig = px.pie(df, names=x_column, values=y_column, title="Pie Chart")

                graph_html = fig.to_html(full_html=False)

            stats_html = df.describe().to_html(classes="table table-bordered table-hover")

    return render_template(
        "upload.html",
        tables=tables,
        columns=columns,
        graph_html=graph_html,
        stats=stats_html,
    )


if __name__ == "__main__":
    app.run(debug=True)
