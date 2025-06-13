# 💸 2CommunityApp – Monthly Contribution Platform (Comsep)

A Python RESTful API that powers a contribution (tontine) management platform, designed for both a web interface and a Flutter mobile app.

---

## 📖 Description

**Comsep** is a monthly rotating savings platform (tontine) for groups of friends or communities. Each month, all members contribute a fixed amount, and one member receives the total. This continues until everyone has had a turn receiving the pooled amount.

---

## 🚀 Features

- 🔐 User authentication (email + password)
- 👥 Member management
- 📅 Creation of contribution sessions (with customizable duration and number of members)
- 💳 Monthly payment tracking for each user
- 🏆 Monthly winner assignment
- 🧾 Contribution and payment history
- 🛠 Admin interface for managing users and sessions

---

## 🗂️ Project Structure

```bash
2CommunityApp/
├── .venv/                  # Virtual environment (ignored by Git)
├── migrations/             # Alembic database migrations
├── src/
│   ├── config/             # App configuration (env variables, settings)
│   ├── controllers/        # Business logic (payment handling, winner selection, etc.)
│   ├── models/             # SQLAlchemy models (User, Contribution, etc.)
│   ├── routes/             # API routes (Flask Blueprints)
│   ├── utils/              # Helper functions (e.g., hashing, JWT)
│   ├── __init__.py         # Package initializer
│   └── app.py              # Main Flask application
├── tests/                  # Unit and integration tests
├── Dockerfile              # Docker configuration
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore              # Git ignore rules



# Clone the repository
git clone https://github.com/your-username/2CommunityApp.git
cd 2CommunityApp

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate   # Or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up the database
flask db init
flask db migrate
flask db upgrade

# Run the app
python src/app.py
