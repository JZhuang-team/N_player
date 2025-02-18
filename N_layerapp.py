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

# Load the dataset
file_path = "./data/attractiveness_dhs.csv"
df = pd.read_csv(file_path)

# Extract necessary data
v = df["base_attractiveness_score_VERY_EARLY_MORNING"].tolist()  # Attractiveness scores
n = len(v)  # Number of stations

# Constants
λ = 1  # Given constant

# Define the attack success probability function
def attack_success_prob(d):
    return np.exp(-λ * np.array(d))  # P_i(d_i) = e^(-λ d_i)

def defender_success_prob(d):
    return 1 - attack_success_prob(d)  # Defender's probability = 1 - Attacker's probability

# Defender's optimization function (Minimization)
def defender_objective(d):
    P = attack_success_prob(d)
    return sum(a[i] * P[i] * v[i] for i in range(n))  # Minimize risk

# Attacker's optimization function (Maximization)
def attacker_objective(a, d):
    P = attack_success_prob(d)
    return -sum(a[i] * P[i] * v[i] for i in range(n))  # Maximize attack success (negated for minimization solver)

# Constraint for the defender: total budget must sum to C
def budget_constraint(d):
    return C - sum(d)

# Constraint for the attacker: must select exactly A targets
def attack_constraint(a):
    return A - sum(a)  # Allow multiple attacks

# Function to perform the defender-attacker optimization
def boston_transit_logic(C, A):
    global a  # Attacker's decision variable

    # Initialize attacker's decision variable (binary-like continuous relaxation)
    a = np.ones(n) / n  # Equal probability for each station initially

    # Initial guesses
    d_init = [C / n] * n  # Defender initially distributes resources equally
    a_init = [A / n] * n  # Attacker initially distributes attack probability equally

    # Bounds
    d_bounds = [(0, None) for _ in range(n)]  # Defender's resources must be non-negative
    a_bounds = [(0, 1) for _ in range(n)]  # Attacker's choice is binary (but we use continuous relaxation)

    # Define constraints with C and A in scope
    d_constraints = {'type': 'eq', 'fun': lambda d: C - sum(d)}  # Budget constraint
    a_constraints = {'type': 'eq', 'fun': lambda a: A - sum(a)}  # Attack constraint

    # Iterate until convergence (equilibrium point)
    tolerance = 1e-4  # Convergence threshold
    max_iterations = 10

    for iteration in range(max_iterations):
        # Solve for the defender's best response (Minimize risk)
        d_result = minimize(defender_objective, d_init, method='SLSQP', bounds=d_bounds, constraints=d_constraints)
        d_optimal = d_result.x

        # Solve for the attacker's best response (Maximize attack success)
        a_result = minimize(attacker_objective, a_init, args=(d_optimal,), method='SLSQP', bounds=a_bounds, constraints=a_constraints)
        a_optimal = a_result.x

        # Check for convergence
        if np.linalg.norm(np.array(d_optimal) - np.array(d_init)) < tolerance and np.linalg.norm(np.array(a_optimal) - np.array(a_init)) < tolerance:
            break  # Equilibrium reached

        # Update initial guesses
        d_init = d_optimal
        a_init = a_optimal

    # Compute defender's success probability
    P_defender = defender_success_prob(d_optimal)

    # Extract the top A attack targets
    chosen_stations = np.argsort(a_optimal)[-A:]  # Select the top A attacks
    chosen_station_names = df.loc[chosen_stations, "station_name"].tolist()

    # Determine attack success or failure
    attack_results = []
    for i in chosen_stations:
        if a_optimal[i] > P_defender[i]:  # If attack probability is higher than defender's probability, attack succeeds
            attack_results.append("❌ Attack Successful")
        else:
            attack_results.append("✅ Attack Blocked")

    # Return the results
    return {
        "chosen_station_names": chosen_station_names,
        "attack_results": attack_results,
        "defense_allocations": d_optimal.tolist(),
        "attack_probabilities": a_optimal.tolist(),
        "defender_success_probabilities": P_defender.tolist(),
    }

@app.route('/bostonMap', methods=['GET', 'POST'])
def boston_map():
     # Default values
    resource_type = ""
    C_bar_init = 0
    num_attacks = 0

    if request.method == 'POST':
        # Retrieve submitted values
        resource_type = request.form.get("resource_type", "")
        C_bar_init = request.form.get("C_bar_init", 0)
        num_attacks = request.form.get("num_attacks", 0)

        # Ensure proper conversion
        C_bar_init = float(C_bar_init) if C_bar_init else 0
        num_attacks = int(num_attacks) if num_attacks else 0

        # Call the risk assessment function
        results = boston_transit_logic(C=C_bar_init, A=num_attacks)

        # Render the bostonMap.html template with the results
        return render_template(
            'bostonMap.html',
            resource_type=resource_type,
            C_bar_init=C_bar_init,
            num_attacks=num_attacks,
            chosen_station_names=results["chosen_station_names"],
            attack_results=results["attack_results"],
            defense_allocations=results["defense_allocations"],
            attack_probabilities=results["attack_probabilities"],
            defender_success_probabilities=results["defender_success_probabilities"],
            zip=zip
        )

    # If it's a GET request, just render the bostonMap.html template
    return render_template('bostonMap.html', zip=zip, num_attacks=num_attacks, C_bar_init=C_bar_init, resource_type=resource_type)  # Pass the zip function to the template


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
    theta_init = [0.04] * _nLayers
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


@app.route('/results', methods=['POST'])
def results():
    return index()

@app.route('/api/student-density')
def student_density():
    try:
        df = pd.read_csv('data/student_data.csv')
        json_data = df.to_dict(orient='records')
        return jsonify(json_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080)
