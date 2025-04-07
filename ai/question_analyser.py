import streamlit as st
from typing import Dict
import os
from pathlib import Path
import json
from enum import Enum
from llm.agents import ModelType

class Status(Enum):
    ACCEPTED = 1
    REJECTED = 0
    

class QuestionAnalyser:
    # avoiding typos
    ACCEPTED_QUESTIONS : str = "accepted_questions"
    REJECTED_QUESTIONS : str = "rejected_questions"
    GENERATED_QUESTIONS : str = "generated_questions"
    TO_DELETE_KEYS : str = "to_delete_keys"

    @classmethod
    def print_question(
        cls,
        question_num : int, 
        question_data : Dict, 
        n_questions_before : int
    ):
        
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

    @classmethod
    def save_questions_as_json(
        cls,
        questions : Dict,
        path : str,
        section_name : str
    ):
        """Saves questions as json

        Args:
            questions (Dict): questions
            path (str): path to save
            section_name (str): section from paper
        """        
        Path(path).mkdir(parents=True, exist_ok=True)
        count = len(os.listdir(path))

        questions['paper_title'] = st.session_state.paper_title
        questions['section'] = section_name

        with open(os.path.join(path, f"{count+1}-{questions['paper_title']}.txt"), 'w') as f:
            res_str = json.dumps(questions)
            f.write(res_str)

    @classmethod
    def get_generated_questions(
        cls,
        show: bool,
        model : ModelType
    ):
        for _sec_name, _sec_dic in st.session_state.selected_sections.items():
            if show:
                st.markdown("### {}".format(_sec_name))
                n_questions_before = 0

                if model == ModelType.GENERATOR:
                    key = "generated_questions"

                if (model == ModelType.VALIDATOR):
                    key = "validator_questions"

                for i, (question_num, question_data) in enumerate(_sec_dic[key].items()):
                    st.write("---------------------")
                    cls.print_question(i + 1, question_data, n_questions_before)
                st.write(" \n ")
        
    @classmethod
    def get_accepted_questions(
        cls, 
        show : bool
    ):
        """shows accepted questions in the app

        Args:
            show (bool): boolean value that represents 
            if the checkbox is checked.
        """        
        for _sec_name, _sec_dic in st.session_state.selected_sections.items():
            if cls.TO_DELETE_KEYS not in _sec_dic:
                _sec_dic[cls.TO_DELETE_KEYS] = []

            if show:
                n_questions_before = 0
                st.markdown("### {}".format(_sec_name))
                for i, (question_num, question_data) in enumerate(_sec_dic[cls.ACCEPTED_QUESTIONS].items()):
                    if isinstance(question_data, str):
                        st.write("---------------------")
                        st.write(question_data)
                    else:
                        st.write("---------------------")
                        cls.print_question(i + 1, question_data, n_questions_before)

                        if st.button("Delete", key="del_{}_{}".format(_sec_name, i)):
                            _sec_dic[cls.TO_DELETE_KEYS] += [list(_sec_dic[cls.ACCEPTED_QUESTIONS])[i]]
                        if list(_sec_dic[cls.ACCEPTED_QUESTIONS])[i] in _sec_dic[cls.TO_DELETE_KEYS]:
                            st.write("deleted")


                n_questions_to_save = len(_sec_dic[cls.ACCEPTED_QUESTIONS]) - len(_sec_dic[cls.TO_DELETE_KEYS])

                st.write("Number of questions to save: {}".format(n_questions_to_save))
                if n_questions_to_save > 0:

                    st.markdown("***")

                    if st.button("Save questions {}".format(_sec_name)):

                        for del_key in _sec_dic[cls.TO_DELETE_KEYS]:
                            if del_key in _sec_dic[cls.ACCEPTED_QUESTIONS]:
                                _sec_dic[cls.ACCEPTED_QUESTIONS].pop(del_key)

                        arxiv_paper_id = "accepted_questions"
                        results_path = "results/arxiv_papers/{}/".format(arxiv_paper_id)
                        st.session_state.result_path = results_path
                        
                        accepted_questions = _sec_dic[cls.ACCEPTED_QUESTIONS]

                        cls.save_questions_as_json(
                            accepted_questions,
                            results_path,
                            _sec_name
                        )
                        

                        _sec_dic["saved"] = True

                    if "saved" in _sec_dic:
                        if _sec_dic["saved"]:
                            st.markdown("Saved !")

    @classmethod
    def get_rejected_questions(
        cls,
        show : bool
    ):
        """Shows rejected questions in the app

        Args:
            show (bool): boolean value that represents 
            if the checkbox is checked.
        """        

        for _sec_name, _sec_dic in st.session_state.selected_sections.items():

            if show:
                n_questions_before = 0
                st.markdown("### {}".format(_sec_name))

                for question_id, (question_name, question_data) in enumerate(_sec_dic[cls.REJECTED_QUESTIONS].items()):
                    if isinstance(question_data, str):
                        st.write("---------------------")
                        st.write(question_data)

                    else:
                        cls.print_question(question_id+1, question_data, n_questions_before)
                    
                n_questions_to_save = len(_sec_dic[cls.REJECTED_QUESTIONS])

                st.write("Number of rejected questions: {}".format(n_questions_to_save))
                if n_questions_to_save > 0:

                    st.markdown("***")

                    if st.button("Save questions {}".format(_sec_name), key = _sec_name):

                        arxiv_paper_id = "rejected_questions"
                        results_path = "results/arxiv_papers/{}/".format(arxiv_paper_id)
                        st.session_state.result_path = results_path
                        
                        rejected_questions = _sec_dic[cls.REJECTED_QUESTIONS]

                        cls.save_questions_as_json(
                            rejected_questions,
                            results_path,
                            _sec_name
                        )
                            

                        _sec_dic["saved_rejected_questions"] = True

                if "saved_rejected_questions" in _sec_dic:
                    if _sec_dic["saved_rejected_questions"]:
                        st.markdown("Saved !")

    @classmethod
    def get_all_saved_questions(cls, show : bool, status : Status):
        if status == Status.ACCEPTED:
            arxiv_paper_id = "accepted_questions"

        elif status == Status.REJECTED:
            arxiv_paper_id = "rejected_questions"


        results_path = "results/arxiv_papers/{}/".format(arxiv_paper_id)
        
        if show:
            files = os.listdir(results_path)
            n_questions_before = 0

            for file in files:
                with open(os.path.join(results_path, file)) as f:
                    loaded_json = f.read()

                loaded_questions = json.loads(loaded_json)
                
                for i, (question_num, question_data) in enumerate(loaded_questions.items()):
                    if isinstance(question_data, str):
                        continue
                        # st.write("---------------------")
                        # st.write(question_data)
                    else:
                        st.write("---------------------")
                        cls.print_question(n_questions_before+1, question_data, 0)
                        n_questions_before += 1
    
    @classmethod
    def get_num_saved_questions(cls):
        
        arxiv_paper_id = "accepted_questions"

        results_path = "results/arxiv_papers/{}/".format(arxiv_paper_id)
    
        files = os.listdir(results_path)
        n_questions = 0

        for file in files:
            with open(os.path.join(results_path, file)) as f:
                loaded_json = f.read()

            loaded_questions = json.loads(loaded_json)
            
            for i, (question_num, question_data) in enumerate(loaded_questions.items()):
                if isinstance(question_data, str):
                    continue
                    # st.write("---------------------")
                    # st.write(question_data)
                else:
                    n_questions += 1

        return n_questions

