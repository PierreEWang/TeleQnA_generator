import os
import ast
import pandas as pd
from ai.llm.agents import Validator


def validate_questions(questions_dict, context):
    # Filter out non-question entries
    filtered_questions = {key: value for key, value in questions_dict.items() if isinstance(value, dict)}

    # Debugging: Print the filtered questions dictionary
    print("Filtered Questions Dictionary:", filtered_questions)

    # Call the validation method with the filtered questions
    validated_questions, validation_cost = Validator.check_questions(filtered_questions, context)
    return validated_questions, validation_cost


def calculate_validity_percentage(validated_questions, total_questions):
    valid_count = len(validated_questions)
    percentage_valid = (valid_count / total_questions) * 100
    return percentage_valid


def process_directory(directory_path):
    total_questions = 0
    total_valid_questions = {}
    # List all text files in the given directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            questions = read_questions_from_file(file_path)
            document_context = "Simulated context for question validation."
            validated_questions, cost = validate_questions(questions, document_context)
            total_valid_questions.update(validated_questions)
            total_questions += len(questions)
    return total_valid_questions, total_questions


def main():
    # questions_directory = 'C:/Users/p50038325/Documents/Workspace/guignolosses/results/arxiv_papers/test'
    # validated_questions, total_questions = process_directory(questions_directory)
    # percentage_valid = calculate_validity_percentage(validated_questions, total_questions)
    #
    # print(f'Percentage of Valid Questions: {percentage_valid}%')
    # print(f'Total Questions Processed: {total_questions}')

    questions = pd.read_pickle('questions.pkl')
    print(questions.iloc[0])

if __name__ == '__main__':
    main()
