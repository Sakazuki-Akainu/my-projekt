from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    if file:
        filename = file.filename

        # Read file (CSV or Excel)
        if filename.endswith(".csv"):
            df = pd.read_csv(file)
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            return "Only CSV or Excel files are supported!"

        # Calculate stats
        average = round(df["Marks"].mean(), 2)
        highest = df["Marks"].max()
        lowest = df["Marks"].min()
        count = df["Marks"].count()

        # Plot interactive graph
        fig = px.bar(df, x="Name", y="Marks", title=f"Student Marks (Avg: {average})")
        graph_html = fig.to_html(full_html=False)

        # Send data + graph to results.html
        return render_template("results.html",
                               count=count,
                               average=average,
                               highest=highest,
                               lowest=lowest,
                               graph_html=graph_html)
    return "No file uploaded"

if __name__ == "__main__":
    app.run(debug=True)
