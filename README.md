# Enterprise Expense & Resource Management System (EERM) 

## 📌 Overview

The Enterprise Expense & Resource Management System (EERM) is a web-based application designed to manage employee expenses, approvals, departmental budgets, and organizational resources efficiently.

The system provides role-based access for **Admin, Manager, and Employee**, ensuring secure and structured workflows.

---

## 🚀 Features

* 🔐 User Authentication (Login, Register, Forgot Password)
* 👤 Role-Based Access Control (Admin, Manager, Employee)
* 💰 Expense Submission with Receipt Upload
* ✅ Expense Approval & Rejection Workflow
* 📊 Department-wise Budget Management
* 📦 Resource Request & Allocation System
* 🔔 Notification System
* 📜 Activity Logging & Audit Tracking

---

## 🏗️ Architecture

The application follows a **modular Flask architecture using Blueprints**:

* `auth` → Authentication & password reset
* `admin` → User, policy, and budget management
* `manager` → Expense approvals and monitoring
* `employee` → Expense submission and resource requests

---

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **Frontend:** HTML, CSS, JavaScript
* **Database:** MySQL / MariaDB
* **Cloud Storage:** Cloudinary

---

## 📁 Project Structure

```id="n1q8xf"
Internship_Project-main/
│
├── app.py
├── database.py
├── utils.py
├── requirements.txt
│
├── blueprints/
│   ├── admin/
│   ├── auth/
│   ├── employee/
│   └── manager/
│
├── services/
│   └── notif_service.py
│
├── static/
│   ├── css/
│   ├── img/
│   └── fonts/
│
├── templates/
│
└── db/
    ├── db_eerm.sql
    └── seed.sql
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```id="qv3k9c"
git clone https://github.com/your-username/eerm-project.git
cd eerm-project
```

### 2. Create Virtual Environment

```id="8xk4mz"
python -m venv venv
```

### 3. Activate Environment

* Windows:

```id="6k9z4p"
venv\Scripts\activate
```

* Mac/Linux:

```id="4g7b2r"
source venv/bin/activate
```

### 4. Install Dependencies

```id="0t8p3y"
pip install -r requirements.txt
```

---

## 🗄️ Database Setup

1. Create database:

```id="2m9z1x"
CREATE DATABASE db_eerm;
```

2. Import the schema:

```id="7x3n5a"
db/db_eerm.sql
```

3. Insert seed data (admin user):

```id="9b2k7q"
db/seed.sql
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```id="1p4k8n"
SECRET_KEY=your_secret_key

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=db_eerm

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

---

## ▶️ Run the Application

```id="3z8n2k"
python app.py
```

Open in browser:

```id="5y1q9r"
http://127.0.0.1:5000
```

---

## 👥 Default Admin Login

After running the seed file:

* **Email:** [admin@gmail.com](mailto:admin@gmail.com)
* **Password:** Admin@12345

---

## 🔐 Security Features

* Secure password hashing
* Token-based password reset system
* Role-based access control

---

## 📊 Future Enhancements

* AI-based expense fraud detection
* Mobile application support
* Advanced analytics dashboard
* Real-time notifications

---

## 📄 License

This project is developed for educational purposes.
