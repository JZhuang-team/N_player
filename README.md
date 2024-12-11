React and Flask Security Optimization App

This project is a web-based application that visualizes and optimizes security investments for schools using React (frontend) and Flask (backend). The application highlights buildings and roads on a map and provides security data for optimization.

---

Features

- Interactive map with building and road highlights.
- Dynamic sidebar with security data visualization.
- Slider-based control for adjusting security layers and resources.
- Backend integration for real-time data processing.

---

Prerequisites

Ensure you have the following installed on your system:

1. Python (3.8 or later)
2. Node.js (16.x or later)
3. npm (comes with Node.js)
4. Git (optional for cloning the repository)

---

Setup Instructions

1. Clone the Repository
Use Git to clone the repository:
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

---

2. Backend Setup (Flask)

a. Create a Virtual Environment
python3 -m venv venv

b. Activate the Virtual Environment
- On Mac/Linux:
  source venv/bin/activate
- On Windows:
  venv\Scripts\activate

c. Install Dependencies
Install the Python dependencies listed in requirements.txt:
pip install -r requirements.txt

d. Run the Flask Server
Navigate to the backend directory and start the server:
python app.py
The Flask server will start running on http://localhost:8080.

---

3. Frontend Setup (React)

a. Navigate to the React App Directory
cd frontend

b. Install Node.js Dependencies
Run the following command to install required packages:
npm install

c. Start the React Development Server
Start the React app:
npm start
This will open the app in your default browser at http://localhost:3000.

---

Usage

1. Adjust the "Total Layers" and "Resource" sliders in the sidebar.
2. Click "Update" to fetch updated data from the backend.
3. View building and road highlights on the map and interact with the layers for detailed data.
4. Use the dark gray sidebar for data visualization.

---

Project Structure

your-repo-name/
├── frontend/               # React frontend code
│   ├── public/
│   ├── src/
│   │   ├── components/     # React components (e.g., Map.js)
│   │   ├── App.js          # Main React app
│   └── package.json        # Node.js dependencies
├── backend/                # Flask backend code
│   ├── app.py              # Main Flask application
│   ├── templates/          # HTML templates (if any)
│   ├── static/             # Static files
│   └── requirements.txt    # Python dependencies
└── README.md               # Project documentation

---

Troubleshooting

1. Flask Server Not Starting:
   - Ensure you’ve activated the virtual environment.
   - Check if requirements.txt was installed without errors.

2. React App Not Starting:
   - Ensure Node.js and npm are installed.
   - Run npm install again to ensure dependencies are correctly installed.

3. Cross-Origin Resource Sharing (CORS) Errors:
   - Make sure Flask allows requests from localhost:3000. If not, install and configure the flask-cors library:
     pip install flask-cors

---

Contributing

1. Fork the repository.
2. Create a feature branch (git checkout -b feature-name).
3. Commit your changes (git commit -m 'Add feature').
4. Push to the branch (git push origin feature-name).
5. Open a pull request.

---

License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Acknowledgments

- Mapbox for interactive mapping features.
- React for the frontend framework.
- Flask for backend API integration.