from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from scipy.optimize import minimize
import numpy as np
import pandas as pd
import copy
import logging
import os

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Load datasets
df_student = pd.read_csv("data/student_data.csv")   
df_transit = pd.read_csv("data/attractiveness_dhs.csv")   

########################################################
# 1) Risk Optimization Functions & Instance Class
########################################################

class instance_nLY:
    def __init__(self, s, beta, alpha, theta, gamma, cost, C_bar):
        """
        s      : 2D list of consequence values, shape = (nLayers, aTypes)
        beta   : 2D list of threat values, shape = (nLayers, aTypes)
        alpha  : 2D list of vulnerability values, shape = (nLayers, aTypes)
        theta  : 2D list of resource effectiveness factors, shape = (nLayers, mFactors)
        gamma  : 2D list, shape = (nLayers, nLayers)
        cost   : 2D list, shape = (nLayers, mFactors); cost[i][j] is the cost for resource j at layer i
        C_bar  : scalar, total resource budget
        """
        self.s = s
        self.beta = beta
        self.alpha = alpha
        self.theta = theta
        self.gamma = gamma
        self.cost_2d = cost 
        self.C_bar = C_bar

        self.nLayers = len(s)
        self.aTypes = len(s[0]) if self.nLayers > 0 else 0
        self.mFactors = len(theta[0]) if self.nLayers > 0 else 0

    def print_values(self):
        print("s =", self.s)
        print("beta =", self.beta)
        print("alpha =", self.alpha)
        print("theta =", self.theta)
        print("gamma =", self.gamma)
        print("cost =", self.cost_2d)
        print("C_bar =", self.C_bar)


def compute_layer_risk(Y_2d, obj):
    """
    Computes the risk at each layer and attack type:
      risk[i][a] = s[i][a]*beta[i][a]*alpha[i][a]*exp(-exponent_term(i)),
    where exponent_term(i) = sum_{k=0}^{i} sum_{j=0}^{mFactors-1} gamma[k][i]*theta[k][j]*Y_2d[k][j].
    """
    nLayers = obj.nLayers
    aTypes = obj.aTypes
    mFactors = obj.mFactors

    risk_2d = []
    for i in range(nLayers):
        exponent_i = 0.0
        for k in range(i+1):
            for j in range(mFactors):
                exponent_i += obj.gamma[k][i] * obj.theta[k][j] * Y_2d[k][j]
        row_risk = []
        for a in range(aTypes):
            val = obj.s[i][a] * obj.beta[i][a] * obj.alpha[i][a] * np.exp(-exponent_i)
            row_risk.append(val)
        risk_2d.append(row_risk)
    return risk_2d


def sum_risk(risk_2d):
    """
    Sums risk by layer and returns both the per-layer sums and the total risk.
    """
    layer_sums = [sum(row) for row in risk_2d]
    total_risk = sum(layer_sums)
    return layer_sums, total_risk


def objective_prob(Y_flat, obj):
    """
    Returns the total risk (objective) given a flattened Y vector.
    """
    nLayers = obj.nLayers
    mFactors = obj.mFactors

    Y_2d = np.array(Y_flat).reshape(nLayers, mFactors)
    risk_2d = compute_layer_risk(Y_2d, obj)
    _, total_risk = sum_risk(risk_2d)
    return total_risk


def grad_objective(Y_flat, obj):
    """
    Computes the gradient of the objective function.
    """
    nLayers = obj.nLayers
    mFactors = obj.mFactors
    aTypes = obj.aTypes

    Y_2d = np.array(Y_flat).reshape(nLayers, mFactors)
    risk_2d = compute_layer_risk(Y_2d, obj)

    grad = np.zeros((nLayers, mFactors))
    for p in range(nLayers):
        for q in range(mFactors):
            deriv_pq = 0.0
            for i in range(p, nLayers):
                for a in range(aTypes):
                    deriv_pq += -risk_2d[i][a] * obj.gamma[p][i] * obj.theta[p][q]
            grad[p, q] = deriv_pq
    return grad.flatten()


def cost_constraint(Y_flat, obj):
    """
    Computes the cost constraint: total_cost should equal C_bar.
    Returns C_bar - total_cost.
    """
    nLayers = obj.nLayers
    mFactors = obj.mFactors

    Y_2d = np.array(Y_flat).reshape(nLayers, mFactors)

    total_cost = 0.0
    for i in range(nLayers):
        for j in range(mFactors):
            total_cost += obj.cost_2d[i][j] * Y_2d[i][j]

    return obj.C_bar - total_cost


def grad_cost_constraint(Y_flat, obj):
    """
    Computes the gradient of the cost constraint.
    """
    nLayers = obj.nLayers
    mFactors = obj.mFactors

    grad = np.zeros((nLayers, mFactors))
    for p in range(nLayers):
        for q in range(mFactors):
            grad[p, q] = -obj.cost_2d[p][q]
    return grad.flatten()


def compute_vulnerability_matrix(obj, Y_2d, selected_attacks, selected_resource):
    """
    Computes a 3D vulnerability matrix for all layers (i), selected attack types, and selected resource types.

    Parameters:
      obj (instance_nLY): The instance containing system parameters.
      Y_2d (numpy array): A 2D array of investments Y[i][j].
      selected_attacks (list): List of attack type indices (as defined externally).
      selected_resource (list): List of resource type indices (as defined externally).

    Returns:
      numpy array: A 3D array of shape (nLayers, len(selected_attacks), len(selected_resource))
                   containing vulnerability values.
    """
    nLayers = obj.nLayers
    vulnerability_matrix = np.zeros((nLayers, len(selected_attacks), len(selected_resource)))
    print("nLayers:", nLayers)
    print("selected_attacks:", selected_attacks)
    print("selected_resource:", selected_resource)

    # Compute vulnerability for each combination of layer, selected attack, and selected resource
    for i in range(nLayers):
        for a in range(len(selected_attacks)):
            for j in range(len(selected_resource)):
                summation_term = sum(obj.gamma[k][i] * obj.theta[k][j] * Y_2d[k][j] for k in range(i + 1))
                vulnerability_matrix[i, a, j] = np.round(obj.alpha[i][a] * np.exp(-summation_term), 3)

    return vulnerability_matrix



def get_numerical_sol(Y_init, obj):
    """
    Uses the SLSQP solver to find the optimal Y.
    """
    bnds = [(0.0, None)] * (obj.nLayers * obj.mFactors)

    con = {
        'type': 'eq',
        'fun': lambda x: cost_constraint(x, obj),
        'jac': lambda x: grad_cost_constraint(x, obj)
    }

    result = minimize(
        fun=lambda x: objective_prob(x, obj),
        x0=Y_init,
        method='SLSQP',
        jac=lambda x: grad_objective(x, obj),
        bounds=bnds,
        constraints=[con],
        options={'ftol': 1e-9, 'eps': 1e-9, 'maxiter': 1000}
    )
    return result


def get_full_sol(obj):
    """
    Provides an all-ones initial guess, solves the problem, and returns the solution.
    """
    nLayers = obj.nLayers
    mFactors = obj.mFactors
    Y_init = [1.0] * (nLayers * mFactors)
    return get_numerical_sol(Y_init, obj)


def initialization_3d(nLayers, selected_attack_types, selected_resource_types, C_bar, building_name, time_value, weekday_value):
    """
    Initializes the model instance using selected attack/resource indices.
    
    Parameters:
      - nLayers: number of layers (int)
      - selected_attack_types: list of attack type indices (e.g., [0, 2])
      - selected_resource_types: list of resource type indices (e.g., [1])
      - C_bar: total resource budget (float)
      - building_name: name of the building (str)
      - time_value: time string (e.g., '8:00')
      - weekday_value: weekday string (e.g., 'Monday')
    """
    def get_student_count(building, time_val, weekday_val):
        filtered = df_student[
            (df_student['Building'] == building) &
            (df_student['Time'] == time_val) &
            (df_student['Weekday'] == weekday_val)
        ]
        return int(filtered['Student_Count_Building'].iloc[0]) if not filtered.empty else 0

    final_count = get_student_count(building_name, time_value, weekday_value)
    print(f"The student number for {building_name} at {time_value} on {weekday_value} is: {final_count}")

    base_s = [
        [20, 20 , 20, 20, 20],
        [20, 20 , 20, 20, 20],
        [20, 20 , 20, 20, 20],
        [20, 20 , 20, 20, 20],
        [20, 20 , 20, 20, 20]
    ]
    s_2d = [[final_count * val for val in row] for row in base_s]
    s_2d = [row[:] for row in s_2d[:nLayers]] 
    s_2d = [[row[a] for a in selected_attack_types] for row in s_2d]

    print("s_2d =")
    for row in s_2d:
        print(" ", row)

    base_beta = [
        [0.2,  0.2, 0.2,  0.2, 0.2],
        [0.2,  0.2, 0.2,  0.2, 0.2],
        [0.2,  0.2, 0.2,  0.2, 0.2],
        [0.2,  0.2, 0.2,  0.2, 0.2],
        [0.2,  0.2, 0.2,  0.2, 0.2]
    ]
    # beta_2d = [row[:] for row in base_beta[:nLayers]]
    # beta_2d = [[row[a] for a in selected_attack_types] for row in beta_2d]

    beta_2d = [[row[a] for a in selected_attack_types] for row in base_beta[:nLayers]]
    total_sum = sum(sum(row) for row in beta_2d)
    beta_2d = [[val / total_sum for val in row] for row in beta_2d]

    base_alpha = [
        [1.0,  1.0,  1.0,  1.0, 1.0],
        [1.0,  1.0,  1.0,  1.0, 1.0],
        [1.0,  1.0,  1.0,  1.0, 1.0],
        [1.0,  1.0,  1.0,  1.0, 1.0],
        [1.0,  1.0,  1.0,  1.0, 1.0]
    ]
    alpha_2d = [row[:] for row in base_alpha[:nLayers]]
    alpha_2d = [[row[a] for a in selected_attack_types] for row in alpha_2d]

    base_gamma = [
        [1.0, 0.5, 0.25, 0.125, 0.0625],
        [1.0, 1.0, 0.5,  0.25,  0.125],
        [1.0, 1.0, 1.0,  0.5,   0.25],
        [1.0, 1.0, 1.0,  1.0,   0.5],
        [1.0, 1.0, 1.0,  1.0,   1.0]
    ]
    gamma_2d = [row[:nLayers] for row in base_gamma[:nLayers]]

    base_theta = [
        [0.050, 0.050],
        [0.050, 0.050],
        [0.050, 0.050],
        [0.050, 0.050],
        [0.050, 0.050]
    ]
    theta_2d = [[row[r] for r in selected_resource_types] for row in base_theta[:nLayers]]

    cost_2d = [
        [2.0, 2.0],
        [2.0, 2.0],
        [2.0, 2.0],
        [2.0, 2.0],
        [2.0, 2.0]
    ]
    cost_2d = [[row[r] for r in selected_resource_types] for row in cost_2d[:nLayers]]

    return instance_nLY(s_2d, beta_2d, alpha_2d, theta_2d, gamma_2d, cost_2d, C_bar)


########################################################
# 2) Boston Transit Logic Functions
########################################################

λ = 1 

def attack_success_prob(d):
    return np.exp(-λ * np.array(d))

def defender_success_prob(d):
    return 1 - attack_success_prob(d)

def defender_objective(d, a, v):
    P = attack_success_prob(d)
    return sum(a[i] * P[i] * v[i] for i in range(len(v)))

def attacker_objective(a, d, v):
    P = attack_success_prob(d)
    return -sum(a[i] * P[i] * v[i] for i in range(len(v)))

def budget_constraint_defender(d, C):
    return C - sum(d)

def attack_constraint(a, A):
    return A - sum(a)

def boston_transit_logic(C, A, time_period):
    score_column = f"base_attractiveness_score_{time_period}"
    if score_column not in df_transit.columns:
        raise ValueError(f"Invalid time period: {time_period}. Column not found in the dataset.")

    v = df_transit[score_column].tolist()
    n = len(v)

    # Uniform initializations as in the notebook
    d_init = np.full(n, C / n)
    a_init = np.full(n, A / n)

    # Adjusted bounds
    d_bounds = [(0, C / 5) for _ in range(n)]
    a_bounds = [(0, 1) for _ in range(n)]

    # Constraints for defender and attacker
    d_constraints = {'type': 'eq', 'fun': lambda d: C - np.sum(d)}
    a_constraints = {'type': 'eq', 'fun': lambda a: A - np.sum(a)}

    # Defender optimization
    d_result = minimize(defender_objective, d_init, args=(a_init, v),
                        method='SLSQP', bounds=d_bounds, constraints=d_constraints,
                        options={'ftol': 1e-9})
    d_optimal = np.round(d_result.x, decimals=6)

    # Attacker optimization
    a_result = minimize(attacker_objective, a_init, args=(d_optimal, v),
                        method='SLSQP', bounds=a_bounds, constraints=a_constraints,
                        options={'ftol': 1e-9})
    a_optimal = np.round(a_result.x, decimals=6)

    # Normalize attack probabilities to sum to A
    a_optimal = a_optimal / np.sum(a_optimal) * A
    a_optimal = np.round(a_optimal, decimals=4)

    P_defender = np.round(defender_success_prob(d_optimal), decimals=6)

    # Identify attacked stations by selecting the top A stations by attack probability
    chosen_stations = np.argsort(a_optimal)[-A:]
    chosen_station_names_set = set(df_transit.loc[chosen_stations, "station_name"].tolist())

    station_data = []
    for i, row in df_transit.iterrows():
        station_name = row["station_name"]
        station_data.append({
            "station_name": station_name,
            "defense_allocation": f"{d_optimal[i]:.3f} K$",
            "attractiveness_score": v[i],
            "attack_probability": f"{a_optimal[i]*100:.2f}%",
            "defender_success_probability": f"{P_defender[i]*100:.2f}%",
            "lon": row["Lon"],
            "lat": row["Lat"],
            "is_attacked": station_name in chosen_station_names_set
        })

    print("\nAttacked Stations (Top A by Probability) for time_period =", time_period)
    for idx in chosen_stations:
        print(f"Station Name: {df_transit.loc[idx, 'station_name']}")
        print(f"  - Defense Allocation: {d_optimal[idx]:.3f}")
        print(f"  - Attack Probability: {a_optimal[idx]*100:.2f}%")
        print(f"  - Defender Success Probability: {P_defender[idx]*100:.2f}%")
        print("-" * 50)

    return station_data


def get_all_locations_geojson(time_period):
    score_column = f"base_attractiveness_score_{time_period}"
    if score_column not in df_transit.columns:
        raise ValueError(f"Invalid time period: {time_period}. Column not found in the dataset.")
    
    features = []
    for _, row in df_transit.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["Lon"], row["Lat"]]
            },
            "properties": {
                "station_name": row["station_name"],
                "attractiveness_score": row[score_column]
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return geojson

########################################################
# 3) Flask Routes
########################################################

# Global dictionary to store metrics for API access
metrics_data = {}

@app.route('/bostonMap', methods=['GET', 'POST'])
def boston_map():
    time_period = ""
    C_bar_init = 0
    num_attacks = 0
    station_data = [] 

    if request.method == 'POST':
        time_period = request.form.get("resource_type", "")
        C_bar_init = float(request.form.get("C_bar_init", 0))
        num_attacks = int(request.form.get("num_attacks", 0))
        station_data = boston_transit_logic(C=C_bar_init, A=num_attacks, time_period=time_period)

    return render_template(
        'bostonMap.html',
        resource_type=time_period,
        C_bar_init=C_bar_init,
        num_attacks=num_attacks,
        station_data=station_data
    )

@app.route('/api/metrics')
def get_metrics():
    return jsonify(metrics_data)


@app.route('/ubpd')
def ubpd():
    return render_template('ubpd.html')


@app.route('/results', methods=['POST'])
def results():
    global metrics_data

    if request.method == 'POST':
        total_layers = int(request.form.get('total_layers'))
        rss_type = request.form.getlist('resource_type')  # Multi-selection
        attack_types = request.form.getlist('attack_type[]')  # Multi-selection
        C_bar_init = float(request.form.get('C_bar_init'))

        # Map to indices instead of counts
        resource_mapping = {"guards": 0, "camera": 1}
        attack_mapping = {
            "Type1": 0, "Type2": 1, "Type3": 2, 
            "Type4": 3, "Type5": 4
        }

        # Get indices for selected types
        selected_resource = [resource_mapping[rt] for rt in rss_type]
        selected_attacks = [attack_mapping[atk] for atk in attack_types]

        # Get additional parameters
        building_name = request.form.get('selected_building', 'Hoch')

        curTime = float(request.form.get('time', 8)) 
        time_value = f"{int(curTime)}:{int((curTime % 1) * 60):02d}"

        weekday_value = request.form.get('weekday')

        app.logger.info(f"Selected Resources: {selected_resource}")
        app.logger.info(f"Selected Attacks: {selected_attacks}")

        # Build instance with specific types
        obj_base = initialization_3d(
            total_layers, 
            selected_attacks, 
            selected_resource, 
            C_bar_init, 
            building_name, 
            time_value, 
            weekday_value
        )
        
        # Solve
        sol = get_full_sol(obj_base)
        Y_opt_2d = np.array(sol.x).reshape(obj_base.nLayers, obj_base.mFactors)
        risk_2d = compute_layer_risk(Y_opt_2d, obj_base)
        layer_sums, total_risk = sum_risk(risk_2d)
        investments = np.round(Y_opt_2d, 2).tolist()
        inv = [sum(row) for row in investments] 

        # Calculate consequence 
        consequence = [sum(row) for row in obj_base.s] 
        # Calculate threat 
        threat = [sum(row) for row in obj_base.beta]
        # nLayers = obj_base.nLayers
        # threat = [1.0 / nLayers] * nLayers

        # Calculate vulnerability
        vulnerability_matrix = compute_vulnerability_matrix(obj_base, Y_opt_2d, selected_attacks, selected_resource)
        print("The vulnerability matrix is: " + str(vulnerability_matrix))
        vulnerability = []
        for layer in vulnerability_matrix:
            layer_sum = 0
            for value in layer.flatten():
                layer_sum += value
            vulnerability.append(layer_sum)


        metrics_data = {
            "layers": total_layers,
            "investment": inv,
            "risk": layer_sums,
            "total_risk": total_risk,
            "consequence": consequence,
            "vulnerability": vulnerability,  
            "threat": threat
        }
        return render_template('index.html', **metrics_data)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(metrics_data)
    else:
        return render_template('index.html', **metrics_data)
    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        return redirect(url_for('results'))

@app.route('/api/student-density')
def student_density():
    try:
        df_sd = pd.read_csv('data/student_data.csv')
        json_data = df_sd.to_dict(orient='records')
        return jsonify(json_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_station_data')
def get_station_data():
    time_period = request.args.get('resource_type', '')
    C_bar_init = float(request.args.get('C_bar_init', 0))
    num_attacks = int(request.args.get('num_attacks', 0))
    station_data = boston_transit_logic(C=C_bar_init, A=num_attacks, time_period=time_period)
    return jsonify(station_data)

@app.route('/get_heatmap_data', methods=['GET'])
def heatmap():
    time_period = request.args.get("time_period", "")
    heatmap_type = request.args.get("heatmap_type", "attractiveness")
    C_bar = float(request.args.get("C_bar", 0))
    num_attacks = int(request.args.get("A", 0))
    station_data = boston_transit_logic(C=C_bar, A=num_attacks, time_period=time_period)
    
    features = []
    for station in station_data:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [station["lon"], station["lat"]]
            },
            "properties": {
                "station_name": station["station_name"],
                "value": get_heatmap_value(station, heatmap_type)
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return jsonify(geojson)

def get_heatmap_value(station, heatmap_type):
    if heatmap_type == "attack_probability":
        return float(station["attack_probability"].replace('%', '')) / 100
    elif heatmap_type == "defense_allocation":
        return float(station["defense_allocation"].replace(' K$', ''))
    else:  # attractiveness
        return station["attractiveness_score"]

@app.route('/data/markers')
def get_markers():
    file_path = 'data/markers.json'
    return send_file(file_path)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080)
