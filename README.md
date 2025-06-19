# 🌿 Osteoarthritis Disease Management Portal

This is a full-stack web app to assist in the management of osteoarthritis using plant/molecule data filtered by disease stage and region.

- 🧠 **Frontend**: React (Vite) + Bootstrap + amCharts
- 🔌 **Backend**: Flask REST API + MySQL
- 🧩 Monolith: React is built and served via Flask
- 🌐 Single-port deployment (no CORS hassle)

---

## 📁 Project Structure

```
osteo-portal/
├── app/
│   ├── static/              # Built React assets (JS/CSS)
│   ├── templates/           # index.html for Flask
│   ├── api/                 # Flask API routes
│   ├── __init__.py
│   └── db.py                # (optional) MySQL connection
├── frontend/                # Vite React source code
├── venv/                    # Python virtual environment
├── run.py                   # Flask entry point
├── requirements.txt
```

---

## ⚙️ Installation Instructions

### 📌 Prerequisites

#### Ubuntu / Debian-based Linux

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-server nodejs npm
```

#### Windows

1. **Install Python** from https://www.python.org/downloads/
2. **Install Node.js** from https://nodejs.org/
3. **Install MySQL** (XAMPP or MySQL installer)
4. Use Git Bash or PowerShell for commands

---

## 🧪 Step-by-Step Setup

### 🔹 1. Clone and Setup Flask (Backend)

```bash
cd osteo-portal
python3 -m venv venv         # (use `python` on Windows)
source venv/bin/activate     # or `venv\Scripts\activate` on Windows

pip install -r requirements.txt
```

If `requirements.txt` doesn’t exist, run:
```bash
pip install flask flask-cors mysql-connector-python sqlalchemy
pip freeze > requirements.txt
```

---

### 🔹 2. Start the Flask Server

```bash
cd ..
source venv/bin/activate      # or `venv\Scripts\activate`
python run.py
```

Visit 📍 http://localhost:5000

---

### 🔹 3. Setup React (Frontend)

```bash
cd frontend
npm install
npm install bootstrap axios @amcharts/amcharts5
```

<!-- In `main.jsx`, import Bootstrap:

```js
import 'bootstrap/dist/css/bootstrap.min.css';
``` -->

---

### 🔹 4. Start React

```bash
cd frontend
npm run dev
```


Visit 📍 http://localhost:5173/

---

### 🔹 5. Build React and Copy to Flask (For deployng one port and server localhost:5000)

```bash
npm run build

# Then copy the built files to Flask:
cp -r dist/assets ../app/static/
cp dist/index.html ../app/templates/
```

**Important**: Edit `index.html` and replace `/assets/...` with:

```html
<link href="{{ url_for('static', filename='assets/index-XXX.css') }}" rel="stylesheet">
<script src="{{ url_for('static', filename='assets/index-XXX.js') }}" type="module"></script>
```

---


### 🔹 5. MySQL Setup (Optional)

```sql
CREATE DATABASE osteo;
CREATE USER 'osteo_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON osteo.* TO 'osteo_user'@'localhost';
FLUSH PRIVILEGES;
```

Update `app/db.py` with MySQL connection.


## 📜 License

MIT License. Built for educational and research purposes.