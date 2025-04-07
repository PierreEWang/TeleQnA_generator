import asyncio
import json

from openai import AsyncOpenAI

from question_prompts import prompts


class LatexJSONDecoder(json.JSONDecoder):
    def decode(self, s):
        s = s.replace('\\', '\\\\')  # Escape backslashes
        return super().decode(s)


async def generate_question(client, item, category, model, max_retries=3):
    prompt = prompts.get(category, "").format(equation=item['equation'], context=item['context'])
    if not prompt:
        print(f"Warning: No prompt found for category '{category}'. Skipping.")
        return None

    for attempt in range(max_retries):
        try:
            print(f"Generating question for category: {category} (Attempt {attempt + 1})")
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that generates multiple choice questions based on LaTeX equations and their context. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )

            response_content = response.choices[0].message.content

            # Try to find JSON content within the response
            try:
                json_start = response_content.index('{')
                json_end = response_content.rindex('}') + 1
                json_content = response_content[json_start:json_end]
                question = json.loads(json_content, cls=LatexJSONDecoder)
            except ValueError:
                raise json.JSONDecodeError("No JSON object could be decoded", response_content, 0)

            question['category'] = category

            return question

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for category {category}. Error details: {str(e)}")
            print(f"Raw response: {response_content}")
            if attempt == max_retries - 1:
                print(f"Max retries reached for category {category}. Skipping.")
                return None
            await asyncio.sleep(1)  # Wait a bit before retrying
        except Exception as e:
            print(f"Unexpected error for category {category}: {str(e)}")
            if attempt == max_retries - 1:
                print(f"Max retries reached for category {category}. Skipping.")
                return None
            await asyncio.sleep(1)  # Wait a bit before retrying

    return None


async def generate_questions(equations_with_context, api_key, categories, model, num_questions_per_category):
    client = AsyncOpenAI(api_key=api_key)
    all_questions = {}

    for idx, item in enumerate(equations_with_context):
        print(f"\n--- Processing equation {idx + 1} ---")
        print(f"Equation: {item['equation']}")

        tasks = []
        for category in categories:
            for _ in range(num_questions_per_category):
                tasks.append(generate_question(client, item, category, model))

        questions = await asyncio.gather(*tasks)
        validated_questions = {f"question_{i + 1}": q for i, q in enumerate(questions) if q is not None}

        all_questions[idx] = validated_questions
        print(f"Successfully generated and validated {len(validated_questions)} questions for equation {idx + 1}")

    return all_questions


def print_questions(questions):
    for eq_idx, eq_questions in questions.items():
        print(f"\nQuestions for Equation {eq_idx + 1}:")
        for q_num, q_data in eq_questions.items():
            print(f"\n{q_num}:")
            print(f"Category: {q_data['category']}")
            print(f"Question: {q_data['question']}")
            print("Options:")
            for opt, text in q_data['options'].items():
                print(f"  {opt}: {text}")
            print(f"Answer: {q_data['answer']}")
            print(f"Explanation: {q_data['explanation']}")
            print(f"Validation: {q_data['validation']}")


if __name__ == "__main__":
    # This section is for testing purposes only
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    sample_equations = [
        {
            'equation': r'E = mc^2',
            'context': 'This equation represents the mass-energy equivalence in Einstein\'s theory of special relativity.'
        },
        {
            'equation': r'F = ma',
            'context': 'This is Newton\'s Second Law of Motion, relating force, mass, and acceleration.'
        }
    ]

    categories = [
        "Equation Interpretation",
        "Variable Identification",
    ]


    async def main():
        questions = await generate_questions(sample_equations, api_key, categories=categories, model="gpt-3.5-turbo",
                                             num_questions_per_category=2)
        print_questions(questions)


    asyncio.run(main())
