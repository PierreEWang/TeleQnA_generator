import streamlit as st
import os
import json
from question_analyser import QuestionAnalyser, Status
from sidebar import Sidebar
from llm.agents import ModelType

def bold(s):
    return "\033[1m" + s + "\033[0m"


def print_question(question_num, question_data, n_questions_before):
    st.markdown("##### Question {}: {}".format(question_num+n_questions_before, question_data["question"]))
    st.write("Options:")
    for option_num in range(1, 6):
        option_key = "option {}".format(option_num)
        if option_key in question_data:
            st.write("{}. {}".format(option_num, question_data[option_key]))

    answer_key = "answer"
    if answer_key in question_data:
        st.markdown("###### Answer: {}".format(question_data[answer_key]))
    comment_key = "explanation"
    if comment_key in question_data:
        st.markdown("###### Explanation: {}".format(question_data[comment_key]))




def main():

    st.set_page_config(page_title="Generate questions from tex",
                       page_icon=":books:")

    if "doc" not in st.session_state:
        st.session_state.doc = None

    st.header("Generate questions from tex")


    #-------------------------------------------------------------------
    # Side bar to select file and sections
    #-------------------------------------------------------------------
    Sidebar()
    

    #---------------------------------------------
    # Print questions
    #---------------------------------------------
    if "selected_sections" not in st.session_state:
        st.session_state.selected_sections = {}

    # Generator
    st.markdown("## Generator")
    show_gen = st.checkbox("Show questions", key="show_gen")
    QuestionAnalyser.get_generated_questions(show_gen, ModelType.GENERATOR)


    # Validator
    st.markdown("---")
    st.markdown("## Validator")
    show_val = st.checkbox("Show questions", key="show_val")
    QuestionAnalyser.get_generated_questions(show_val, ModelType.VALIDATOR)



    # Accepted questions
    st.markdown("---")
    st.markdown("## Accepted questions")
    show_accepted = st.checkbox("Show questions", key="show_accepted")
    QuestionAnalyser.get_accepted_questions(show_accepted)

    

    st.markdown("---")
    st.markdown("## Rejected questions")
    show_rejected = st.checkbox("Show questions", key="show_rejected")
    QuestionAnalyser.get_rejected_questions(show_rejected)

   

    st.write("\n \n \n")

    st.markdown("***")
    st.markdown("## All previously saved (accepted) questions")
    show_all_accepted = st.checkbox("Show all saved questions")
    QuestionAnalyser.get_all_saved_questions(show_all_accepted, Status.ACCEPTED)

    st.markdown("***")
    st.markdown("## All previously saved (rejected) questions")
    show_all_rejected = st.checkbox("Show all saved questions", key = "rejected_saved")
    QuestionAnalyser.get_all_saved_questions(show_all_rejected, Status.REJECTED)
    
    n_saved_questions = QuestionAnalyser.get_num_saved_questions()
    st.markdown("***")
    st.markdown(f"## Number of saved questions: {n_saved_questions}")


if __name__ == '__main__':
    main()