from flask import Flask, render_template_string, request, redirect, url_for, jsonify, make_response
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import copy
import seaborn as sns
import io
import base64
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)




form_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>N-layer Model</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        :root {
            --primary-color: #007bff;
            --secondary-color: #000000;
            --background-color: #ecf0f1;
            --text-color: #34495e;
            --card-background: #ffffff;
        }
        body {
            font-family: 'Roboto', sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }
        .navbar {
            background-color: var(--primary-color);
            box-shadow: 0 2px 4px rgba(0,0,0,.1);
        }
        .navbar-brand, .nav-link {
            color: #fff !important;
            transition: opacity 0.3s ease;
        }
        .navbar-brand:hover, .nav-link:hover {
            opacity: 0.8;
        }
        .nav-item.active .nav-link {
            font-weight: bold;
            border-bottom: 2px solid #fff;
        }
        .main-content {
            padding: 40px 0;
        }
        .card {
            background-color: var(--card-background);
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }
        .card-header {
            background-color: var(--primary-color);
            color: #fff;
            border-radius: 15px 15px 0 0;
            padding: 20px;
        }
        .card-body {
            padding: 30px;
        }
        .card-body h4 i {
            color: #000000;
            margin-right: 10px;
        }
        .form-group label {
            font-weight: 500;
            color: var(--secondary-color);
            margin-bottom: 10px;
        }
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            transition: background-color 0.3s ease, transform 0.3s ease;
            border-radius: 25px;
            padding: 10px 20px;
            font-weight: bold;
        }
        .btn-primary:hover {
            background-color: #0056b3;
            border-color: #0056b3;
            transform: scale(1.05);
        }
        .model-description {
            margin-top: 20px;
            text-align: center;
            font-size: 16px;
            color: var(--secondary-color);
        }
        .slider-container {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .slider {
            -webkit-appearance: none;
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: #d3d3d3;
            outline: none;
            opacity: 0.7;
            transition: opacity .2s;
            margin-right: 15px;
        }
        .slider:hover {
            opacity: 1;
        }
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--primary-color);
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.3);
        }
        .slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--primary-color);
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.3);
        }
        .slider::-webkit-slider-thumb:hover,
        .slider::-moz-range-thumb:hover {
            background-color: #0056b3;
            box-shadow: 0 0 0 5px rgba(0, 123, 255, 0.5);
        }
        .slider:active::-webkit-slider-thumb,
        .slider:active::-moz-range-thumb {
            background-color: #004085;
        }
        .slider-value {
            min-width: 50px;
            text-align: center;
            font-weight: bold;
            color: var(--primary-color);
            font-size: 18px;
            background-color: #f8f9fa;
            padding: 5px 10px;
            border-radius: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .custom-control-input:checked ~ .custom-control-label::before {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="#">N-layer Model</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ml-auto">
                    <li class="nav-item active">
                        <a class="nav-link" href="/">Model</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/about">About</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/contact">Contact</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="main-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="text-center mb-0">Model Configuration</h2>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <form action="/results" method="post">
                                <div class="form-group">
                                    <label>Model Type:</label>
                                    <div class="custom-control custom-radio">
                                        <input type="radio" id="prob" name="model_type" class="custom-control-input" value="prob" checked>
                                        <label class="custom-control-label" for="prob">Probabilistic Model</label>
                                    </div>
                                    <div class="custom-control custom-radio mt-2">
                                        <input type="radio" id="stra" name="model_type" class="custom-control-input" value="stra">
                                        <label class="custom-control-label" for="stra">Strategic Model</label>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="total_layers">Total Layers:</label>
                                    <div class="slider-container">
                                        <input type="range" class="slider" name="total_layers" id="total_layers" min="1" max="50" value="1" required>
                                        <span id="total_layers_value" class="slider-value">1</span>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="C_bar_init">Cost:</label>
                                    <div class="slider-container">
                                        <input type="range" class="slider" name="C_bar_init" id="C_bar_init" min="0" max="500" step="5" value="0" required>
                                        <span id="C_bar_init_value" class="slider-value">0</span>
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-primary btn-block">Solve </button>
                            </form>
                        </div>
                        <div class="col-md-6">
                            <h4 class="text-center mb-4"><i class="fas fa-sitemap"></i> Game Tree </h4>
                            <img src="{{ url_for('static', filename='image.png') }}" alt="Model Configuration Image" class="img-fluid rounded shadow">
                            <div id="model-description" class="model-description mt-4">
                                <p>The Probabilistic model is designed to analyze systems facing non-strategic attackers, providing insights into multi-layered security dynamics.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script>
        function updateSliderValue(sliderId, valueId) {
            const slider = document.getElementById(sliderId);
            const output = document.getElementById(valueId);
            output.innerHTML = slider.value;
            slider.oninput = function() {
                output.innerHTML = this.value;
                updateSliderBackground(sliderId);
            }
        }

        function updateSliderBackground(sliderId) {
            const slider = document.getElementById(sliderId);
            const percentage = (slider.value - slider.min) / (slider.max - slider.min) * 100;
            slider.style.background = `linear-gradient(to right, var(--primary-color) 0%, var(--primary-color) ${percentage}%, #d3d3d3 ${percentage}%, #d3d3d3 100%)`;
        }

        updateSliderValue('total_layers', 'total_layers_value');
        updateSliderValue('C_bar_init', 'C_bar_init_value');

        // Initial call to set the background on page load
        updateSliderBackground('total_layers');
        updateSliderBackground('C_bar_init');

        // Update model description based on selected model type
        const modelTypeInputs = document.querySelectorAll('input[name="model_type"]');
        const modelDescription = document.getElementById('model-description');

        modelTypeInputs.forEach(input => {
            input.addEventListener('change', function() {
                if (this.value === 'prob') {
                    modelDescription.innerHTML = '<p>The Probabilistic model is designed to analyze systems facing non-strategic attackers, providing insights into multi-layered security dynamics.</p>';
                } else {
                    modelDescription.innerHTML = '<p>The Strategic model is tailored for systems dealing with strategic attackers, incorporating game-theoretic concepts to model complex security interactions.</p>';
                }
            });
        });
    </script>
</body>
</html>
"""


results_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>N-layer Model Results</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        :root {
            --primary-color: #007bff;
            --secondary-color: #000000;
            --background-color: #ecf0f1;
            --text-color: #34495e;
            --card-background: #ffffff;
        }
        body {
            font-family: 'Roboto', sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }
        .navbar {
            background-color: var(--primary-color);
            box-shadow: 0 2px 4px rgba(0,0,0,.1);
        }
        .navbar-brand, .nav-link {
            color: #fff !important;
            transition: opacity 0.3s ease;
        }
        .navbar-brand:hover, .nav-link:hover {
            opacity: 0.8;
        }
        .nav-item.active .nav-link {
            font-weight: bold;
            border-bottom: 2px solid #fff;
        }
        .main-content {
            padding: 40px 0;
        }
        .card {
            background-color: var(--card-background);
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            margin-bottom: 30px;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }
        .card-header {
            background-color: var(--primary-color);
            color: #fff;
            border-radius: 15px 15px 0 0;
            padding: 20px;
        }
        .card-body {
            padding: 30px;
        }
        .card-body h4 i {
            color: #000000;
            margin-right: 10px;
        }
        .form-group label {
            font-weight: 500;
            color: var(--secondary-color);
            margin-bottom: 10px;
        }
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            transition: background-color 0.3s ease, transform 0.3s ease;
            border-radius: 25px;
            padding: 10px 20px;
            font-weight: bold;
        }
        .btn-primary:hover {
            background-color: #0056b3;
            border-color: #0056b3;
            transform: scale(1.05);
        }
        .model-description {
            margin-top: 20px;
            text-align: center;
            font-size: 16px;
            color: var(--secondary-color);
        }
        .slider-container {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .slider {
            -webkit-appearance: none;
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: #d3d3d3;
            outline: none;
            opacity: 0.7;
            transition: opacity .2s;
            margin-right: 15px;
        }
        .slider:hover {
            opacity: 1;
        }
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--primary-color);
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.3);
        }
        .slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--primary-color);
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.3);
        }
        .slider::-webkit-slider-thumb:hover,
        .slider::-moz-range-thumb:hover {
            background-color: #0056b3;
            box-shadow: 0 0 0 5px rgba(0, 123, 255, 0.5);
        }
        .slider:active::-webkit-slider-thumb,
        .slider:active::-moz-range-thumb {
            background-color: #004085;
        }
        .slider-value {
            min-width: 50px;
            text-align: center;
            font-weight: bold;
            color: var(--primary-color);
            font-size: 18px;
            background-color: #f8f9fa;
            padding: 5px 10px;
            border-radius: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .custom-control-input:checked ~ .custom-control-label::before {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }
        .table {
            background-color: var(--card-background);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .table thead th {
            background-color: var(--primary-color);
            color: #fff;
            border-top: none;
        }
        .table-striped tbody tr:nth-of-type(odd) {
            background-color: rgba(0,0,0,.03);
        }
        .plot-container {
            background-color: var(--card-background);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .plot-container img {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="#">N-layer Model</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ml-auto">
                    <li class="nav-item active">
                        <a class="nav-link" href="/">Model</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/about">About</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/contact">Contact</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="main-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="text-center mb-0">Model Results</h2>
                </div>
                <div class="card-body">
                    <div class="row mt-4">
                        <div class="col-12">
                            <h4 class="text-center"><i class="fas fa-layer-group"></i> Layer-Specific Configuration</h4>
                            {% if layer_image %}
                                <div class="text-center">
                                    <img src="{{ url_for('static', filename=layer_image) }}" alt="Layer Configuration" class="img-fluid rounded mx-auto d-block">
                                </div>
                            {% else %}
                                <p class="text-center">No specific layer configuration image available for {{ total_layers }} layers.</p>
                            {% endif %}
                        </div>
                    </div>

                    <div class="row mt-4">
                        <div class="col-md-6">
                            <h4><i class="fas fa-cog"></i> Configuration</h4>
                            <form action="/results" method="post">
                                <div class="form-group">
                                    <label>Model Type:</label>
                                    <div class="custom-control custom-radio">
                                        <input class="custom-control-input" type="radio" name="model_type" id="prob" value="prob" {% if model_type == 'prob' %}checked{% endif %}>
                                        <label class="custom-control-label" for="prob">Probabilistic Model</label>
                                    </div>
                                    <div class="custom-control custom-radio mt-2">
                                        <input class="custom-control-input" type="radio" name="model_type" id="stra" value="stra" {% if model_type == 'stra' %}checked{% endif %}>
                                        <label class="custom-control-label" for="stra">Strategic Model</label>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="total_layers">Total Layers:</label>
                                    <div class="slider-container">
                                        <input type="range" class="slider" name="total_layers" id="total_layers" min="1" max="50" value="{{ total_layers }}" required>
                                        <span id="total_layers_value" class="slider-value">{{ total_layers }}</span>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="C_bar_init">Cost:</label>
                                    <div class="slider-container">
                                        <input type="range" class="slider" name="C_bar_init" id="C_bar_init" min="0" max="500" step="5" value="{{ C_bar_init }}" required>
                                        <span id="C_bar_init_value" class="slider-value">{{ C_bar_init }}</span>
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-primary">Update Results</button>
                            </form>
                        </div>
                        <div class="col-md-6">
                            <h4><i class="fas fa-sitemap"></i> Game Tree</h4>
                            <img src="{{ url_for('static', filename='image.png') }}" alt="Model Configuration Image" class="img-fluid rounded shadow-sm">
                            <div id="model-description" class="model-description">
                                {% if model_type == 'prob' %}
                                Probabilistic model is to model Non-Strategic Attackers.
                                {% else %}
                                Strategic model is to model Strategic Attackers.
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <h4><i class="fas fa-table"></i> Optimization Outputs</h4>
                            <table class="table table-striped">
                                <tbody>
                                    <tr>
                                        <th>Model</th>
                                        <td>{{ model }}</td>
                                    </tr>
                                    <tr>
                                        <th>Solutions</th>
                                        <td>{{ solutions }}</td>
                                    </tr>
                                </tbody>
                            </table>
                            <h5 class="mt-4">Values:</h5>
                            <ul class="list-unstyled">
                                <li><strong>s:</strong> {{ s }}</li>
                                <li><strong>beta:</strong> {{ beta }}</li>
                                <li><strong>alpha:</strong> {{ alpha }}</li>
                                <li><strong>theta:</strong> {{ theta }}</li>
                                <li><strong>gamma:</strong> {{ gamma }}</li>
                                <li><strong>cost:</strong> {{ cost }}</li>
                                <li><strong>C_bar:</strong> {{ C_bar }}</li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h4><i class="fas fa-chart-area"></i> Optimal Investment Across Layers</h4>
                            <div class="plot-container">
                                <img src="data:image/png;base64,{{ plot_url }}" alt="N-layer Results Plot" class="img-fluid rounded">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script>
        function updateSliderValue(sliderId, valueId) {
            const slider = document.getElementById(sliderId);
            const output = document.getElementById(valueId);
            output.innerHTML = slider.value;
            slider.oninput = function() {
                output.innerHTML = this.value;
                updateSliderBackground(sliderId);
            }
        }

        function updateSliderBackground(sliderId) {
            const slider = document.getElementById(sliderId);
            const percentage = (slider.value - slider.min) / (slider.max - slider.min) * 100;
            slider.style.background = `linear-gradient(to right, var(--primary-color) 0%, var(--primary-color) ${percentage}%, #d3d3d3 ${percentage}%, #d3d3d3 100%)`;
        }

        updateSliderValue('total_layers', 'total_layers_value');
        updateSliderValue('C_bar_init', 'C_bar_init_value');

        // Initial call to set the background on page load
        updateSliderBackground('total_layers');
        updateSliderBackground('C_bar_init');
    </script>
</body>
</html>
"""

# About template

about_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - N-layer Model</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        :root {
            --primary-color: #007bff;
            --secondary-color: #2c3e50;
            --background-color: #ecf0f1;
            --text-color: #34495e;
            --card-background: #ffffff;
        }
        body {
            font-family: 'Roboto', sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }
        .navbar {
            background-color: var(--primary-color);
            box-shadow: 0 2px 4px rgba(0,0,0,.1);
        }
        .navbar-brand, .nav-link {
            color: #fff !important;
            transition: opacity 0.3s ease;
        }
        .navbar-brand:hover, .nav-link:hover {
            opacity: 0.8;
        }
        .nav-item.active .nav-link {
            font-weight: bold;
            border-bottom: 2px solid #fff;
        }
        .main-content {
            padding: 40px 0;
        }
        .card {
            background-color: var(--card-background);
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }
        .card-header {
            background-color: var(--primary-color);
            color: #fff;
            border-radius: 15px 15px 0 0;
            padding: 20px;
        }
        .card-header h2 {
            color: #FFFFFF;  /* Changed to white */
        }
        .card-body {
            padding: 30px;
        }
        h2 {
            color: var(--primary-color);
        }
        ul {
            padding-left: 20px;
        }
        li {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">N-layer Model</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ml-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Model</a>
                    </li>
                    <li class="nav-item active">
                        <a class="nav-link" href="/about">About</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/contact">Contact</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="main-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="text-center mb-0">About the N-layer Model</h2>
                </div>
                <div class="card-body">
                    <p>The N-layer Model is an advanced tool for analyzing and optimizing multi-layered security systems. It provides two main types of analysis:</p>
                    <ul>
                        <li><strong>Probabilistic Model:</strong> This model is designed to analyze systems facing non-strategic attackers. It helps in understanding the probabilistic nature of attacks and defenses across multiple layers.</li>
                        <li><strong>Strategic Model:</strong> This model is tailored for systems dealing with strategic attackers. It incorporates game-theoretic concepts to model the strategic interactions between defenders and attackers.</li>
                    </ul>
                    <p>Our model allows you to configure the number of layers and associated costs, providing a comprehensive view of optimal investment strategies across different security layers.</p>
                    <p>Whether you're a security professional, researcher, or decision-maker, the N-layer Model offers valuable insights into creating robust, multi-layered security systems.</p>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
"""
# Contact template

contact_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact - N-layer Model</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        :root {
            --primary-color: #007bff;
            --secondary-color: #2c3e50;
            --background-color: #ecf0f1;
            --text-color: #34495e;
            --card-background: #ffffff;
        }
        body {
            font-family: 'Roboto', sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }
        .navbar {
            background-color: var(--primary-color);
            box-shadow: 0 2px 4px rgba(0,0,0,.1);
        }
        .navbar-brand, .nav-link {
            color: #fff !important;
            transition: opacity 0.3s ease;
        }
        .navbar-brand:hover, .nav-link:hover {
            opacity: 0.8;
        }
        .nav-item.active .nav-link {
            font-weight: bold;
            border-bottom: 2px solid #fff;
        }
        .main-content {
            padding: 40px 0;
        }
        .card {
            background-color: var(--card-background);
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }
        .card-header {
            background-color: var(--primary-color);
            color: #FFFFFF;
            border-radius: 15px 15px 0 0;
            padding: 20px;
        }
        .card-header h2 {
            color: #FFFFFF;  
        }
        .card-body {
            padding: 30px;
        }
        h2 {
            color: var(--primary-color);
        }
        .contact-info {
            font-size: 1.2em;
            margin-top: 20px;
        }
        .contact-info i {
            color: var(--primary-color);
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">N-layer Model</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ml-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Model</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/about">About</a>
                    </li>
                    <li class="nav-item active">
                        <a class="nav-link" href="/contact">Contact</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="main-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="text-center mb-0">Contact Us</h2>
                </div>
                <div class="card-body">
                    <p class="text-center">For any inquiries or feedback about the N-layer Model, please don't hesitate to reach out to us.</p>
                    <div class="contact-info text-center">
                        <p><i class="fas fa-envelope"></i> <a href="mailto:support@nlayermodel.com">support@nlayermodel.com</a></p>
                        <p><i class="fas fa-phone"></i> +1 (xxx) 123-4567</p>
                        <p><i class="fas fa-map-marker-alt"></i> 123 XXX, 14221 </p>
                    </div>
                    <p class="text-center mt-4">We appreciate your interest and will get back to you as soon as possible.</p>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
"""


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
        f[i] = np.exp(-1 * sum([obj2.gamma[i-k] * obj2.theta[k] * Y[k] for k in range(i+1)]))
    raw_risk = [_s * _beta * _alpha for _s, _beta, _alpha in zip(obj2.s, obj2.beta, obj2.alpha)]
    return sum(a * b for a, b in zip(raw_risk, f))

def objective_stra(Y, _nLayers):
    global obj2
    f = [None] * _nLayers
    for i in range(len(f)):
        f[i] = np.exp(-1 * sum([obj2.gamma[i-k] * obj2.theta[k] * Y[k] for k in range(i+1)]))
    raw_risk = [_s * _alpha for _s, _alpha in zip(obj2.s, obj2.alpha)]
    return max(a * b for a, b in zip(raw_risk, f))

def constraint(Y, obj2):
    return obj2.C_bar - sum(a * b for a, b in zip(obj2.cost, Y))

def get_numerical_sol(init_val, _model, _nLayers, obj2):
    Y0 = init_val
    b = (0.0, None)
    bnds = (b,) * _nLayers
    con1 = {'type': 'eq', 'fun': lambda Y: constraint(Y, obj2)}
    cons = ([con1])
    if _model == 'prob':
        solution = minimize(lambda Y: objective_prob(Y, _nLayers), Y0, method='SLSQP', bounds=bnds, constraints=cons)
        x = solution.x
        x = [round(i, 4) for i in x]
        obj_value = round(objective_prob(x, _nLayers), 4)
    elif _model == 'stra':
        solution = minimize(lambda Y: objective_stra(Y, _nLayers), Y0, method='SLSQP', bounds=bnds, constraints=cons)
        x = solution.x
        x = [round(i, 4) for i in x]
        obj_value = round(objective_stra(x, _nLayers), 4)
    else:
        print("Something is wrong here......(get_numerical_sol)")
    return flatten_list([obj_value, x])

def addRow(df, ls):
    numEl = len(ls)
    newRow = pd.DataFrame(np.array(ls).reshape(1, numEl), columns=list(df.columns))
    df = pd.concat([df, newRow], ignore_index=True)
    return df

def get_full_sol(_nLayers, whichmodel, obj2, vars_col):
    intial_sol = [3] * _nLayers
    solutions = get_numerical_sol(intial_sol, whichmodel, _nLayers, obj2)
    required_length = len(vars_col)
    while len(solutions) < required_length:
        solutions.append(0)
    return solutions[:required_length]

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

def generate_plot(whichmodel, solution_df, total_layers, obj2):
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    global obj2

    if request.method == 'POST':
        model_type = request.form.get('model_type')
        total_layers = int(request.form.get('total_layers'))
        C_bar_init = float(request.form.get('C_bar_init'))

        app.logger.info(f"Total Layers: {total_layers}")
        app.logger.info(f"C_bar_init: {C_bar_init}")

        vars_col = ['obj_value'] + ['y' + str(i+1) for i in range(total_layers)]
        model_set = ['prob', 'stra']
        prob_solutions = None
        stra_solutions = None

        labels = ['Layer ' + str(i+1) for i in range(total_layers)]
        plot_urls = {}

        # Select the appropriate image based on total_layers
        layer_image = None
        if total_layers in [1, 2, 3, 4]:
            layer_image = f"layer{total_layers}.png"

        for m in range(len(model_set)):
            whichmodel = model_set[m]
            solution_df = pd.DataFrame(columns=vars_col)

            for i in range(total_layers):
                _nLayers = i + 1
                obj_base = initialization(_nLayers, C_bar_init)
                obj2 = copy.deepcopy(obj_base)
                solutions = get_full_sol(_nLayers, whichmodel, obj2, vars_col)
                solution_df = addRow(solution_df, solutions)
            
            solution_df["Layers"] = [i for i in range(1, total_layers+1)] 

            if whichmodel == 'prob':
                prob_solutions = solutions
            elif whichmodel == 'stra':
                stra_solutions = solutions
            else:
                print("Something is wrong.")

            finaldata = pd.DataFrame()
            for i in range(0, total_layers):
                new_name = 'invest' + str(i+1)
                old_name = 'y' + str(i+1)
                finaldata[new_name] = obj2.cost[i] * solution_df[old_name]

            data_perc = 100 * finaldata[finaldata.columns.values.tolist()].divide(finaldata[finaldata.columns.values.tolist()].sum(axis=1), axis=0)
            data_perc["Layers"] = [i for i in range(1, total_layers+1)]

            for i in range(1, total_layers + 1):
                col = 'invest' + str(i)
                data_perc[col] = pd.to_numeric(data_perc[col], errors='coerce')

            plt.stackplot(data_perc['Layers'],
                          [data_perc['invest' + str(i+1)] for i in range(total_layers)],
                          labels=labels,
                          colors=sns.color_palette(("Greys"), total_layers),
                          alpha=1, edgecolor='grey')

            plt.margins(x=0)
            plt.margins(y=0)
            plt.rcParams['font.size'] = 15
            if whichmodel == 'prob':
                plt.ylabel("Budget allocation (%)", fontsize=18)
                plt.xlabel("Number of layers for LRA-PR Model", fontsize=18)
            if whichmodel == 'stra':
                plt.xlabel("Number of layers for LRA-SR Model", fontsize=18)

            plt.legend(fontsize=14, markerscale=2, loc='center left', bbox_to_anchor=(1.2, 0.5), fancybox=True, shadow=True, ncol=1)

            plot_urls[whichmodel] = generate_plot(whichmodel, solution_df, total_layers, obj2)

        if model_type == 'prob':
            display_solutions = prob_solutions
            display_model = 'prob'
        else:
            display_solutions = stra_solutions
            display_model = 'stra'

        return render_template_string(
            results_template,
            model_type=model_type,
            plot_url=plot_urls[display_model],
            total_layers=total_layers,
            C_bar_init=C_bar_init,
            model=display_model,
            solutions=str(display_solutions),
            s=str(obj2.s),
            beta=str(obj2.beta),
            alpha=str(obj2.alpha),
            theta=str(obj2.theta),
            gamma=str(obj2.gamma),
            cost=str(obj2.cost),
            C_bar=str(obj2.C_bar),
            layer_image=layer_image)  # New parameter for layer-specific image

    return render_template_string(form_template)

@app.route('/about')
def about():
    return render_template_string(about_template)

@app.route('/contact')
def contact():
    return render_template_string(contact_template)

@app.route('/results', methods=['POST'])
def results():
    return index()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

#if __name__ == "__main__":
#    app.run(debug=True, port=5000)
