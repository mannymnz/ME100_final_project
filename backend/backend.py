from flask import Flask, request
from flask_cors import CORS
import json

app = Flask(__name__)

CORS(app, origins=["http://localhost:3000"])

# mimics an actual database. Stores data points on each bottle
database = {
    "bottle_1": [100]
}

@app.route("/")
def hello_world():
    return "<p>water bottle program backend!</p>"

@app.route("/reset_data", methods=["POST"])
def reset_data():
    """
        resets data for a given water bottle name

        body: {
            bottle_name: string
        }
    """
    data = json.loads(request.data.decode('utf-8'))

    name = data["bottle_name"]

    database[name] = [100]

    return f"successfully reset {name}"


@app.route("/upload_data", methods=['POST'])
def upload_data():
    """
        appends data points for a water bottle

        body: {
            bottle_name: String
            data: Array
        }
    """

    data = json.loads(request.data.decode('utf-8'))
    
    name = data["bottle_name"]
    new_data_points = data["data"]

    database[name].extend(new_data_points)

    return f"successfully uploaded {len(new_data_points)} data points to {name}"

@app.route("/get_most_recent", methods=["POST"])
def get_most_recent():
    data = json.loads(request.data.decode('utf-8'))

    bottle_name = data["bottle_name"]

    return str(database[bottle_name][-1])
    


@app.route("/get_data", methods=["GET"])
def get_data():
    """
        gets data from the page

        body: {
            bottle_name: string,
            cursor: integer (default 0)
        }
    """

    data = json.loads(request.data.decode('utf-8'))

    bottle_name = data["bottle_name"]

    cursor = 0
    if "cursor" in data:
        cursor = int(data["cursor"])
        assert cursor >= 0 

    return database[bottle_name][cursor:]


@app.route("/get_database", methods=["GET"])
def get_database():
    return database


if __name__ == "__main__":
    app.run(debug=True)