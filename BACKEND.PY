from getpass import getpass
from groq import Groq

# Get API key without saving it in the file
api_key = getpass("Enter your Groq API key: ")

# Get prompt from user
user_prompt = input("Enter your prompt: ")

# Connect to Groq
client = Groq(api_key=api_key)

# Call the LLM
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": user_prompt
        }
    ]
)

# Print the LLM response
print("\nLLM Response:")
print(response.choices[0].message.content)