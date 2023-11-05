import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
def advise(food, goal_calorie, goal, age, height, weight, gender, exercise):
    prompt = f"I need advice for my diet. I am {age} years old. I weight {weight} kgs, and I am {gender}. I excersise {exercise}.I ate {food} today. My goal calorie is {goal_calorie}. My goal is to {goal}. Give a answer like a professional health expert."
    response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=prompt, max_tokens=1000, stream=True)

    full_response = ""  # Initialize an empty string to collect the chunks
    for chunk in response:
        full_response += chunk["choices"][0]["text"]

    return full_response.strip()


    

