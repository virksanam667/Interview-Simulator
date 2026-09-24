import os

from flask import Flask, render_template, request, session
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

# Needed so Flask can remember interview information
app.secret_key = os.getenv("FLASK_SECRET_KEY", "development-secret-key")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start_interview():

    resume = request.files["resume"]
    job_description = request.form["job_description"]

    # Extract resume text
    reader = PdfReader(resume)
    resume_text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            resume_text += page_text + "\n"

    # Ask AI for Question 1
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": """
You are a professional job interviewer.

Conduct a realistic interview using the candidate's
resume and target job description.

Ask ONE question at a time.
Do not give feedback during the interview.
Ask questions relevant to the candidate and position.
"""
            },
            {
                "role": "user",
                "content": f"""
RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Ask the first interview question.
"""
            }
        ]
    )

    first_question = response.choices[0].message.content

    # Remember interview information
    session["resume_text"] = resume_text
    session["job_description"] = job_description
    session["current_question"] = first_question
    session["question_number"] = 1
    session["transcript"] = []

    return render_template(
        "interview.html",
        question=first_question,
        question_number=1
    )


@app.route("/answer", methods=["POST"])
def answer():

    user_answer = request.form["answer"]

    current_question = session["current_question"]
    question_number = session["question_number"]

    # Save question + answer to transcript
    transcript = session["transcript"]

    transcript.append({
        "question": current_question,
        "answer": user_answer
    })

    session["transcript"] = transcript

    # Ask AI for adaptive follow-up
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": """
You are conducting a professional job interview.

Ask ONE question at a time.
Do NOT give feedback or grade the candidate.
Use the candidate's previous answer to decide the
best next question.

The next question may be:
- a follow-up to something interesting in their answer
- or a new question relevant to the resume and job

Keep the interview realistic.
"""
            },
            {
                "role": "user",
                "content": f"""
RESUME:
{session["resume_text"]}

JOB DESCRIPTION:
{session["job_description"]}

PREVIOUS QUESTION:
{current_question}

CANDIDATE ANSWER:
{user_answer}

Ask the best next interview question.
"""
            }
        ]
    )

    next_question = response.choices[0].message.content

    question_number += 1

    session["current_question"] = next_question
    session["question_number"] = question_number

    return render_template(
        "interview.html",
        question=next_question,
        question_number=question_number
    )


if __name__ == "__main__":zzz
    app.run(debug=True)