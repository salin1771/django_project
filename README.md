

```markdown
# Credit Service System

A Django-based loan management system with credit scoring, billing, and payment processing.

## Features

- User registration with Aadhar verification
- Credit score calculation from transaction history
- Loan application processing
- EMI payment tracking
- Automated billing system
- Admin dashboard

## Technology Stack

- Backend: Python 3.6+
- Database: SQLite (Development) / PostgreSQL (Production)
- Framework: Django 3.2.11
- Task Queue: Celery 5.3.6
- Caching: Redis 4.3.6

## Database Schema (SQL)

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    aadhar_id VARCHAR(12) UNIQUE NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    annual_income DECIMAL(12,2) NOT NULL,
    credit_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions Table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    aadhar_id VARCHAR(12) NOT NULL,
    date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    transaction_type VARCHAR(6) CHECK (transaction_type IN ('CREDIT', 'DEBIT')),
    FOREIGN KEY (aadhar_id) REFERENCES users(aadhar_id)
);

-- Loans Table
CREATE TABLE loans (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    loan_type VARCHAR(20) DEFAULT 'CREDIT_CARD',
    principal_amount DECIMAL(12,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    term_period INTEGER NOT NULL,
    disbursement_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/salin1771/django_project.git
   cd credit_service
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .\.venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database setup**
   ```bash
   python manage.py migrate
   ```

5. **Import sample data**
   ```bash
   python manage.py import_transactions
   ```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/register-user/` | POST | Register new user |
| `/api/apply-loan/` | POST | Apply for loan |
| `/api/make-payment/` | POST | Record payment |
| `/api/get-statement/` | GET | View loan statement |

## Running the System

1. **Start Django server**
   ```bash
   python manage.py runserver
   ```

2. **Start Celery worker** (in separate terminal)
   ```bash
   celery -A credit_service worker --loglevel=info
   ```

3. **Start Redis** (required for Celery)
   ```bash
   redis-server
   ```

## Project Structure

```
credit-service/
├── data/                   # CSV data files
├── credit_service/         # Django project
│   ├── settings.py         # Configuration
│   └── urls.py            # Main URLs
├── lone_ease/             # Main app
│   ├── management/
│   │   └── commands/      # Custom commands
│   ├── migrations/        # Database migrations
│   ├── models.py          # Database models
│   └── views.py           # API endpoints
├── requirements.txt       # Dependencies
└── manage.py              # Django CLI
```

## Testing

Run unit tests:
```bash
python manage.py test
```

## Admin Access

1. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

   ![Screenshot 2025-04-01 181800](https://github.com/user-attachments/assets/a9c9c6ca-13b0-4f24-ba5e-d1fbb7aa95d7)
![Screenshot 2025-04-01 181812](https://github.com/user-attachments/assets/e51b5169-c702-4a6b-a5df-d5e21b06eab1)



2. Access admin panel at:
   ```
   http://localhost:8000/admin/
   ```

