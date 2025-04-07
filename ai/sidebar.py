from typing import Any
import os
import streamlit as st
import numpy as np
from parsers.arxiv_reader import *
from parsers.ieee_standards_reader import *
from parsers.pdf_reader import *
from docx import Document
from PyPDF2 import PdfReader
from copy import deepcopy
import time
from llm.agents import Generator, Validator
from question_analyser import QuestionAnalyser


class Sidebar:
    def __reinit_doc(self):
        if ".docx" in st.session_state.tex_file.name:
            DocxNode._n_nodes = 0
            doc = Document(st.session_state.tex_file)
            paragraphs = [p.text for p in doc.paragraphs]
            st.session_state.doc = StandardsDoc(paragraphs)
        elif ".pdf" in st.session_state.tex_file.name:
            PDFNode._n_nodes = 0
            doc = PdfReader(st.session_state.tex_file)
            st.session_state.doc = PDFDoc(doc)
        else:
            TexNode._n_nodes = 0
            doc = st.session_state.tex_file.read().decode("utf-8")
            st.session_state.doc = ArxivDoc(doc)

    @staticmethod
    def is_already_analysed(document_name : str) -> bool:
        file_path = os.path.join("results", "verified_documents.txt")
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                if document_name in content:
                    return True
                else:
                    return False
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
            return False
        
    def set_document_visualized(document_name : str):        
        file_path = os.path.join("results", "verified_documents.txt")
        try:
            with open(file_path, 'a') as file:
                file.write(f'\n{document_name}')  # Add a newline at the end
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")

    @classmethod
    def show_with_counts(cls, _node, _ind):
        _s = _node.title.find('{')+1
        _e = _node.title.find('}')
        if _s < _e:
            _text = _node.title[_s:_e] + ": {} words \n ".format(_node.nwords)
        else:
            _text = _node.title + ": {} words \n ".format(_node.nwords)

        st.session_state._sections_ids += [_node.attributes['id']]
        st.session_state._sections_text += [_text]
        st.session_state._sections_counts += [_node.nwords]

    def __init__(self) -> Any:
        with st.sidebar:
            st.subheader("Tex file")
            st.session_state.tex_file = st.file_uploader(
                "Upload the tex file and click on 'Process'", 
                accept_multiple_files=False
            )

            if st.session_state.tex_file is None:
                default_title = "unknown" 
            elif ".docx" in st.session_state.tex_file.name:
                default_title = st.session_state.tex_file.name[:-5]
            else:
                default_title = st.session_state.tex_file.name[:-4]

            already_analysed = Sidebar.is_already_analysed(default_title)
            if already_analysed:
                st.markdown("<span style='color: red;'>Document already analysed</span>", unsafe_allow_html=True)
                
            st.session_state.paper_title = st.text_input(
                "Title of the paper",
                default_title
            )

            st.session_state.tag = st.text_input(
                "Tag to add to the question",
                ""
            )

            if st.button("Process"):
                with st.spinner("Processing"):
                    # Construct Arxiv doc
                    self.__reinit_doc()

            if st.session_state.doc is not None:
                # Show doc structure with word counts
                st.session_state.summary = ""

                st.session_state._sections_ids = []
                st.session_state._sections_text = []
                st.session_state._sections_counts = []




                st.session_state.doc.apply(self.show_with_counts, reccursive=False)


                selected_sections = st.multiselect(
                    'Select section',
                    ["All sections"] + st.session_state._sections_text,
                    # max_selections=4
                )



                for _selected in selected_sections:
                    if _selected == "All sections":

                        min_words = st.slider("Minimum number of words", 0, 5_000, 1_000, 500)
                        
                        for section in st.session_state._sections_text:
                            nwords= int(section.split(" ")[-4])
                            if min_words < nwords:
                                
                                selected_sections.append(section)

                                idx = np.where(np.array(st.session_state._sections_text)==section)[0][0]
                                st.markdown(f"### Section {section}")
                            


                        break

                    idx = np.where(np.array(st.session_state._sections_text)==_selected)[0][0]
                    st.markdown("### Selection nwords: {}".format(st.session_state._sections_counts[idx]))

                st.sidebar.write(" \n ")
                n_questions = st.sidebar.slider('How many questions to generate?', 5, 25, 1)
                n_validators = st.slider("Number of validators", 1,5,1,1)

                if st.button("Generate"):
                    st.session_state.selected_sections = {}
                    for _selected in selected_sections:
                        if _selected == "All sections":
                            continue

                        st.session_state.selected_sections[_selected] = {}

                        st.session_state.selected_sections[_selected]['doc'] = deepcopy(st.session_state.doc)

                        idx = np.where(np.array(st.session_state._sections_text) == _selected)[0][0]


                        _sec = st.session_state.selected_sections[_selected]['doc']._find_func(
                            lambda _node: _node.attributes['id'] == idx
                        )[0]
                        _sec.add_attribute("selected", True)

                        with st.spinner("Generation and Validation: {}".format(_selected)):
                            tic = time.time()
                            # Generate questions
                            stop = False
                            _rep = 0
                            cost = 0
                            while not stop:
                                questions, generation_cost, context = Generator.from_arxiv_doc(
                                    st.session_state.selected_sections[_selected]['doc'],
                                    n_questions-_rep
                                )

                                if st.session_state.tag != "":
                                    for q in questions:
                                        questions[q]['question'] += " " + st.session_state.tag

                                # Validate questions

                                # remove keywords
                                pop_keys = set()
                                for question_name, q in questions.items():
                                    for keyword in Validator.KEYWORDS:
                                        
                                        if (question_name in pop_keys):
                                            break

                                        if keyword in q["question"].lower():
                                            pop_keys.add(question_name)
                                
                                for k in pop_keys:
                                    questions.pop(k)
                                    

                                accepted_questions = questions
                                for idx in range(n_validators):
                                    accepted_questions,  rejected_questions, validation_cost, val_output = \
                                        Validator.check_questions_with_val_output(accepted_questions, context)
                                    
                                    if len(rejected_questions) > 0:
                                        results_path = "results/arxiv_papers/rejected_questions/"
                                        QuestionAnalyser.save_questions_as_json(rejected_questions, results_path, "")
                                        
                                _rep += 1
                                cost += generation_cost + validation_cost

                                if len(accepted_questions) > 0 or _rep >= 2:
                                    stop = True

                            toc = time.time()

                            # Output results
                            st.session_state.selected_sections[_selected]['cost'] = cost
                            st.session_state.selected_sections[_selected]['generation_time'] = toc - tic
                            st.session_state.selected_sections[_selected]['generated_questions'] = questions
                            st.session_state.selected_sections[_selected]['validator_questions'] = val_output
                            st.session_state.selected_sections[_selected]['accepted_questions'] = accepted_questions
                            st.session_state.selected_sections[_selected]['rejected_questions'] = rejected_questions

                    if len(st.session_state.selected_sections)==0:
                        st.markdown("## Select a section first")
                    Sidebar.set_document_visualized(default_title)


                for _sec_name, _sec_dic in st.session_state.selected_sections.items():

                    if all([s in _sec_dic for s in ['cost', "generation_time", "accepted_questions"]]):
                        st.write(" \n \n ")
                        st.markdown("#### {}".format(_sec_name))
                        st.markdown("Number of accepted questions: {}".format(
                            len(_sec_dic['accepted_questions'])  
                        ))
                        # st.write(_sec_dic['accepted_questions'])
                        st.markdown("Generation + Validation cost: {} $".format(
                            round(_sec_dic['cost'], 2)
                        ))
                        st.markdown("Elapsed time: {} s".format(
                            round(_sec_dic['generation_time'], 2)
                        ))
            