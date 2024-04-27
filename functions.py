import openai

def generate_question_and_get_answer(text):
    question = "For the givem text provide all concepts and relations between them. \
                Present the result in turtle format using Rdfs schema, schema.org and example.org for the enteties.\nText: " \
                + text

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=question,
        max_tokens=50,
        temperature=0.7
    )

    answer = response['choices'][0]['text'].strip()
    return answer

