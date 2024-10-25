from flask import Flask, render_template , request, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def start():
    if request.method == "POST":
        r = requests.get('https://whoer.net/en/main/api/ip') 
        return jsonify({"ip":r.json() , "request_body": request.json})
    else:
        return "<h1> sab sahi hai :) </h1>"

@app.route("/mbsa")
def mbsa():
    return render_template('index.html')
