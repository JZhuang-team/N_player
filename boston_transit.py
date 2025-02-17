import pandas as pd
import numpy as np
from scipy.optimize import minimize

# Load the dataset
file_path = "./data/attractiveness_dhs.csv"
df = pd.read_csv(file_path)

# Extract necessary data
v = df["base_attractiveness_score_VERY_EARLY_MORNING"].tolist()  # Attractiveness scores
n = len(v)  # Number of stations

# Constants
λ = 1  # Given constant

# Initialize attacker's decision variable (binary-like continuous relaxation)
a = np.ones(n) / n  # Equal probability for each station initially

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
    # Initial guesses
    d_init = [C / n] * n  # Defender initially distributes resources equally
    a_init = [A / n] * n  # Attacker initially distributes attack probability equally

    # Bounds
    d_bounds = [(0, None) for _ in range(n)]  # Defender's resources must be non-negative
    a_bounds = [(0, 1) for _ in range(n)]  # Attacker's choice is binary (but we use continuous relaxation)

    # Constraints
    d_constraints = {'type': 'eq', 'fun': budget_constraint}
    a_constraints = {'type': 'eq', 'fun': attack_constraint}

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

# Test the function with example inputs
C = 100  # Defender's budget
A = 3    # Number of attacks

results = boston_transit_logic(C, A)

# Print the results
print("Chosen Station Names:", results["chosen_station_names"])
print("Attack Results:", results["attack_results"])