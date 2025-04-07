prompts = {
    "Equation Interpretation": """
Generate a multiple choice question that tests the student's ability to interpret the given equation.
The question should focus on the overall meaning or significance of the equation in its context.
Ensure that the options include common misinterpretations as distractors.

Equation: {equation}
Context: {context}

Format your response as a JSON object with the following structure:
{{
    "question": "What does this equation represent?",
    "options": {{
        "option 1": "[text]",
        "option 2": "[text]",
        "option 3": "[text]",
        "option 4": "[text]",
        "option 5": "[text]"
    }},
    "answer": "option x: [Correct interpretation]",
    "explanation": "[Detailed explanation of why this interpretation is correct and why others are incorrect]"
}}
""",

    "Variable Identification": """
Create a multiple choice question that tests the student's ability to identify and understand the variables in the given equation.
Focus on the meaning, units, or significance of one or more variables.

Equation: {equation}
Context: {context}

Format your response as a JSON object with the following structure:
{{
    "question": "What does [variable] represent in this equation?",
    "options": {{
        "option 1": "[text]",
        "option 2": "[text]",
        "option 3": "[text]",
        "option 4": "[text]",
        "option 5": "[text]"
    }},
    "answer": "option x: [Correct description of the variable]",
    "explanation": "[Detailed explanation of the variable's meaning and its role in the equation]"
}}
""",

    "Dimensional Analysis": """
Generate a multiple choice question that tests the student's understanding of the dimensions or units in the equation.
The question should focus on the dimensional consistency or the units of a specific term.

Equation: {equation}
Context: {context}

Format your response as a JSON object with the following structure:
{{
    "question": "What are the units of [term] in this equation?",
    "options": {{
        "option 1": "[text]",
        "option 2": "[text]",
        "option 3": "[text]",
        "option 4": "[text]",
        "option 5": "[text]"
    }},
    "answer": "option x: [Correct units]",
    "explanation": "[Detailed explanation of the dimensional analysis, including how the units are derived]"
}}
""",

    "Equation Application": """
Create a multiple choice question that tests the student's ability to apply the equation to a specific scenario or problem.
The question should involve using the equation to calculate a value or predict an outcome.

Equation: {equation}
Context: {context}

Format your response as a JSON object with the following structure:
{{
    "question": "Given [scenario details], what is the value of [variable]?",
    "options": {{
        "option 1": "[text]",
        "option 2": "[text]",
        "option 3": "[text]",
        "option 4": "[text]",
        "option 5": "[text]"
    }},
    "answer": "option x: [Correct calculated value]",
    "explanation": "[Step-by-step explanation of how to apply the equation to solve the problem]"
}}
""",

    "Equation Manipulation": """
Generate a multiple choice question that tests the student's ability to manipulate or rearrange the equation.
The question should involve solving for a different variable or combining the equation with another relevant equation.

Equation: {equation}
Context: {context}

Format your response as a JSON object with the following structure:
{{
    "question": "How would you rearrange this equation to solve for [variable]?",
    "options": {{
        "option 1": "[text]",
        "option 2": "[text]",
        "option 3": "[text]",
        "option 4": "[text]",
        "option 5": "[text]"
    }},
    "answer": "option x: [Correct rearranged equation]",
    "explanation": "[Step-by-step explanation of how to manipulate the equation correctly]"
}}
""",

    "Equation Comparison": """
Create a multiple choice question that compares the given equation to another related equation or a variant of the same equation.
The question should test the student's ability to understand the similarities, differences, or relationships between equations.

Equation: {equation}
Context: {context}

Format your response as a JSON object with the following structure:
{{
    "question": "How does this equation relate to [another equation in the same field]?",
    "options": {{
        "option 1": "[text]",
        "option 2": "[text]",
        "option 3": "[text]",
        "option 4": "[text]",
        "option 5": "[text]"
    }},
    "answer": "option x: [Correct relationship or comparison]",
    "explanation": "[Detailed explanation of the relationship between the equations, highlighting key similarities or differences]"
}}
""",

    "Conceptual Reasoning": """
Generate a multiple choice question that tests the student's conceptual understanding of the principles underlying the equation.
The question should focus on the theoretical foundations or implications of the equation rather than its mathematical form.

Equation: {equation}
Context: {context}

Format your response as a JSON object with the following structure:
{{
    "question": "What fundamental concept does this equation demonstrate?",
    "options": {{
        "option 1": "[text]",
        "option 2": "[text]",
        "option 3": "[text]",
        "option 4": "[text]",
        "option 5": "[text]"
    }},
    "answer": "option x: [Correct concept]",
    "explanation": "[Detailed explanation of the concept, its relationship to the equation, and why other options are incorrect]"
}}
""",

    "Context Integration": """
Create a multiple choice question that tests the student's ability to integrate the equation with its broader context or field of study.
The question should involve understanding how the equation fits into larger theories or its practical applications.

Equation: {equation}
Context: {context}

Format your response as a JSON object with the following structure:
{{
    "question": "In what practical scenario would this equation be most relevant?",
    "options": {{
        "option 1": "[text]",
        "option 2": "[text]",
        "option 3": "[text]",
        "option 4": "[text]",
        "option 5": "[text]"
    }},
    "answer": "option x: [Correct practical application]",
    "explanation": "[Detailed explanation of why this application is most relevant, including how the equation is used in this context]"
}}
""",

    "Interdisciplinary Connection": """
Generate a multiple choice question that explores the connections between this equation and concepts from other disciplines.
The question should test the student's ability to recognize how the equation or its principles apply across different fields.

Equation: {equation}
Context: {context}

Format your response as a JSON object with the following structure:
{{
    "question": "Which concept from [another discipline] is most closely related to this equation?",
    "options": {{
        "option 1": "[text]",
        "option 2": "[text]",
        "option 3": "[text]",
        "option 4": "[text]",
        "option 5": "[text]"
    }},
    "answer": "option x: [Correct interdisciplinary connection]",
    "explanation": "[Detailed explanation of the interdisciplinary connection, including how the principles of the equation apply in another field]"
}}
""",

    "Masked Equation Infilling": """
Create a multiple choice question based on the given equation, where part of the equation is masked (hidden).
The question should ask the student to identify the correct missing part.

Original Equation: {equation}
Context: {context}

First, create a masked version of the equation by replacing a crucial part with <MASK>.
Then, generate a question asking what should replace the <MASK>.

Format your response as a JSON object with the following structure:
{{
    "question": "In the equation: [Masked equation], what should replace <MASK>?",
    "options": {{
        "option 1": "[text]",
        "option 2": "[text]",
        "option 3": "[text]",
        "option 4": "[text]",
        "option 5": "[text]"
    }},
    "answer": "option x: [Correct missing part]",
    "explanation": "[Detailed explanation of why this is the correct part to fill the mask, including how it relates to the equation's meaning and context]"
}}
"""
}
