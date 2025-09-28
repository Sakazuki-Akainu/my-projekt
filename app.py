import pandas as pd
import plotly.express as px
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    table_html = None
    graph_html = None

    if request.method == "POST":
        file = request.files.get("file")
        if file:
            df = pd.read_csv(file)

            # Preview table
            table_html = df.head().to_html(classes="table table-striped", index=False)

            # Interactive Plotly bar chart (animated if "Subject" column exists)
            if "Subject" in df.columns:
                fig = px.bar(
                    df,
                    x="Student",
                    y="Marks",
                    color="Marks",
                    animation_frame="Subject",
                    hover_data=df.columns,
                    title="Student Marks per Subject"
                )
            else:
                fig = px.bar(
                    df,
                    x=df.columns[0],
                    y=df.columns[1],
                    color=df.columns[1],
                    hover_data=df.columns,
                    title=f"{df.columns[1]} vs {df.columns[0]}"
                )

            fig.update_layout(
                template="plotly_dark",
                transition_duration=500
            )

            graph_html = fig.to_html(full_html=False)

    return render_template("upload.html", table_html=table_html, graph_html=graph_html)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Render fix
    app.run(host="0.0.0.0", port=port, debug=True)
