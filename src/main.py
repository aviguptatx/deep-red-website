from flask import Flask, render_template, request, jsonify
from rnn import get_pred_string

app = Flask(__name__, template_folder='../templates', static_url_path='/static', static_folder='../static')


@app.route("/predict", methods=["POST"])
def predict():
    text = request.json["text"]

    prediction = get_pred_string(text)

    # Return the prediction as JSON response
    response = {"prediction": prediction}
    return jsonify(response)


@app.route("/instructions")
def instructions():
    return render_template("instructions.html")


@app.route("/about")
def about():
  return render_template("about.html") 


# Define the home route
@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
