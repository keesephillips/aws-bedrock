import os, json, html
from flask import Flask, request, session, redirect, url_for, make_response
import boto3
import time

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
REGION          = os.getenv("AWS_REGION", "us-east-2")      # Bedrock region
PROMPT_ARN      = os.getenv(
    "BEDROCK_PROMPT_ARN",
    "arn:aws:bedrock:us-east-2:381492212823:prompt/QSG8T98UZM"
)  # your managed-prompt ARN
PROMPT_VAR_NAME = os.getenv("PROMPT_VAR_NAME", "user_input")  # variable in the prompt template

if not PROMPT_ARN:
    raise RuntimeError("BEDROCK_PROMPT_ARN must be set")

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

# ------------------------------------------------------------------
# Flask application
# ------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "replace-with-secure-hex")  # set in env for prod

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
    """Convert conversation list → HTML."""
    rows = []
    for t in turns:
        role_cls = "user" if t["role"] == "user" else "assistant"
        label    = "You"   if t["role"] == "user" else "Claude"
        rows.append(
            f'<div class="msg"><span class="{role_cls}">{label}:</span> {html.escape(t["text"])}</div>'
        )
    return "\n".join(rows)

@app.route("/", methods=["GET", "POST"])
def index():
    # initialise chat history for this browser session
    if "conversation" not in session:
        session["conversation"] = []

    if request.method == "POST":
        user_text = request.form.get("message", "").strip()
        if user_text:
            # 1️⃣ store the user's question so it shows up immediately
            session["conversation"].append({"role": "user", "text": user_text})

            try:
                # 2️⃣ send it to your managed prompt via the Converse API
                resp = bedrock.converse(
                    modelId=PROMPT_ARN,
                    promptVariables={PROMPT_VAR_NAME: {"text": user_text}},
                    # inferenceConfig={"temperature": 0.5, "max_tokens": 512},
                )

                assistant_text = resp["output"]["message"]["content"][0]["text"]
            except Exception as exc:
                # show the error right in the chat so you can debug
                assistant_text = f"Error: {exc}"

            # 3️⃣ add Claude's answer to the history
            session["conversation"].append({"role": "assistant", "text": assistant_text})

        # redirect–after–POST pattern prevents form re-submission on refresh
        page = HTML_SKELETON.format(conversation=render_conversation(session["conversation"]))
        return make_response(page, 200, {"Content-Type": "text/html"})

    # GET → render the full conversation
    page = HTML_SKELETON.format(conversation=render_conversation(session["conversation"]))
    return make_response(page, 200, {"Content-Type": "text/html"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # App Runner injects PORT
    app.run(host="0.0.0.0", port=port)
