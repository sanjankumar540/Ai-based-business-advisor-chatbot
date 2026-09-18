# System Diagrams (Mermaid)

Paste any block into https://mermaid.live to render, or view directly in
any Markdown viewer that supports Mermaid (GitHub, VS Code with the Mermaid
extension, etc.).

---

## 1. System Architecture

```mermaid
graph TB
    subgraph Client["Presentation Layer"]
        UI[Bootstrap UI + Jinja2 Templates + Chart.js]
    end

    subgraph App["Application Layer (Flask)"]
        Auth[auth.py]
        Dash[dashboard.py]
        Chat[chatbot.py]
        Biz[business.py]
        Pred[prediction.py]
        Rep[reports.py]
    end

    subgraph AI["AI Layer"]
        NLP[nlp.py - Intent Classification]
        RAG[rag.py - TF-IDF Retrieval]
        LLM[llm.py - LLM Client / Demo Fallback]
        Prompts[prompts.py]
    end

    subgraph ML["ML Layer"]
        Train[train_model.py - Random Forest]
        Predict[predict.py]
        Seg[segmentation.py - K-Means]
    end

    subgraph Data["Data Layer"]
        DB[(SQLite via SQLAlchemy)]
    end

    subgraph Reports["Reports Layer"]
        PDF[ReportLab]
        Excel[OpenPyXL]
    end

    UI --> Auth & Dash & Chat & Biz & Pred & Rep
    Chat --> NLP --> RAG --> LLM --> Prompts
    Pred --> Predict --> Train
    Dash --> Seg
    Auth & Dash & Chat & Biz & Pred --> DB
    Rep --> PDF & Excel
    Rep --> DB
```

---

## 2. Data Flow Diagram (Chatbot Query)

```mermaid
flowchart LR
    A[User types question] --> B[NLP: clean + tokenize + classify intent]
    B --> C[RAG: TF-IDF retrieve top-k knowledge base chunks]
    C --> D{Demo Mode?}
    D -- Yes --> E[Structured template response]
    D -- No --> F[Call LLM API with query + context + intent]
    F -- success --> G[LLM-generated structured response]
    F -- failure --> E
    E --> H[Save user + AI messages to DB]
    G --> H
    H --> I[Render response in chat UI]
```

---

## 3. Use Case Diagram

```mermaid
graph LR
    User((Entrepreneur / Founder))

    User --> UC1[Register / Login]
    User --> UC2[Chat with AI Assistant]
    User --> UC3[Generate Business Plan]
    User --> UC4[Run Market Analysis]
    User --> UC5[Predict Business Risk]
    User --> UC6[View Analytics Dashboard]
    User --> UC7[View / Delete Query History]
    User --> UC8[Export PDF / Excel Report]
```

---

## 4. ER Diagram

```mermaid
erDiagram
    USER ||--o{ CONVERSATION : has
    USER ||--o{ BUSINESS_PLAN : creates
    USER ||--o{ PREDICTION : requests
    CONVERSATION ||--o{ MESSAGE : contains

    USER {
        int id PK
        string name
        string email
        string password_hash
        string role
        datetime created_at
    }
    CONVERSATION {
        int id PK
        int user_id FK
        string title
        datetime created_at
    }
    MESSAGE {
        int id PK
        int conversation_id FK
        string sender
        text message
        string category
        datetime created_at
    }
    BUSINESS_PLAN {
        int id PK
        int user_id FK
        string business_name
        string business_type
        float budget
        string target_market
        text content
        datetime created_at
    }
    PREDICTION {
        int id PK
        int user_id FK
        string business_type
        float investment
        string market_demand
        string competition
        string experience
        float operating_cost
        string target_market_size
        string predicted_risk
        datetime created_at
    }
    CUSTOMER_RECORD {
        int id PK
        int age
        float income
        int purchase_frequency
        float spending_amount
        string segment
    }
```

---

## 5. ML Workflow (Risk Prediction Training)

```mermaid
flowchart TD
    A[Load business_dataset.csv] --> B[Drop null rows]
    B --> C[Label-encode categorical columns]
    C --> D[Train/test split 80/20, stratified]
    D --> E[Train RandomForestClassifier n_estimators=200]
    E --> F[Evaluate: accuracy, precision, recall, F1, confusion matrix]
    F --> G[Save model.pkl + encoders.pkl]
    G --> H[predict.py loads artifacts for live predictions]
```

---

## 6. RAG Workflow

```mermaid
flowchart TD
    A[knowledge_base/*.txt files] --> B[Split into paragraph chunks]
    B --> C[TF-IDF vectorize all chunks - fit]
    C --> D[(In-memory TF-IDF index)]
    E[User query] --> F[TF-IDF vectorize query - transform]
    F --> G[Cosine similarity vs all chunks]
    D --> G
    G --> H[Rank chunks, take top-k with score > 0]
    H --> I[Return as context string]
    I --> J[Passed to LLM / Demo template]
```

---

## 7. Overall System Workflow

```mermaid
flowchart TD
    A[User registers/logs in] --> B[Dashboard]
    B --> C{Choose action}
    C -->|Chat| D[NLP -> RAG -> LLM/Demo -> Structured Answer]
    C -->|Risk Prediction| E[Random Forest -> Risk Level + Recommendations]
    C -->|Business Plan| F[LLM/Demo Template -> 10-section Plan]
    C -->|Market Analysis| G[Demo Template -> Market Insights]
    C -->|Analytics| H[K-Means Segmentation + Charts]
    D & E & F & G --> I[(Saved to SQLite)]
    I --> J[Reports: PDF / Excel Export]
```
