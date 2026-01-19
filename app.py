import streamlit as st
from PIL import Image
import numpy as np
import tempfile
import warnings

warnings.filterwarnings(
    "ignore",
    message=".*pin_memory.*"
)

# Try importing OCR and ASR, but allow graceful fallback
try:
    from multimodal.ocr import run_ocr
    OCR_AVAILABLE = True
except Exception as e:
    OCR_AVAILABLE = False
    run_ocr = None

try:
    from multimodal.asr import whisper_transcribe
    ASR_AVAILABLE = True
except Exception as e:
    ASR_AVAILABLE = False
    whisper_transcribe = None

from agents.parser_agent import build_parser_input, HumanInTheLoopRequired, ParserAgent
from agents.router_agent import RouterAgent
from agents.solver_agent import SolverAgent
from agents.verifier_agent import VerifierAgent
from rag.retriever import RAGRetriever
from memory.memory_store import MemoryStore


if "original_input" not in st.session_state:
    st.session_state.original_input = None

if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

if "edited_text" not in st.session_state:
    st.session_state.edited_text = ""

if "user_confirmed" not in st.session_state:
    st.session_state.user_confirmed = False

if "structured_problem" not in st.session_state:
    st.session_state.structured_problem = None

if "solution" not in st.session_state:
    st.session_state.solution = None

if "route" not in st.session_state:
    st.session_state.route = None

if "confidence" not in st.session_state:
    st.session_state.confidence = 1.0


# UI
st.title("📘 AI Math Mentor")

input_type = st.radio(
    "Select input type",
    ["text", "image", "audio"]
)


# INPUT Handling
if input_type == "text":
    st.session_state.extracted_text = st.text_area(
        "Enter the math problem",
        value=st.session_state.extracted_text
    )
    st.session_state.confidence = 1.0
    st.session_state.original_input = st.session_state.extracted_text


elif input_type == "image":
    if not OCR_AVAILABLE:
        st.error("❌ Image OCR is temporarily unavailable. Please use text input instead.")
    else:
        image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        if image_file:
            image = Image.open(image_file).convert("RGB")
            image_np = np.array(image)
            text, conf = run_ocr(image_np)
            st.session_state.extracted_text = text
            st.session_state.confidence = conf
            st.session_state.original_input = image_file

elif input_type == "audio":
    if not ASR_AVAILABLE:
        st.error("❌ Audio transcription is temporarily unavailable. Please use text input instead.")
    else:
        audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a"])
        if audio_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_file.read())
                audio_path = tmp.name
            text, conf = whisper_transcribe(audio_path)
            st.session_state.extracted_text = text
            st.session_state.confidence = conf
            st.session_state.original_input = audio_path



# Review and Confirm
if st.session_state.extracted_text:
    st.subheader("Extracted Text (Review & Edit)")

    st.session_state.edited_text = st.text_area(
        "Edit the extracted text if needed:",
        value=st.session_state.extracted_text
    )

    st.session_state.user_confirmed = st.checkbox(
        "I confirm the extracted text is correct",
        value=st.session_state.user_confirmed
    )


# Proceed
if st.session_state.extracted_text and st.session_state.user_confirmed:
    if st.button("Proceed"):
        try:
            parser_input = build_parser_input(
                input_type=input_type,
                original_input=st.session_state.original_input,
                extracted_text=st.session_state.edited_text,
                confidence=st.session_state.confidence,
                user_confirmed=st.session_state.user_confirmed
            )

            # -------- AGENT TRACE --------
            st.subheader("Agent Trace")
            st.markdown("""
            - **Parser Agent** → Structured the problem  
            - **Router Agent** → Determined intent  
            - **RAG Retriever** → Retrieved knowledge  
            - **Solver Agent** → Solved the problem  
            - **Verifier Agent** → Verified correctness  
            """)

            # -------- PARSER --------
            parser_agent = ParserAgent()
            structured_problem = parser_agent.parse(parser_input)
            st.session_state.structured_problem = structured_problem

            st.subheader("Parsed Problem")
            st.json(structured_problem)

            # -------- RAG --------
            retriever = RAGRetriever()
            retrieved_context = retriever.retrieve(
                structured_problem["problem_text"]
            )

            with st.expander("Retrieved Knowledge Context"):
                for i, ctx in enumerate(retrieved_context, 1):
                    st.markdown(f"**Source {i}:** {ctx}")

            # -------- ROUTER --------
            router = RouterAgent()
            route = router.route(structured_problem)
            st.session_state.route = route

            st.caption(f"Detected problem type: `{route}`")

            if route == "unknown":
                st.warning(
                    "Problem intent could not be inferred automatically. "
                    "Please rephrase the problem."
                )
                st.stop()

            # -------- MEMORY LOOKUP --------
            memory = MemoryStore()
            past_solution = memory.find_similar(structured_problem["problem_text"])

            if past_solution:
                st.info("Similar problem found in memory.")
                st.write(past_solution["final_answer"])
                if st.checkbox("Reuse past solution"):
                    st.subheader("Final Answer")
                    st.success(past_solution["final_answer"])
                    st.stop()

            # -------- SOLVER --------
            solver = SolverAgent()
            solution = solver.solve(
                structured_problem=structured_problem,
                rag_context=retrieved_context,
                route=route
            )
            st.session_state.solution = solution

            # -------- VERIFIER --------
            verifier = VerifierAgent()
            verification = verifier.verify(
                structured_problem=structured_problem,
                solution=solution
            )

            if not verification["is_valid"]:
                st.error("Solution verification failed.")
                st.stop()

            # -------- CONFIDENCE --------
            st.subheader("Confidence Indicator")
            conf = st.session_state.confidence
            if conf >= 0.9:
                st.success(f"High confidence ({conf:.2f})")
            elif conf >= 0.75:
                st.warning(f"Medium confidence ({conf:.2f})")
            else:
                st.error(f"Low confidence ({conf:.2f})")

            # -------- OUTPUT --------
            st.subheader("Step-by-Step Solution")
            for step in solution["steps"]:
                st.write("•", step)

            st.subheader("Final Answer")
            st.success(solution["final_answer"])

            # -------- SAVE MEMORY --------
            memory.save({
                "problem_text": structured_problem["problem_text"],
                "route": route,
                "final_answer": solution["final_answer"],
                "steps": solution["steps"],
                "verified": True,
                "user_feedback": "unknown"
            })

            # -------- FEEDBACK --------
            st.subheader("Was this solution helpful?")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Correct"):
                    memory.save({
                        "problem_text": structured_problem["problem_text"],
                        "route": route,
                        "final_answer": solution["final_answer"],
                        "steps": solution["steps"],
                        "verified": True,
                        "user_feedback": "correct"
                    })
                    st.success("Feedback saved.")

            with col2:
                if st.button("❌ Incorrect"):
                    correction = st.text_area("Provide correction or comment")
                    if correction:
                        memory.save({
                            "problem_text": structured_problem["problem_text"],
                            "route": route,
                            "final_answer": solution["final_answer"],
                            "steps": solution["steps"],
                            "verified": False,
                            "user_feedback": "incorrect",
                            "correction": correction
                        })
                        st.success("Correction saved.")

        except HumanInTheLoopRequired as e:
            st.warning(f"HITL required: {str(e)}")
