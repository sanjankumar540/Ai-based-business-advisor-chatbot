# Viva Preparation — Questions & Answers

### 0. How is this different from just using ChatGPT or Gemini?
ChatGPT/Gemini are general-purpose conversational models — you talk to them
and they answer from what they learned in training. This project is a
Business Decision Support System where the LLM is only one component: it
also has a deterministic Financial Feasibility Engine (real revenue/cost/
ROI/break-even math), a trained Random Forest that outputs a genuine
Low/Medium/High risk classification with a feature-importance-based
explanation, a What-If Simulator for live scenario comparison, a combined
Business Health Score, an ML-scored Idea Generator, and a database that
saves every analysis per user so they can revisit and compare businesses
over time. A general chatbot cannot calculate your break-even point,
cannot give you a reproducible risk classification from a trained model, and
does not persist structured business records tied to your account.

### 1. Why did you choose this project?
Entrepreneurs and students often lack access to structured, affordable
business guidance. This project shows how Generative AI, NLP, RAG, and
Machine Learning can be combined into one practical tool that gives
structured business advice, risk prediction, and planning documents.

### 2. Why did you use Generative AI instead of just a static FAQ system?
A static FAQ can only answer pre-written questions. Generative AI, combined
with RAG, can answer a much wider range of natural-language questions while
still grounding its answers in a specific, controlled knowledge base.

### 3. What is RAG (Retrieval-Augmented Generation)?
RAG is a technique where relevant documents are retrieved from a knowledge
base based on the user's query, and that retrieved text is given to the
language model as context before it generates its answer — instead of the
model relying only on what it memorized during training.

### 4. Why did you use RAG in this project?
RAG lets the assistant's answers be grounded in curated business knowledge
(marketing, finance, risk management, etc.) rather than generic or
unsupported text, and it makes the system's reasoning explainable — we can
show exactly which knowledge-base document was retrieved for a given query.

### 5. How does your RAG implementation actually work (no vector database)?
Knowledge base `.txt` files are split into paragraph chunks. All chunks are
vectorized using TF-IDF (`scikit-learn`). At query time the user's question
is vectorized with the same fitted vectorizer, and cosine similarity ranks
all chunks against the query. The top-k most similar chunks become the
retrieved context.

### 6. Why didn't you use a vector database like FAISS or Pinecone?
For a knowledge base of this size (a handful of documents), TF-IDF +
cosine similarity is fast, requires no extra infrastructure, and is much
easier to explain and debug in an academic setting. A vector database would
be the natural next step for a much larger knowledge base (see Future Scope).

### 7. What is NLP, and how is it used here?
NLP (Natural Language Processing) is used to clean, tokenize, and classify
the user's raw text query into one of eight business intent categories
(e.g., Marketing, Finance, Risk Analysis) using a transparent keyword-scoring
rule-based classifier.

### 8. Why did you use a rule-based classifier instead of a trained NLP model?
It is simple, fast, requires no training data or GPU, and is fully
explainable in a viva ("we score the query against a keyword dictionary per
category and pick the highest-scoring category") — appropriate for an
academic project of this scope.

### 9. What is Machine Learning, and where is it used in this project?
Machine Learning is used in two places: (1) a Random Forest classifier
predicts business risk (Low/Medium/High) from founder-provided parameters,
and (2) K-Means clustering segments sample customer data into four groups.

### 10. Why did you choose Random Forest for risk prediction?
Random Forest is an ensemble of decision trees that is robust to noisy
data, handles both categorical and numerical features well, resists
overfitting better than a single decision tree, and is easy to explain: "many
trees vote, and the majority vote wins."

### 11. What is XGBoost, and why isn't it the primary model here?
XGBoost is a gradient-boosted tree ensemble that often achieves higher
accuracy than Random Forest but is more complex to tune and explain.
Random Forest was chosen as the primary model for easier viva explanation;
XGBoost is listed as an optional advanced extension.

### 12. What features does the risk-prediction model use?
Business type, initial investment, market demand, competition level, founder
experience, expected operating cost, and target market size.

### 13. What dataset did you use to train the model?
A synthetic, academically generated dataset (`data/business_dataset.csv`,
600 rows) created specifically for this project, with risk labels derived
from a transparent scoring rule (higher investment + lower demand + higher
competition + lower experience → higher risk) plus random noise, so the
model has to learn genuine patterns rather than a simple lookup.

### 14. Why is the dataset synthetic instead of real business data?
Real business outcome data (which businesses succeeded/failed and why) is
not publicly available at the granularity needed, and using unverified
scraped data would raise data-quality and licensing concerns. The synthetic
dataset is clearly labeled as such throughout the project and is
appropriate for demonstrating the ML pipeline end-to-end.

### 15. What accuracy did your model achieve, and is it reliable for real use?
The model achieves roughly 70% weighted accuracy on the synthetic test set
(exact figures are printed by `ml/train_model.py`). Because the dataset is
synthetic, this accuracy demonstrates that the pipeline works correctly, but
it is not a claim about real-world predictive accuracy.

### 16. How do you evaluate the model?
Using accuracy, precision, recall, F1-score (all weighted, since classes
are imbalanced), and a confusion matrix, computed on a held-out 20% test
split.

### 17. What is K-Means clustering, and how did you use it?
K-Means is an unsupervised algorithm that groups data points into k clusters
based on feature similarity. Here it clusters sample customers by age,
income, purchase frequency, and spending amount into four segments, which
are then ranked by average spending and labeled Budget/Regular/Premium/
High-Value Customers.

### 18. How does the chatbot actually generate its response, step by step?
(1) NLP cleans the query and classifies its intent. (2) RAG retrieves the
top-k most relevant knowledge-base chunks via TF-IDF cosine similarity. (3)
The query, intent, and retrieved context are combined into a prompt. (4) If
a live LLM API key is configured, the prompt is sent to the LLM; otherwise
(or if the call fails), a structured Demo Mode template response is
returned. (5) Both the user's message and the AI's response are saved to
the database.

### 19. What is "Demo Mode" and why does it matter?
Demo Mode is a fallback that activates automatically when no LLM API key is
configured (or if a live API call fails). It ensures the chatbot, business
plan generator, and market analysis tools still return structured, useful
responses without requiring internet access or an API key — so the whole
project can always be demonstrated in a viva.

### 20. How is the database structured?
SQLite via SQLAlchemy ORM, with tables: User, Conversation, Message,
BusinessPlan, Prediction, and CustomerRecord, linked with foreign keys (e.g.,
Conversation.user_id → User.id, Message.conversation_id → Conversation.id).

### 21. Why Flask instead of Django?
Flask is lightweight and unopinionated, which makes it easier for a student
to understand every part of the request/response flow explicitly (routes,
blueprints, templates) without a large amount of auto-generated boilerplate.

### 22. Why SQLite instead of MySQL/PostgreSQL?
SQLite is file-based and requires no separate database server to install or
configure, which keeps the project simple to set up and run for an academic
demonstration, while SQLAlchemy makes it easy to switch to another database
later if needed.

### 23. How are passwords secured?
Passwords are never stored in plaintext. `werkzeug.security.generate_password_hash`
hashes the password before storing it, and `check_password_hash` verifies
login attempts against the stored hash.

### 24. How do you prevent the app from crashing if the LLM API is down?
All external LLM calls are wrapped in a try/except block (`ai/llm.py`); on
any failure (timeout, invalid key, bad response), the code automatically
falls back to the Demo Mode structured template response instead of raising
an unhandled exception.

### 25. What happens if a user enters an unseen business type in the prediction form?
The prediction preprocessing (`ml/preprocessing.py`) checks whether the
value exists in the fitted LabelEncoder's known classes; if not, it maps the
unseen value to the encoder's first known class rather than crashing, so
prediction always returns a result.

### 26. What is the difference between the chatbot and the Business Plan Generator?
The chatbot handles open-ended, conversational questions with NLP+RAG-driven
structured answers. The Business Plan Generator takes specific structured
inputs (business name, type, budget, etc.) and produces a fixed 10-section
business plan document, which can be saved and exported.

### 27. How do you generate the PDF/Excel reports?
PDF reports are built with ReportLab (`SimpleDocTemplate`, `Paragraph`,
`Table`), pulling the user's latest risk prediction and its recommendations.
Excel reports are built with OpenPyXL, exporting the user's full prediction
history as a formatted spreadsheet.

### 28. How is the recommendation engine built?
It's a rule-based function (`build_recommendations` in `routes/prediction.py`)
that combines the ML-predicted risk level with the raw input parameters
(e.g., "if competition is High, recommend clear differentiation") to produce
a tailored list of next-step recommendations.

### 29. What are the main limitations of this project?
The risk model is trained on synthetic (not real historical) data; the RAG
knowledge base is small and topic-limited; Demo Mode responses are
template-based rather than fully generative without an API key; and market
analysis figures are AI/demo estimates, not verified real-time market data.

### 30. What is the future scope of this project?
Replacing the TF-IDF retriever with a vector database for a larger knowledge
base; integrating real market-data APIs; adding XGBoost as a selectable
model; multi-language chatbot support; and a mobile/PWA front-end reusing
the existing Flask routes.

### 31. How did you test the system?
With a `pytest` suite covering registration/login, the login-required
guard, NLP intent classification across categories, RAG retrieval
relevance, ML prediction validity (including unseen categorical inputs),
and the chatbot/business-plan/market-analysis routes end-to-end using
Flask's test client and an in-memory SQLite database.

### 32. Is this project "real" AI, or is it faked for the demo?
The NLP intent classification and RAG retrieval are genuinely computed for
every query — the retrieved knowledge-base context actually changes based
on the query, verifiable in `tests/test_rag.py`. The Random Forest and
K-Means models are genuinely trained on real (if synthetic) data using
scikit-learn, not hard-coded outputs. Only the final natural-language
generation step uses a template when no LLM API key is configured (Demo
Mode) — everything upstream of that is real computation.
