from flask import Flask,render_template
from flask_pymongo import PyMongo
import pandas as pd
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/covid"
mongo = PyMongo(app)

@app.route("/")
def index():
    df = pd.read_csv('data.csv').drop('Open', axis=1)
    chart_data = df.to_dict(orient='records')
    chart_data = json.dumps(chart_data, indent=2)
    data = {'chart_data': chart_data}
    covid = mongo.db.state.find()
    print(covid)
    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)