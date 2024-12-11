from flask import Flask, request, jsonify
from flask_cors import CORS
from scipy.optimize import minimize
import numpy as np
import pandas as pd
import copy
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for React integration
app.logger.setLevel(logging.INFO)

# Initialization functions
class instance_nLY:
    def __init__(self, s=[], beta=[], alpha=[], theta=[], gamma=[], cost=[], C_bar=[]):
        self.s = s
        self.beta = beta
        self.alpha = alpha
        self.theta = theta
        self.gamma = gamma
        self.cost = cost
        self.C_bar = C_bar
        self.raw_risk = [_s * _beta * _alpha for _s, _beta, _alpha in zip(s, beta, alpha)]

def flatten_list(_2d_list):
    flat_list = []
    for element in _2d_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list

def objective_prob(Y, _nLayers, obj2):
    f = [np.exp(-1 * sum([obj2.gamma[i - k] * obj2.theta[k] * Y[k] for k in range(i + 1)])) for i in range(_nLayers)]
    return sum(a * b for a, b in zip(obj2.raw_risk, f))

def constraint(Y, obj2):
    return obj2.C_bar - sum(a * b for a, b in zip(obj2.cost, Y))

def compute_f(Y, _nLayers, obj2):
    return [np.exp(-1 * sum([obj2.gamma[i - k] * obj2.theta[k] * Y[k] for k in range(i + 1)])) for i in range(_nLayers)]

def get_numerical_sol(init_val, _nLayers, obj2):
    Y0 = init_val
    bnds = [(0.0, None)] * _nLayers
    con1 = {'type': 'eq', 'fun': lambda Y: constraint(Y, obj2)}
    solution = minimize(lambda Y: objective_prob(Y, _nLayers, obj2), Y0, method='SLSQP', bounds=bnds, constraints=[con1])
    x = [round(i, 2) for i in solution.x]
    f_values = [round(f, 4) for f in compute_f(x, _nLayers, obj2)]
    raw_risk = obj2.raw_risk
    risk_contributions = [round(a * b, 4) for a, b in zip(raw_risk, f_values)]
    total_risk = round(sum(risk_contributions), 4)
    return flatten_list([total_risk, x]), f_values, risk_contributions, total_risk

def initialization(_nLayers, C_bar_init):
    gam = 0.5
    s_init = [500] * _nLayers
    alpha_init = [0.5] * _nLayers
    beta_init = [1 / _nLayers] * _nLayers
    theta_init = [0.4] * _nLayers
    cost_init = [1] * _nLayers
    gamma_init = [1] + [gam**i for i in range(1, _nLayers)]
    return instance_nLY(s=s_init, alpha=alpha_init, beta=beta_init, theta=theta_init, cost=cost_init, gamma=gamma_init, C_bar=C_bar_init)

@app.route('/results', methods=['POST'])
def results():
    try:
        data = request.get_json()
        total_layers = int(data.get('total_layers', 1))
        resource = float(data.get('resource', 100))
        model_type = data.get('model_type', 'prob')

        obj_base = initialization(total_layers, resource)
        solutions, f_values, risk_contributions, total_risk = get_numerical_sol([3] * total_layers, total_layers, obj_base)

        return jsonify({
            'objective_value': total_risk,
            'solutions': solutions[1:],  # Exclude the total risk from the solutions
            'vulnerability': f_values,
            'risk': risk_contributions,
            'consequence': obj_base.s,
            'threat': obj_base.beta,
            'message': f"Processed {model_type} model with {total_layers} layers."
        })
    except Exception as e:
        app.logger.error(f"Error in /results: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
