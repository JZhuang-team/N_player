React and Flask Security Optimization App

This project is a web-based application that visualizes and optimizes security investments for schools using React (frontend) and Flask (backend). The application highlights buildings and roads on a map and provides security data for optimization.

---

Prerequisites

Ensure you have the following installed on your system:

1. [**Python (3.8 or later)**](https://www.python.org/downloads/)  
2. [**Node.js (16.x or later)**](https://nodejs.org/)  
3. **npm** (comes with Node.js)  
4. [**Git**](https://git-scm.com/) (optional for cloning the repository)  

---

Setup Instructions

1. Clone the Repository
Use Git to clone the repository:
git clone https://github.com/JZhuang-team/N_player.git

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

b. Install Node.js Dependencies
Run the following command to install required packages:
npm install

c. Start the React Development Server
Start the React app:
npm start
This will open the app in your default browser at http://localhost:3000.