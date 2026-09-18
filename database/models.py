"""
database/models.py
-------------------
SQLAlchemy ORM models for the AI Business Assistant.

Tables:
    User          - registered users
    Conversation  - a chat "thread" belonging to a user
    Message       - individual chat messages inside a conversation
    BusinessPlan  - generated business plans
    Prediction    - ML risk-prediction records
    CustomerRecord- sample customer data used for segmentation demo
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")  # "user" or "admin"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    conversations = db.relationship(
        "Conversation", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    business_plans = db.relationship(
        "BusinessPlan", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    predictions = db.relationship(
        "Prediction", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    business_profiles = db.relationship(
        "BusinessProfile", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.email}>"


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), default="New Conversation")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship(
        "Message", backref="conversation", lazy=True,
        cascade="all, delete-orphan", order_by="Message.created_at"
    )


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # "user" or "ai"
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)  # detected NLP intent
    sources = db.Column(db.String(300), nullable=True)  # comma-separated RAG source filenames
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BusinessPlan(db.Model):
    __tablename__ = "business_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    business_name = db.Column(db.String(150), nullable=False)
    business_type = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=True)
    target_market = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)  # full generated plan text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    business_type = db.Column(db.String(100), nullable=False)
    investment = db.Column(db.Float, nullable=False)
    market_demand = db.Column(db.String(20), nullable=False)   # Low/Medium/High
    competition = db.Column(db.String(20), nullable=False)     # Low/Medium/High
    experience = db.Column(db.String(20), nullable=False)      # Low/Medium/High
    operating_cost = db.Column(db.Float, nullable=False)
    target_market_size = db.Column(db.String(20), nullable=False)  # Small/Medium/Large
    predicted_risk = db.Column(db.String(20), nullable=False)  # Low/Medium/High Risk
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BusinessProfile(db.Model):
    """
    A saved, structured business analysis: profile inputs + computed
    feasibility numbers + ML risk prediction + Business Health Score,
    all stored together so the user can revisit / compare businesses
    later under "My Businesses".
    """
    __tablename__ = "business_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # --- Business Profile inputs ---
    business_name = db.Column(db.String(150), nullable=False)
    business_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(150), nullable=True)
    startup_cost = db.Column(db.Float, nullable=False)
    target_customers = db.Column(db.String(200), nullable=True)
    expected_price_per_order = db.Column(db.Float, nullable=False)
    expected_daily_customers = db.Column(db.Float, nullable=False)
    num_employees = db.Column(db.Integer, default=0)
    avg_employee_cost = db.Column(db.Float, default=0)
    monthly_rent = db.Column(db.Float, default=0)
    raw_material_cost_per_month = db.Column(db.Float, default=0)
    marketing_budget_per_month = db.Column(db.Float, default=0)
    other_monthly_expenses = db.Column(db.Float, default=0)
    business_experience = db.Column(db.String(20), default="Low")  # Low/Medium/High
    market_demand = db.Column(db.String(20), default="Medium")
    competition = db.Column(db.String(20), default="Medium")

    # --- Computed feasibility outputs ---
    monthly_revenue = db.Column(db.Float, nullable=True)
    monthly_cost = db.Column(db.Float, nullable=True)
    net_profit = db.Column(db.Float, nullable=True)
    profit_margin_pct = db.Column(db.Float, nullable=True)
    roi_pct = db.Column(db.Float, nullable=True)
    breakeven_months = db.Column(db.Float, nullable=True)

    # --- ML + Health Score outputs ---
    predicted_risk = db.Column(db.String(20), nullable=True)
    overall_health_score = db.Column(db.Integer, nullable=True)
    financial_score = db.Column(db.Integer, nullable=True)
    risk_score = db.Column(db.Integer, nullable=True)
    competition_score = db.Column(db.Integer, nullable=True)
    market_score = db.Column(db.Integer, nullable=True)
    growth_score = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CustomerRecord(db.Model):
    """Sample customer data used purely for the K-Means segmentation demo."""
    __tablename__ = "customer_records"

    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    income = db.Column(db.Float, nullable=False)
    purchase_frequency = db.Column(db.Integer, nullable=False)
    spending_amount = db.Column(db.Float, nullable=False)
    segment = db.Column(db.String(50), nullable=True)  # assigned after clustering
