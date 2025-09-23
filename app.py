from flask import Flask, render_template, request, send_file
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if not file:
            return "No file uploaded", 400
        
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        df = pd.read_csv(filepath)

        # Generate multiple graphs
        graphs = []
        numeric_cols = df.select_dtypes(include=["number"]).columns

        if len(numeric_cols) >= 2:
            col1, col2 = numeric_cols[0], numeric_cols[1]

            # Bar Chart
            fig1 = px.bar(df, x=col1, y=col2, title=f"Bar Chart of {col1} vs {col2}")
            graphs.append(pio.to_html(fig1, full_html=False))

            # Line Chart
            fig2 = px.line(df, x=col1, y=col2, title=f"Line Chart of {col1} vs {col2}")
            graphs.append(pio.to_html(fig2, full_html=False))

            # Scatter Chart
            fig3 = px.scatter(df, x=col1, y=col2, title=f"Scatter Plot of {col1} vs {col2}")
            graphs.append(pio.to_html(fig3, full_html=False))

            # Histogram (of col1)
            fig4 = px.histogram(df, x=col1, title=f"Histogram of {col1}")
            graphs.append(pio.to_html(fig4, full_html=False))

        return render_template("results.html", tables=[df.head().to_html(classes="data")], graphs=graphs, filename=file.filename)

    return render_template("upload.html")
