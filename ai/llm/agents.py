import openai
import ast
from copy import deepcopy
import json
from enum import Enum
# import streamlit as st
from ai.parsers.arxiv_reader import *

openai.api_key = "sk-proj-dNOfpBceQvxQOp62S930T3BlbkFJaszKg9TjVbGDJjLNlHYS"

class ModelType(Enum):
    GENERATOR = 1
    VALIDATOR = 2

class Generator:
    
    model = "gpt-3.5-turbo-16k"
    
    syst_prompt = """
    Please provide me with multiple-choice questions and their correct answers based on the content of a document or a specific context. The questions should be answerable by someone expert in the field of the document's content without having seen the specific document. Please omit specific mentions to the document itself and focus on the information present in the document. There should be between 3 to 5 options per question. The output should be in a json format, 
    {
    "question 1": {
    "question": question,
    "option 1": option,
    "option 2": option,
    etc,
    "answer": "option {answer id}: {answer string}",
    "explanation": {Explain the answer to the question in one sentence}
    }
    }
    When acronyms are used, make sure you provide the definitions. Avoid at all costs providing in the multiple-choice questions anything containing the word \cite in it. Make sure to avoid including sophisticated equations in the questions or answers. Please omit specific mentions to the document itself and focus on the information present in the document.
    """
    # Use \cite{doc} instead of this document/survey/paper/review.
    #"comment": {are all the acronyms in the question defined and does the question refer explictly to the document at hand?}
    context_length = 9000
    token_cost = 0.003

    @classmethod
    def from_arxiv_doc(cls, arxiv_doc:ArxivDoc, n_questions=10):
        
        user_prompt = "I need {} questions. ".format(n_questions)
        context = ""
        
        selected_sections = arxiv_doc._find_func(
            lambda _node: 'selected' in _node.attributes and _node.attributes['selected'] == True
        )
        
        for sec in selected_sections:
            context += sec.content
            context += "\n"
            
        generated_output = openai.ChatCompletion.create(
          model=Generator.model,
          messages=[
              {"role": "system", "content": Generator.syst_prompt},
              {"role": "user", "content":  user_prompt+ "Here is the context:"+context }, 
               # {"role": "user", "content": context},
               # {"role": "system", "content": Generator.syst_prompt+user_prompt},
                
            ]
        )
        
        generation_cost = Generator.token_cost * generated_output.usage.total_tokens / 1000
        
        questions_str = generated_output.choices[0].message.content
        questions_str = questions_str.replace('"\n', '",\n')
        
        # st.write(questions_str)
        parsed_question = ast.literal_eval(questions_str)
        
        return parsed_question, generation_cost, context
    
class Validator:
    model = "gpt-3.5-turbo-16k"
    
    syst_prompt = """
    Please provide the answers to the following multiple choice questions based on the content of a document I will provide. The questions will be in a JSON format, the answers should also be in a JSON format as follows:
     {
    "question 1": {
    "question": question,
    "answer": "option {answer id}: {answer string}"
    },
    ...
    }
    """
    KEYWORDS = [
        "this", 
        "section", 
        "chapter", 
        "table", 
        "solution", 
        "figure", 
        "step",
        "document",
        "appendix",
        "annex",
        "clause"
    ]
    token_cost = 0.003
    
    @classmethod
    def check_questions(cls, questions_dict, context):
        
        questions_only = deepcopy(questions_dict)
        answers_only =  {}
        for q in questions_dict:
            answers_only[q] = {
                "question": questions_dict[q]["question"],
                "answer": questions_dict[q]["answer"]
            }
    
            questions_only[q].pop("answer")
        
        user_prompt = "Here is the document: \n "
        user_prompt += context
        
        user_prompt += "\n \n Here are the questions: \n"
        user_prompt += json.dumps(questions_only)
        
        generated_output = openai.ChatCompletion.create(
          model=Validator.model,
          messages=[
                {"role": "system", "content": Validator.syst_prompt},
                {"role": "user", "content": user_prompt},
              
            ]
        )
        
        validation_cost = Validator.token_cost * generated_output.usage.total_tokens / 1000
        
        predicted_answers_str = generated_output.choices[0].message.content
        predicted_answers_str = predicted_answers_str.replace('"\n', '",\n')
        
        parsed_predicted_answers = ast.literal_eval(predicted_answers_str)
        
        accepted_questions = {}
        
        for q in questions_dict:
            if q in parsed_predicted_answers and q in answers_only:
                if parsed_predicted_answers[q] == answers_only[q]:
                    if "this" not in parsed_predicted_answers[q]["question"].lower():
                        accepted_questions[q] = questions_dict[q]
        
        return accepted_questions, validation_cost

    @classmethod
    def check_questions_with_val_output(cls, questions_dict, context):

        questions_only = deepcopy(questions_dict)
        answers_only = {}
        for q in questions_dict:
            answers_only[q] = {
                "question": questions_dict[q]["question"],
                "answer": questions_dict[q]["answer"]
            }

            questions_only[q].pop("answer")
            if "explanation" in questions_only[q]:
                questions_only[q].pop("explanation")
                

        user_prompt = "Here is the document: \n "
        user_prompt += context

        user_prompt += "\n \n Here are the questions: \n"
        user_prompt += json.dumps(questions_only)

        generated_output = openai.ChatCompletion.create(
            model=Validator.model,
            messages=[
                {"role": "system", "content": Validator.syst_prompt},
                {"role": "user", "content":  user_prompt},
            ]
        )

        validation_cost = Validator.token_cost * generated_output.usage.total_tokens / 1000

        predicted_answers_str = generated_output.choices[0].message.content
        predicted_answers_str = predicted_answers_str.replace('"\n', '",\n')

        parsed_predicted_answers = ast.literal_eval(predicted_answers_str)

        for q in parsed_predicted_answers:
            if "answer" in parsed_predicted_answers[q] and "question" in parsed_predicted_answers[q]:
                parsed_predicted_answers[q] = {
                    "question": parsed_predicted_answers[q]["question"],
                    "answer": parsed_predicted_answers[q]["answer"]
                }

        accepted_questions = {}
        rejected_questions = {}

        for q in questions_dict:
            if q in parsed_predicted_answers and q in answers_only:
                if parsed_predicted_answers[q] == answers_only[q]:
                    valid_question = True

                    for keyword in Validator.KEYWORDS:
                        if keyword in parsed_predicted_answers[q]["question"].lower():
                            valid_question = False
                            rejected_questions[q]= questions_dict[q]
                            break
                    if valid_question:
                        accepted_questions[q] = questions_dict[q]

                else:
                    rejected_questions[q] = questions_dict[q]
                        #if "remark" in parsed_predicted_answers[q]:
                           # accepted_questions[q]["remark"] = parsed_predicted_answers[q]["remark"]
        
        
        return accepted_questions, rejected_questions, validation_cost, parsed_predicted_answers
    
class MultipleValidators():
    def __init__(self, n_validators : int) -> None:
        self.n_validators = n_validators