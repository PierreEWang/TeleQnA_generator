import asyncio
import json
import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

import equation_extractor
from question_generator import generate_questions

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    st.error("Please set the OPENAI_API_KEY environment variable in your .env file.")
    st.stop()

APPROVED_QUESTIONS_FILE = "approved_questions.json"

def process_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_file_path = temp_file.name

    try:
        equations_with_context = equation_extractor.process_pdf_equations(temp_file_path)
    finally:
        try:
            os.unlink(temp_file_path)
        except PermissionError:
            st.warning("Unable to delete temporary file. It will be removed when you close the application.")

    return equations_with_context


def display_latex_equation(equation):
    st.latex(equation['equation'])


def load_approved_questions():
    if os.path.exists(APPROVED_QUESTIONS_FILE):
        try:
            with open(APPROVED_QUESTIONS_FILE, 'r') as f:
                content = f.read()
                if content.strip():
                    return json.loads(content)
                else:
                    return {}
        except json.JSONDecodeError:
            st.warning("Error reading approved questions file. Starting with an empty set.")
            return {}
    return {}


def save_approved_question(question, eq_num, category):
    approved_questions = load_approved_questions()
    question_number = len(approved_questions) + 1
    approved_questions[f"question_{question_number}"] = {
        "equation": eq_num,
        "category": category,
        "data": question
    }
    with open(APPROVED_QUESTIONS_FILE, 'w') as f:
        json.dump(approved_questions, f, indent=2)

    if 'approved_questions_session' not in st.session_state:
        st.session_state.approved_questions_session = {}
    st.session_state.approved_questions_session[f"question_{question_number}"] = {
        "equation": eq_num,
        "category": category,
        "data": question
    }


async def generate_questions_for_equation(equation, api_key, categories, model, num_questions_per_category):
    return await generate_questions(
        [equation],
        api_key,
        categories=categories,
        model=model,
        num_questions_per_category=num_questions_per_category
    )


async def generate_all_questions(equations, api_key, categories, model, num_questions_per_category):
    tasks = [
        generate_questions_for_equation(equation, api_key, categories, model, num_questions_per_category)
        for equation in equations
    ]
    results = await asyncio.gather(*tasks)
    return results

st.title("Equation Question Generator")

if 'equations' not in st.session_state:
    st.session_state.equations = None
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'approved_questions_session' not in st.session_state:
    st.session_state.approved_questions_session = {}

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("Extract Equations"):
        with st.spinner("Extracting equations..."):
            equations_with_context = process_pdf(uploaded_file)
            st.session_state.equations = equations_with_context
        st.success("Equations extracted successfully!")

if st.session_state.equations is not None:
    equation_options = [f"Equation {i + 1}" for i in range(len(st.session_state.equations))]
    selected_equations = st.multiselect("Select equations", equation_options)

    for equation in selected_equations:
        equation_index = equation_options.index(equation)
        st.subheader(f"{equation}")
        display_latex_equation(st.session_state.equations[equation_index])

    categories = [
        "Equation Interpretation",
        "Variable Identification",
        "Dimensional Analysis",
        "Equation Application",
        "Equation Manipulation",
        "Equation Comparison",
        "Conceptual Reasoning",
        "Context Integration",
        "Interdisciplinary Connection",
        "Masked Equation Infilling"
    ]
    selected_categories = st.multiselect("Select categories", categories)

    models = ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4"]
    selected_model = st.selectbox("Select GPT model", models, index=0)

    num_questions = st.number_input("Number of questions to generate per equation and category", min_value=1,
                                    max_value=5, value=1)

    if st.button("Generate Questions"):
        with st.spinner("Generating questions..."):
            async def generate():
                selected_equation_objects = [
                    st.session_state.equations[equation_options.index(eq)]
                    for eq in selected_equations
                ]
                all_questions = await generate_all_questions(
                    selected_equation_objects,
                    api_key,
                    categories=selected_categories,
                    model=selected_model,
                    num_questions_per_category=num_questions
                )
                return all_questions


            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            all_questions = loop.run_until_complete(generate())

            st.session_state.questions = all_questions
        st.success("Questions generated successfully!")

    if st.session_state.questions:
        if st.button("Clear Generated Questions"):
            st.session_state.questions = []
            st.success("Generated questions cleared!")
            st.rerun()

    if st.session_state.questions:
        st.subheader("Generated Questions")
        for eq_index, eq_questions in enumerate(st.session_state.questions):
            st.write(f"Equation {eq_index + 1}")
            for category_dict in eq_questions.values():
                for q_key, question in category_dict.items():
                    category = question['category']
                    with st.expander(f"{q_key}: {category}"):
                        st.write(f"Question: {question['question']}")
                        options = question['options']
                        if options:
                            st.write("Options:")
                            for opt, text in options.items():
                                st.write(f"  {opt}: {text}")
                        else:
                            st.write("No options available for this question.")
                        st.write(f"Answer: {question['answer']}")
                        st.write(f"Explanation: {question['explanation']}")

                        if st.button(f"Approve {q_key}", key=f"approve_{eq_index}_{category}_{q_key}"):
                            save_approved_question(question, eq_index + 1, category)
                            category_dict.pop(q_key)
                            if not category_dict:
                                eq_questions.pop(next(iter(eq_questions)))
                            if not eq_questions:
                                st.session_state.questions.pop(eq_index)
                            st.rerun()

    if st.session_state.approved_questions_session:
        st.subheader("Approved Questions (This Session)")
        for q_num, question_data in st.session_state.approved_questions_session.items():
            eq_num = question_data["equation"]
            category = question_data["category"]
            question = question_data["data"]

            with st.expander(f"{q_num}: Equation {eq_num} - {category}"):
                st.write(f"Question: {question['question']}")
                options = question['options']
                if options:
                    st.write("Options:")
                    for opt, text in options.items():
                        st.write(f"  {opt}: {text}")
                else:
                    st.write("No options available for this question.")
                st.write(f"Answer: {question['answer']}")
                st.write(f"Explanation: {question['explanation']}")

    else:
        st.write("No questions generated or approved yet.")
