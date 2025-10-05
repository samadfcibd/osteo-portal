# 🌿 Osteoarthritis Disease Management Portal

A comprehensive full-stack web application for managing osteoarthritis research data, featuring plant/molecule data filtering by disease stage and region. The platform enables researchers to explore biomolecular relationships and clinical trial stages for osteoarthritis treatment.

![Logo](https://github.com/samadfcibd/osteo-portal/blob/master/react-ui/src/assets/images/homepage.png)


## 🚀 Features

- **🔬 Research Data Management** - Organize and query biomolecule data with advanced filtering
- **👨‍💼 Admin Dashboard** - Professional interface built with [Berry Dashboard](https://berrydashboard.com/)
- **📊 Data Visualization** - Interactive charts and data exploration with amCharts integration
- **🔐 Authentication System** - JWT-based secure user authentication and authorization
- **📁 File Upload System** - Support for CSV data imports and PDB molecular files
- **🎯 Clinical Stage Filtering** - Filter data by clinical trial stages and disease progression
- **🌐 Single-Port Deployment** - Simplified deployment architecture without CORS configuration
- **🔍 Advanced Search** - Intelligent search across molecules, plants, and clinical data

<!-- ## 🛠️ Tech Stack

### Frontend
- **React 18** - Main frontend framework
- **Berry Dashboard** - Admin panel template and UI components
- **amCharts** - Data visualization library
- **React Router** - Client-side routing

### Backend  
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **JWT** - Authentication tokens
- **MySQL** - Database management -->

<br />

## 🏗️ Architecture

The application follows a **two-tier architecture** with decoupled frontend and backend:

Frontend (React) ←→ Backend (Flask API) ←→ Database (MySQL)

<br />

## 📁 Project Structure

```plaintext
OSTEO-PORTAL/
├── 📂 api-server-flask/          # Flask Backend API
│   ├── 📂 api/                  # Flask source code (routes, models, business logic)
│   ├── 📂 env/                  # Python virtual environment
│   ├── 📂 uploads/              # File upload directory
│   ├── 📄 .env                  # Backend environment variables
│   ├── 📄 requirements.txt      # Python dependencies
│   ├── 📄 run.py               # Main application entry point
│   └── 📄 gunicorn-rfg.py      # Production server configuration
│
├── 📂 DB/                       # Database schema and migrations
│   └── 📄 osteoarthritis_db.sql # MySQL database dump
│
├── 📂 react-ui/                 # React Frontend Application
│   ├── 📂 build/               # Production build files
│   ├── 📂 node_modules/        # Node.js dependencies
│   ├── 📂 public/              # Static assets
│   ├── 📂 src/                 # React source code
│   │   ├── 📂 components/      # Reusable UI components
│   │   ├── 📂 pages/           # Application pages
│   │   ├── 📂 assets/          # Images, styles, fonts
│   │   └── 📂 utils/           # Helper functions
│   ├── 📄 .env                 # Frontend environment variables
│   ├── 📄 package.json         # Node.js dependencies and scripts
│   └── 📄 .prettierrc          # Code formatting configuration
│
├── 📄 LICENSE.md               # Project license
└── 📄 README.md               # Project documentation
```

<br />

## ⚙️ Prerequisites
Before installation, ensure you have the following installed:

- 🐍 Python 3.8+ - Backend runtime
- 🟢 Node.js 14+ - Frontend runtime (npm or yarn)
- 🗄️ MySQL 5.7+ - Database server
- 🌐 Git - Version control
- 💻 Git Bash or PowerShell - Command line tools (Windows)

<br />

## 🛠️ Installation & Setup

### 🔧 Backend Setup (Flask API)

#### Setup and Run Flask (Backend)

```bash
# 1. Navigate to backend directory
cd api-server-flask

# 2. Create and activate virtual environment
virtualenv env (or python -m venv env)

# On Linux/Mac:
source env/bin/activate

# On Windows:
env\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your database credentials and settings. 
# - Database credentials
# - Secret key
# - API settings
```


#### Database Setup (MySQL):

We are using mysql DB. There is a folder at root named `DB` where you will find the whole mysql db file. Just import the database and update the DB credentials into `.env` inside `api-server-flask`

#### Environment Configuration (.env):

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database Configuration (MySQL)
DB_ENGINE=mysql+pymysql
DB_HOST=127.0.0.1
DB_NAME=osteoarthritis_db
DB_USERNAME=your_username
DB_PASS=your_password
DB_PORT=3306

# File Upload
UPLOAD_FOLDER=uploads
PDB_FOLDER=pdb_files
```

<br />

### ⚛️ Frontend Setup (React UI)

#### Setup & Run React (Frontend)
```bash
# 1. Navigate to frontend directory
cd react-ui

# 2. Install dependencies
npm install
# or using yarn
yarn install

# 3. Configure environment variables
cp env.example .env
# Edit .env with your API configuration

```

#### Environment Configuration (.env):

```bash
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENV=development
REACT_APP_VERSION=1.0.0
```

<br />

### 🚀 Running the Application

#### 🔄 Development Mode

**Start Backend Server:**
```bash
cd api-server-flask
flask run
```

📡 API Server: http://localhost:5000

**Start Frontend Development Server:**
```bash
cd react-ui
npm start
```
🌐 React UI: http://localhost:3000

#### 🏗️ Production Deployment

**Backend Production:**

1. Use Gunicorn for production server

```bash
cd api
gunicorn -c gunicorn-rfg.py run:app
```

2. Configure Nginx (see api/nginx/ for configuration examples)


**Frontend Production Build:**


1. Create production build

```bash
cd react-ui
npm run build
# or
yarn build
```

2. Serve built files using a web server like Nginx

<br />

## 🐛 Troubleshooting

### Common Issues & Solutions
1. **Port already in use:** Change ports in configuration or kill existing processes
2. **Module not found:** Reinstall dependencies using `pip install -r requirements.txt` or `npm install`
3. **Environment variables not loading:** Ensure `.env` files are in correct directories
4. **Database connection failed:** Verify MySQL credentials in `.env` file
5. **CORS errors:** Verify API URL in frontend `.env` matches running backend

### Debugging Tips
1. Check server logs for detailed error messages
2. Verify database connection using MySQL client
3. Confirm virtual environment is activated for Python
4. Clear browser cache if facing frontend issues

<br />

## 🤝 Contributing
We welcome contributions! Please follow these steps:

1. 🍴 Fork the repository

2. 🌿 Create a feature branch (git checkout -b feature/amazing-feature)

3. 💾 Commit your changes (git commit -m 'Add amazing feature')

4. 📤 Push to the branch (git push origin feature/amazing-feature)

5. 🔀 Open a Pull Request

<br />

## 📞 Support
For support and questions:

📧 Email: samadocpl@gmail.com or humayun.112358@gmail.com

<br />

## 🙏 Acknowledgments

### Third-Party Components
- **[Berry Dashboard](https://berrydashboard.com/)** - Open-source React admin template for the backend administration interface
- **amCharts** - Data visualization components
- **Heroicons** - UI icon library

<br />

## 📜 License

This project is licensed under the MIT License - see the LICENSE.md file for details.

Built for educational and research purposes in osteoarthritis disease management.