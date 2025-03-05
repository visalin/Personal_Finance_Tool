# Personal Finance Dashboard - Simplify Your Financial Management

The Personal Finance Dashboard is a comprehensive web application that helps users track expenses, manage budgets, and monitor savings across different categories. Built with Flask and MySQL, it provides an intuitive interface for maintaining financial health through detailed expense tracking and budget management.

The application offers powerful features for personal finance management including monthly budget tracking, categorized expense logging, and visual representations of financial data. Users can set category-specific budgets, track remaining amounts, and view their savings progress through an interactive dashboard with charts and detailed summaries.

## Repository Structure
```
.
├── app/                      # Main application package
│   ├── __init__.py          # Flask application initialization
│   ├── config.py            # Application configuration settings
│   ├── models.py            # Database models and schemas
│   ├── routes.py            # Application routes and view functions
│   ├── static/              # Static assets (CSS, JS)
│   ├── templates/           # HTML templates for the application
│   └── utils.py             # Utility functions
├── requirements.txt         # Project dependencies
└── run.py                  # Application entry point
```

## Usage Instructions
### Prerequisites
- Python 3.6 or higher
- MySQL Server
- pip (Python package installer)

### Installation
1. Clone the repository and navigate to the project directory:
```bash
git clone <repository-url>
cd personal-finance-dashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in a `.env` file:
```
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_NAME=your_database_name
SECRET_KEY=your_secret_key
```

### Quick Start
1. Initialize the database:
```bash
flask db upgrade
```

2. Run the application:
```bash
python run.py
```

3. Access the application at `http://localhost:5000`

### More Detailed Examples
#### Adding an Expense
```python
# Route: /add_expense
# Method: POST
{
    "description": "Grocery Shopping",
    "amount": 150.50,
    "category": "Food",
    "date": "2024-01-15"
}
```

#### Setting a Monthly Budget
```python
# Route: /Setbudget
# Method: POST
{
    "amount": 2000.00,
    "month": "2024-01"
}
```

### Troubleshooting
#### Database Connection Issues
- Error: "Unable to connect to MySQL server"
  1. Verify MySQL service is running:
     ```bash
     sudo service mysql status
     ```
  2. Check database credentials in `.env` file
  3. Ensure MySQL server is accepting connections:
     ```bash
     mysql -u your_username -p
     ```

#### Login Issues
- Error: "Invalid username or password"
  1. Check if user exists in database:
     ```sql
     SELECT * FROM user WHERE username = 'your_username';
     ```
  2. Reset password through forgot password flow
  3. Clear browser cache and cookies

## Data Flow
The application follows a standard MVC pattern for data processing. User requests flow through routes, which interact with models to perform CRUD operations on the MySQL database.

```ascii
[User Interface] -> [Routes] -> [Models] -> [Database]
       ↑             ↓           ↓            ↑
       └─────────── [Templates] [Utils] ──────┘
```

Key component interactions:
1. Routes handle HTTP requests and manage application flow
2. Models define database structure and handle data operations
3. Templates render dynamic HTML content
4. Utils provide helper functions for data processing
5. Database stores user data, expenses, and budget information
6. Authentication middleware ensures secure access to protected routes
7. Session management maintains user state during interaction