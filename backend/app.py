from flask import Flask, jsonify, request
import numpy as np
import pandas as pd

app = Flask(__name__)

@app.route('/api/metrics', methods=['POST'])
def get_metrics():
    data = request.json  # Parse JSON payload
    layers = data.get("layers", 2)
    c_bar_init = data.get("C_bar_init", [500, 500])

    # Perform calculations (Replace with your actual logic)
    result = {
        "layers": layers,
        "investment": [7.82, 2.18],
        "risk": [5.475, 10.9375],
        "vulnerability": [0.0438, 0.0875],
        "consequence": c_bar_init,
        "threat": [0.5, 0.5],
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
