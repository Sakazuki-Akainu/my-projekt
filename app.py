import os
import pandas as pd
import plotly.express as px
from flask import Flask, render_template, request

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

            df = df.replace({pd.NA: None})
            df_json = df.to_json(orient='records')

            graphs = []
            numeric_cols = df.select_dtypes(include='number').columns
            categorical_cols = df.select_dtypes(include='object').columns

            if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                fig_bar = px.bar(df, x=categorical_cols[0], y=numeric_cols[0], title="Bar Chart")
                graphs.append((fig_bar.to_html(full_html=False), "Bar Chart"))

            if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                fig_donut = px.pie(df, names=categorical_cols[0], values=numeric_cols[0], hole=0.3, title="Donut Distribution")
                graphs.append((fig_donut.to_html(full_html=False), "Donut Chart"))

            return render_template("results.html", graphs=graphs, df_json=df_json)

    return render_template("upload.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT
    app.run(host="0.0.0.0", port=port, debug=True)
