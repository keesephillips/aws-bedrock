import os, json, html, time
from flask import Flask, request, session, redirect, url_for, make_response
import boto3

REGION = os.getenv("AWS_REGION", "us-east-2")      
PROMPT_ARN = os.getenv(
    "BEDROCK_PROMPT_ARN",
    "arn:aws:bedrock:us-east-2:381492212823:prompt/QSG8T98UZM"
) 
PROMPT_VAR_NAME = os.getenv("PROMPT_VAR_NAME", "user_input") 

bedrock = boto3.client("bedrock-runtime", region_name=REGION)


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "8200E54A64AF2F8FFB509F99AFE8CF4C")  

HTML_SKELETON = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AIPI561 Chatbot</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    .msg {{ margin: .8em 0; }}
    .user {{ color: blue; font-weight: bold; }}
    .assistant {{ color: green; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Chatbot via Amazon Bedrock</h1>
  <form method="POST">
    <input type="text" name="message" placeholder="Type your message…" required autofocus>
    <button type="submit">Send</button>
  </form>
  {conversation}
</body>
</html>
"""

def render_conversation(turns):
    rows = []
    for t in turns:
        role_cls = "user" if t["role"] == "user" else "assistant"
        label = "You" if t["role"] == "user" else "Chatbot"
        rows.append(
            f'<div class="msg"><span class="{role_cls}">{label}:</span> {html.escape(t["text"])}</div>'
        )
    return "\n".join(rows)

@app.route("/", methods=["GET", "POST"])
def index():
    if "conversation" not in session:
        session["conversation"] = []

    if request.method == "POST":
        user_text = request.form.get("message", "").strip()
        if user_text:
            session["conversation"].append({"role": "user", "text": user_text})

            try:
                resp = bedrock.converse(
                    modelId=PROMPT_ARN,
                    promptVariables={PROMPT_VAR_NAME: {"text": user_text}},
                    inferenceConfig={"maxTokens": 1024},
                )

                assistant_text = resp["output"]["message"]["content"][0]["text"]
            except Exception as exc:
                assistant_text = f"Error: {exc}"

            session["conversation"].append({"role": "assistant", "text": assistant_text})

        page = HTML_SKELETON.format(conversation=render_conversation(session["conversation"]))
        return make_response(page, 200, {"Content-Type": "text/html"})

    page = HTML_SKELETON.format(conversation=render_conversation(session["conversation"]))
    return make_response(page, 200, {"Content-Type": "text/html"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  
    app.run(host="0.0.0.0", port=port)
