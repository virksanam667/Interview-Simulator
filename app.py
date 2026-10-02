import os

from flask import Flask, render_template, request, session, redirect, url_for
from groq import Groq
from dotenv import load_dotenv
from markdown_it import MarkdownIt


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# LOAD SYSTEM PROMPT FROM system_prompt.txt
# =========================================================

with open("system_prompt.txt", "r", encoding="utf-8") as file:
    system_prompt = file.read()


# Temporary diagnostic:
# This proves that app.py is actually reading system_prompt.txt
print("\n========================================")
print("SYSTEM PROMPT LOADED:")
print("========================================")
print(system_prompt)
print("========================================\n")


# =========================================================
# SET UP FLASK
# =========================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "class-secret-key"
)


# =========================================================
# CONNECT TO GROQ
# =========================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "openai/gpt-oss-20b"


# =========================================================
# MARKDOWN RENDERER
# =========================================================

md = MarkdownIt()


# =========================================================
# MAIN CHAT PAGE
# =========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    # Create conversation memory
    if "messages" not in session:
        session["messages"] = []


    # -----------------------------------------------------
    # USER SUBMITS MESSAGE
    # -----------------------------------------------------

    if request.method == "POST":

        user_prompt = request.form.get(
            "user_prompt",
            ""
        ).strip()


        if user_prompt:

            messages = session["messages"]


            # -------------------------------------------------
            # SAVE USER MESSAGE
            # -------------------------------------------------

            messages.append({
                "role": "user",
                "content": user_prompt
            })


            # -------------------------------------------------
            # BUILD GROQ CONVERSATION
            # -------------------------------------------------

            groq_messages = [

                {
                    "role": "system",

                    "content": system_prompt
                }

            ]


            # Add entire previous conversation
            groq_messages.extend(messages)


            # Temporary diagnostic
            print("\n----------------------------------------")
            print("SYSTEM PROMPT BEING SENT TO GROQ:")
            print("----------------------------------------")
            print(system_prompt)

            print("\nUSER MESSAGE:")
            print(user_prompt)

            print("----------------------------------------\n")


            # -------------------------------------------------
            # CALL GROQ
            # -------------------------------------------------

            response = client.chat.completions.create(

                model=MODEL,

                messages=groq_messages,

                temperature=0.3

            )


            # -------------------------------------------------
            # GET LLM RESPONSE
            # -------------------------------------------------

            assistant_response = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )


            print("\nLLM RESPONSE:")
            print(assistant_response)
            print("\n")


            # -------------------------------------------------
            # CONVERT MARKDOWN TO HTML
            # -------------------------------------------------

            assistant_response_html = md.render(
                assistant_response
            )


            # -------------------------------------------------
            # SAVE AI RESPONSE INTO MEMORY
            # -------------------------------------------------

            messages.append({

                "role": "assistant",

                "content": assistant_response_html

            })


            session["messages"] = messages


        # Prevent duplicate POST after refresh
        return redirect(url_for("home"))


    # -----------------------------------------------------
    # DISPLAY PAGE
    # -----------------------------------------------------

    return render_template(

        "index.html",

        messages=session["messages"]

    )


# =========================================================
# CLEAR CHAT
# =========================================================

@app.route("/clear", methods=["POST"])
def clear_chat():

    session["messages"] = []

    return redirect(url_for("home"))


# =========================================================
# RUN FLASK
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)