# NEXTMIND: RUN AND TEST GUIDE

Follow these steps to run the application locally and test the full research workflow using Postman.

## 1. PRE-REQUISITES
- Python 3.11+
- [Postman](https://www.postman.com/downloads/) installed.
- API Keys for:
    - **OpenRouter** (for LLMs: DeepSeek, Claude)
    - **OpenAI** (for Embeddings)
    - **Tavily** (for Web Search)

## 2. ENVIRONMENT SETUP
1.  **Rename** `.env.example` to `.env`.
2.  **Fill in the keys** in `.env`:
    - `OPENROUTER_API_KEY`: Your key from openrouter.ai
    - `OPENAI_API_KEY`: Your key from platform.openai.com
    - `TAVILY_API_KEY`: Your key from tavily.com
    - `NEXTMIND_API_KEY`: Set this to `NEXTMIND_API_YOUR_KEY123` (or any secret string).
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 3. START THE SERVER
Run the following command in your terminal:
```bash
python nextmind/main.py
```
The server will start at `http://localhost:8000`.

---

## 4. NETWORK ACCESS (SHARING WITH FRIENDS)
To allow your friend to access the API from her laptop:
1.  **Find your local IP address**:
    -   On Windows: Open Command Prompt and type `ipconfig`. Look for "IPv4 Address" (e.g., `192.168.1.15`).
2.  **Tell your friend to use your IP**:
    -   Instead of `http://localhost:8000`, she should use `http://<YOUR_IP>:8000` (e.g., `http://192.168.1.15:8000`).
3.  **Ensure same network**: Both laptops must be connected to the same Wi-Fi/Local Network.
4.  **Firewall**: Ensure your Windows Firewall allows incoming connections on port 8000.

---

## 5. POSTMAN TESTING WORKFLOW

### STEP 1: AUTHENTICATION
All requests require the following header:
- **Header Key**: `X-API-Key`
- **Header Value**: `NEXTMIND_API_YOUR_KEY123` (matching your `.env`)

---

### STEP 2: START RESEARCH
Initialize the research process for a specific field.

- **Method**: `POST`
- **URL**: `http://localhost:8000/start-research`
- **Body (JSON)**:
```json
{
    "field": "Quantum Machine Learning"
}
```
- **Action**: Copy the `session_id` from the response.

---

### STEP 3: CHECK PROGRESS (TOPIC GENERATION)
Wait a few seconds for the AI to generate topics.

- **Method**: `GET`
- **URL**: `http://localhost:8000/progress/{{session_id}}`
- **Action**: Look at the `logs` and `topics` generated in the state. Once "Topic generation" is complete, pick a topic.

---

### STEP 4: SELECT TOPIC
Tell the AI which specific topic to dive into.

- **Method**: `POST`
- **URL**: `http://localhost:8000/select-topic`
- **Body (JSON)**:
```json
{
    "session_id": "{{session_id}}",
    "topic": "Variational Quantum Eigensolvers for Chemistry"
}
```

---

### STEP 5: MONITOR FULL WORKFLOW
The AI is now performing retrieval, analysis, and synthesis in the background.

- **Method**: `GET`
- **URL**: `http://localhost:8000/progress/{{session_id}}`
- **Action**: Poll this endpoint. You will see stages like `retrieval`, `aggregation`, `gap_detection`, and `hypothesis_generation`.

---

### STEP 6: GET FINAL RESULT
Once progress reaches 100% and status is "completed".

- **Method**: `GET`
- **URL**: `http://localhost:8000/result/{{session_id}}`
- **Response**: You will receive the identified **Research Gap**, the **Hypothesis**, and the **Novelty Score**.

---

## TROUBLESHOOTING
- **403 Forbidden**: Check if your `X-API-Key` header matches exactly what is in your `.env`.
- **Session Not Found**: Ensure you are using the correct `session_id` returned from the first step.
- **Graph Error**: Check the terminal logs for any API errors (e.g., incorrect OpenRouter key).
