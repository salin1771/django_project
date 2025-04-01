# # **Bright Money - Loan Management System**  
**A Django-based web application for managing loans, payments, and user statements.**  

---

## **📥 Installation Guide**  

### **Prerequisites**  
Before running the project, ensure you have the following installed:  
- **Python** (3.8 or higher)  
- **Pip** (Python package manager)  
- **Git** (for cloning the repository)  
- **PostgreSQL** (or SQLite for development)  

---

## **🚀 Quick Setup (Local Development)**  

### **1. Clone the Repository**  
```bash
git clone https://github.com/akshat302/bright-money.git
cd bright-money
```

### **2. Create a Virtual Environment (Recommended)**  
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**  
```bash
pip install -r requirements.txt
```

### **4. Configure Database (PostgreSQL Recommended)**  
- Create a database named `bright_money` (or modify `settings.py` for SQLite).  
- Update `DATABASES` in `lone_ease/settings.py`:  
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': 'bright_money',
          'USER': 'your_db_user',
          'PASSWORD': 'your_db_password',
          'HOST': 'localhost',
          'PORT': '5432',
      }
  }
  ```

### **5. Apply Migrations**  
```bash
python manage.py migrate
```

### **6. Create a Superuser (Admin Access)**  
```bash
python manage.py createsuperuser
```
Follow prompts to set up an admin account.  

### **7. Run the Development Server**  
```bash
python manage.py runserver
```
Access the app at:  
👉 **http://127.0.0.1:8000/**  

---

## **🔧 Available Endpoints**  
| Endpoint | Description |
|----------|-------------|
| `/admin/` | Django admin panel |
| `/register_user/` | User registration |
| `/apply_loan/` | Apply for a loan |
| `/make_payment/` | Make a loan payment |
| `/get_statement/` | View loan statement |

---

## **⚙️ Environment Variables**  
Create a `.env` file in the root directory with:  
```
SECRET_KEY=your_django_secret_key
DEBUG=True
DB_NAME=bright_money
DB_USER=postgres_user
DB_PASSWORD=postgres_password
DB_HOST=localhost
DB_PORT=5432
```

---

## **🐳 Docker Setup (Alternative)**  
If you prefer Docker:  

### **1. Build & Run**  
```bash
docker-compose up --build
```
The app will be available at **http://localhost:8000**  

---

## **🛠️ Troubleshooting**  
### **Issue: "Page Not Found (404)"**  
- Ensure you are accessing valid endpoints (e.g., `/register_user/`).  
- If you want a root URL (`/`), modify `lone_ease/urls.py` to include:  
  ```python
  from django.views.generic import RedirectView
  urlpatterns = [
      path('', RedirectView.as_view(url='register_user/')),
      # ... other paths
  ]
  ```

### **Issue: Database Connection Errors**  
- Verify PostgreSQL is running.  
- Check credentials in `settings.py`.  

---

## **📜 License**  
MIT License  

---

## **📬 Contact**  
For issues or contributions, open a **GitHub Issue** or contact the maintainer.  

🚀 **Happy Coding!** 🚀
