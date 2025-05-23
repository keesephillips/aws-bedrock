import os, json
from flask import Flask, render_template, request, session, redirect, url_for
import boto3

# ------------------------------------------------------------------
# Configuration – read once at startup
# ------------------------------------------------------------------
REGION            = os.getenv("AWS_REGION", "us-east-2")          # Bedrock region
PROMPT_ARN        = os.getenv("BEDROCK_PROMPT_ARN", "arn:aws:bedrock:us-east-2:381492212823:prompt/QSG8T98UZM")               # required!
PROMPT_VAR_NAME   = os.getenv("PROMPT_VAR_NAME", "user_input")    # name inside {{ }} in your prompt
if not PROMPT_ARN:
    raise RuntimeError("BEDROCK_PROMPT_ARN environment variable is required")

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

# ------------------------------------------------------------------
# Flask application
# ------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "replace-with-a-secure-secret-key"

@app.route("/", methods=["GET", "POST"])
def index():
    # Initialise chat history once per browser session
    if "conversation" not in session:
        session["conversation"] = []

    if request.method == "POST":
        user_text = request.form.get("message", "").strip()
        if user_text:
            # ---- 1. store the user turn locally so we can display it
            session["conversation"].append({"role": "user", "text": user_text})

            # ---- 2. Build the Converse payload
            payload = {
                "promptVariables": {
                    PROMPT_VAR_NAME: { "text": user_text }
                }
                # If you need multi-turn context *in addition* to the prompt
                # template, you can append messages like this:
                # "messages": [
                #     { "role": m["role"],
                #       "content": [ { "text": m["text"] } ] }
                #     for m in session["conversation"]   # or some window
                # ]
            }

            try:
                response = bedrock.converse(
                    modelId=PROMPT_ARN,
                    contentType="application/json",
                    body=json.dumps(payload)
                )
                # Converse returns structured JSON, no need to read a stream
                assistant_text = response["output"]["message"]["content"][0]["text"]
            except Exception as exc:
                assistant_text = f"❌ Error: {exc}"
