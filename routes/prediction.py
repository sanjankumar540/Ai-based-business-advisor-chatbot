"""
routes/prediction.py
---------------------
Business Risk Prediction page: collects inputs, calls ml/predict.py,
saves the result, and shows AI+ML combined recommendations.
"""

from flask import Blueprint, render_template, request, session, flash

from database.database import db
from database.models import Prediction
from routes.auth import login_required
from ml.predict import predict_risk, ModelNotTrainedError

prediction_bp = Blueprint("prediction", __name__)

BUSINESS_TYPES = ["Retail", "Food & Beverage", "E-commerce", "Services",
                   "Manufacturing", "Technology", "Education", "Fashion & Clothing"]
LEVELS = ["Low", "Medium", "High"]
MARKET_SIZES = ["Small", "Medium", "Large"]


def build_recommendations(predicted_risk: str, form_data: dict) -> list:
    """Simple rule-based recommendation engine combining ML output + inputs."""
    recs = []

    if predicted_risk == "High Risk":
        recs.append("Start with a small pilot before committing the full investment amount.")
        recs.append("Re-evaluate your budget — consider reducing initial operating costs.")
        recs.append("Study your top 3 competitors closely before launch.")
    elif predicted_risk == "Medium Risk":
        recs.append("Validate customer demand with a small test batch or soft launch.")
        recs.append("Maintain a 3-6 month cash flow buffer before scaling.")
    else:
        recs.append("Market conditions appear favorable — focus on execution speed.")
        recs.append("Consider allocating extra budget to marketing to capture demand early.")

    if form_data.get("competition") == "High":
        recs.append("Differentiate clearly on price, quality, or niche focus given high competition.")
    if form_data.get("experience") == "Low":
        recs.append("Consider a mentor, online course, or partner with relevant industry experience.")
    if form_data.get("market_demand") == "Low":
        recs.append("Reconsider target market sizing or explore an adjacent niche with stronger demand.")

    recs.append("Track key metrics (sales, cost, customer feedback) weekly during the first 3 months.")
    return recs


@prediction_bp.route("/prediction", methods=["GET", "POST"])
@login_required
def prediction_page():
    result = None
    recommendations = None
    form_data = {}
    error_message = None

    if request.method == "POST":
        try:
            business_type = request.form.get("business_type", "")
            investment = request.form.get("investment", "")
            market_demand = request.form.get("market_demand", "")
            competition = request.form.get("competition", "")
            experience = request.form.get("experience", "")
            operating_cost = request.form.get("operating_cost", "")
            target_market = request.form.get("target_market", "")

            form_data = {
                "business_type": business_type, "investment": investment,
                "market_demand": market_demand, "competition": competition,
                "experience": experience, "operating_cost": operating_cost,
                "target_market": target_market,
            }

            # --- input validation ---
            if not all([business_type, investment, market_demand, competition,
                        experience, operating_cost, target_market]):
                flash("Please fill in all fields.", "danger")
                raise ValueError("missing fields")

            investment = float(investment)
            operating_cost = float(operating_cost)
            if investment <= 0 or operating_cost < 0:
                flash("Investment must be positive and operating cost cannot be negative.", "danger")
                raise ValueError("invalid numeric input")

            prediction_result = predict_risk(
                business_type=business_type, investment=investment,
                market_demand=market_demand, competition=competition,
                experience=experience, operating_cost=operating_cost,
                target_market=target_market,
            )
            predicted_risk = prediction_result["predicted_risk"]

            recommendations = build_recommendations(predicted_risk, form_data)
            result = {
                "predicted_risk": predicted_risk,
                "probabilities": prediction_result["probabilities"],
            }

            # save to DB
            record = Prediction(
                user_id=session["user_id"], business_type=business_type,
                investment=investment, market_demand=market_demand,
                competition=competition, experience=experience,
                operating_cost=operating_cost, target_market_size=target_market,
                predicted_risk=predicted_risk,
            )
            db.session.add(record)
            db.session.commit()

        except ModelNotTrainedError:
            error_message = ("The prediction model hasn't been trained yet. "
                              "Please run 'python ml/train_model.py' first.")
        except ValueError:
            pass  # flash message already set above
        except Exception:
            error_message = "Something went wrong while generating the prediction. Please check your inputs."

    return render_template(
        "prediction.html",
        business_types=BUSINESS_TYPES, levels=LEVELS, market_sizes=MARKET_SIZES,
        result=result, recommendations=recommendations,
        form_data=form_data, error_message=error_message,
    )
