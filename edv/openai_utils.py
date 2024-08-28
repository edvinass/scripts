import openai
import os

def write_story():
    api_key = os.getenv("OPENAI_API_KEY")
    # Define the prompt or conversation
    prompt = "Write a short story about a brave knight who saved a village from a dragon."

    # Call the OpenAI API using the ChatGPT model (e.g., gpt-3.5-turbo)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Specify the model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},  # System message (optional)
            {"role": "user", "content": prompt},  # User's prompt or message
        ],
        max_tokens=150  # Adjust as needed for the response length
    )

    # Extract the assistant's response
    chat_response = response['choices'][0]['message']['content']

    # Print the assistant's response
    print(chat_response)
