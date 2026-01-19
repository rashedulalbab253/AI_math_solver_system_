🧠 Multimodal Math Mentor AI

A reliable, end-to-end AI Math Mentor that can solve  math problems using multimodal inputs (image, audio, text), explain solutions step-by-step, and improve over time using memory and human feedback.

This project demonstrates practical engineering of RAG pipelines, multi-agent systems, Human-in-the-Loop (HITL), and memory-based self-learning rather than simple model usage.

🚀 Key Features

Multimodal Input

📷 Image upload (OCR for printed/handwritten math)

🎙 Audio input (speech-to-text)

⌨ Text input

Parser Agent

Cleans OCR/ASR output

Converts raw input into a structured math problem

Detects ambiguity and triggers HITL

Retrieval-Augmented Generation (RAG)

Curated math knowledge base

Vector search using sentence embeddings

No hallucinated citations

Multi-Agent System

Parser Agent

Router Agent (intent detection)

Solver Agent (symbolic math via SymPy)

Verifier Agent (correctness checks)

Optional Guardrails via answer-type validation

Human-in-the-Loop (HITL)

Low OCR/ASR confidence

Ambiguous problem statements

Verification failures

User-initiated corrections

Memory & Self-Learning

Stores solved problems, feedback, and corrections

Reuses past solutions for similar problems

Improves reliability without model retraining

Interactive UI

Input selection (text/image/audio)

OCR / transcript preview with edit option

Agent execution trace

Retrieved knowledge display

Feedback buttons (✅ correct / ❌ incorrect)

📐 Architecture

The overall system architecture is shown below:

![Architecture Diagram] ![alt text](<Architecture Diagram-1.png>)

High-level Flow

User provides input (text, image, or audio)

OCR / ASR extracts text

User reviews and confirms extracted text

Parser Agent creates structured problem

Router Agent determines problem intent

RAG retrieves relevant math knowledge

Solver Agent computes solution

Verifier Agent validates correctness

HITL triggers if confidence is low

Memory Store saves verified solutions

Final answer and explanation shown to user

📚 Supported Math Scope

Algebra

Quadratic equations

Quadratic optimization (min/max)

Basic calculus concepts (derivatives, extrema)

Expression factorization



🛠 Tech Stack

Python

Streamlit (UI)

SymPy (symbolic math)

Sentence Transformers (embeddings)

FAISS / Chroma (vector store)

OCR: PaddleOCR / EasyOCR

ASR: Whisper

LangChain (community modules)


2️⃣ Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the application
streamlit run app.py

🌐 Deployment



🎥 Demo Video

A short demo (3–5 minutes) demonstrates:

Image → OCR → solution

Audio → transcription → solution

HITL correction flow

Memory reuse on similar questions



🧪 Example Problems the System Can Solve

(x − 4)(x + 2) = 12

f(x) = x² − 4x + k, minimum value = 5, find k

4x² + 8x + 16 (factorization)

Spoken quadratic equations via audio input

⚠️ Known Limitations

OCR accuracy may vary for very messy handwriting

Limited to core JEE-level math (not advanced calculus)

No model fine-tuning (pattern reuse only)

These trade-offs are intentional to focus on reliability and explainability.

📌 Evaluation Summary

This project demonstrates:

Correct use of RAG (no hallucinations)

Multi-agent orchestration

Robust HITL handling

Memory-based improvement

Production-oriented Streamlit app

👤 Author

Rashedul Albab
AI / ML Engineer
https://www.linkedin.com/in/rashedul-albab/
