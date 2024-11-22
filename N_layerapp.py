from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from scipy.optimize import minimize
import numpy as np
import pandas as pd
import copy
import logging
import os
app = Flask(__name__)
app.logger.setLevel(logging.INFO)
metrics_data = {}
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

        # 添加计算 raw_risk 的属性
        self.raw_risk = [_s * _beta * _alpha for _s, _beta, _alpha in zip(s, beta, alpha)]

    def print_values(self):
        print("s =", self.s)
        print("beta =", self.beta)
        print("alpha =", self.alpha)
        print("theta =", self.theta)
        print("gamma =", self.gamma)
        print("cost =", self.cost)
        print("C_bar =", self.C_bar)

def flatten_list(_2d_list):
    flat_list = []
    for element in _2d_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list

def objective_prob(Y, _nLayers):
    global obj2
    f = [None] * _nLayers
    for i in range(len(f)):
        f[i] = np.exp(-1 * sum([obj2.gamma[i - k] * obj2.theta[k] * Y[k] for k in range(i + 1)]))  # vulnerability
    raw_risk = obj2.raw_risk  # 使用预先计算的 raw_risk
    return sum(a * b for a, b in zip(raw_risk, f))

def constraint(Y, obj2):
    return obj2.C_bar - sum(a * b for a, b in zip(obj2.cost, Y))

def compute_f(Y, _nLayers):
    global obj2
    f = [None] * _nLayers
    for i in range(len(f)):
        f[i] = np.exp(-1 * sum([obj2.gamma[i - k] * obj2.theta[k] * Y[k] for k in range(i + 1)]))
    return f

def compute_raw_risk():
    global obj2
    return obj2.raw_risk

def compute_risk_contributions(raw_risk, f_values):
    # 计算每一层的风险贡献：raw_risk[i] * f[i]
    risk_contributions = [round(a * b, 4) for a, b in zip(raw_risk, f_values)]
    total_risk = round(sum(risk_contributions), 4)
    return risk_contributions, total_risk

def get_numerical_sol(init_val, _nLayers, obj2):
    Y0 = init_val
    b = (0.0, None)
    bnds = (b,) * _nLayers
    con1 = {'type': 'eq', 'fun': lambda Y: constraint(Y, obj2)}
    cons = ([con1])
    solution = minimize(lambda Y: objective_prob(Y, _nLayers), Y0, method='SLSQP', bounds=bnds, constraints=cons)
    x = solution.x
    x = [round(i, 2) for i in x]
    f_values = compute_f(x, _nLayers)  # 计算 f[i] 值
    f_values = [round(f, 4) for f in f_values]  # 对 f[i] 进行四舍五入，方便显示
    raw_risk = compute_raw_risk()  # 计算 raw_risk
    risk_contributions, total_risk = compute_risk_contributions(raw_risk, f_values)
    obj_value = total_risk  # objective value 就是 total_risk
    return flatten_list([obj_value, x]), f_values, risk_contributions, total_risk

def addRow(df, ls):
    numEl = len(ls)
    newRow = pd.DataFrame(np.array(ls).reshape(1, numEl), columns=list(df.columns))
    df = pd.concat([df, newRow], ignore_index=True)
    return df

def get_full_sol(_nLayers, obj2, vars_col):
    intial_sol = [3] * _nLayers
    solutions, f_values, risk_contributions, total_risk = get_numerical_sol(intial_sol, _nLayers, obj2)
    required_length = len(vars_col)
    while len(solutions) < required_length:
        solutions.append(0)
    solutions = solutions[:required_length]
    return solutions, f_values, risk_contributions, total_risk

def initialization(_nLayers, C_bar_init):
    gam = 0.5
    s_init = [500 for i in range(1, _nLayers+1)]
    alpha_init = [0.5] * _nLayers
    beta_init = [1 / _nLayers] * _nLayers
    theta_init = [0.4] * _nLayers
    cost_init = [1 for i in range(1, _nLayers+1)]
    gamma_init = [1] + [gam**i for i in range(1, _nLayers)]
    obj_base = instance_nLY(s=s_init, alpha=alpha_init, beta=beta_init, theta=theta_init, cost=cost_init, gamma=gamma_init, C_bar=C_bar_init)
    return obj_base

@app.route('/', methods=['GET', 'POST'])
def index():
    global obj2, metrics_data

    if request.method == 'POST':
        total_layers = int(request.form.get('total_layers'))
        C_bar_init = float(request.form.get('C_bar_init'))

        app.logger.info(f"Total Layers: {total_layers}")
        app.logger.info(f"C_bar_init: {C_bar_init}")

        vars_col = ['obj_value'] + ['y' + str(i+1) for i in range(total_layers)]

        solution_df = pd.DataFrame(columns=vars_col)

        layer_image = None
        if total_layers in [1, 2, 3, 4]:
            layer_image = f"layer{total_layers}.png"

        final_solutions = None
        final_f_values = None
        final_risk_contributions = None
        total_risk = None

        for i in range(total_layers):
            _nLayers = i + 1
            obj_base = initialization(_nLayers, C_bar_init)
            obj2 = copy.deepcopy(obj_base)
            solutions, f_values, risk_contributions, total_risk = get_full_sol(_nLayers, obj2, vars_col)
            solution_df = addRow(solution_df, solutions)
            if i == total_layers - 1:
                final_solutions = solutions
                final_f_values = f_values
                final_risk_contributions = risk_contributions

        solution_df["Layers"] = [i for i in range(1, total_layers+1)] 

        # 提取最终的投资方案
        investments = [final_solutions[i+1] for i in range(total_layers)]  # final_solutions[0] 是 obj_value
        print(total_layers,investments,final_risk_contributions,final_f_values,obj2.s,obj2.beta)
        # Store the calculated data in the global `metrics_data` dictionary
        metrics_data = {
            "layers": total_layers,
            "investment": investments,
            "risk": final_risk_contributions,
            "vulnerability": final_f_values,
            "consequence": obj2.s,
            "threat": obj2.beta
        }
        return render_template(
            'index.html',
            total_layers=total_layers,
            C_bar_init=C_bar_init,
            solutions=investments,#investiment
            objective_value=total_risk,  
            vulnerability=final_f_values,  # vulnerability
            risk=final_risk_contributions,  # risk
            consequence=obj2.s, #consequence
            threat=obj2.beta, #threat
            alpha=obj2.alpha,
            theta=obj2.theta,
            gamma=obj2.gamma,
            cost=obj2.cost,
            C_bar=obj2.C_bar,
            layer_image=layer_image,
            )

    return render_template('home.html')
@app.route('/api/metrics')
def get_metrics():
    return jsonify(metrics_data)

@app.route('/about')
def about():
    return render_template('about_template.html')

@app.route('/contact')
def contact():
    return render_template('contact_template.html')

@app.route('/results', methods=['POST'])
def results():
    return index()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))