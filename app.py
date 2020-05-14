from flask import Flask,render_template
from flask_pymongo import PyMongo
import pandas as pd
import json
from os import listdir

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/covid"
mongo = PyMongo(app)

@app.route("/")
def index():
    filepaths = [f for f in listdir("C:\\Users\\Akansha\\MyProject\\statedata") if f.endswith('.csv')]
    #print (filepaths)
    #df = pd.concat((pd.read_csv(f) for f in filepaths))
    headers = ['day_of_week', 'avg_retail_and_recreation_percent_change','avg_grocery_and_pharmacy_percent_change', 'avg_parks_percent_change','avg_transit_stations_percent_change','avg_workplaces_percent_change', 'avg_residential_percent_change']
    li = []
    for filename in filepaths:
        df = pd.read_csv("C:\\Users\\Akansha\\MyProject\\statedata\\" + filename, header=0, names = headers)
        li.append(df)
    frame = pd.concat(li, ignore_index=True)
    chart_data = frame.to_dict(orient='records')
    chart_data = json.dumps(chart_data, indent=2)
    data = {'chart_data': chart_data}
    covid = mongo.db.state.find()
    print(covid)
    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)