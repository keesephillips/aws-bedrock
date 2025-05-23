import os, json, html
from flask import Flask, render_template, request, session, redirect, url_for, make_response
import boto3

# ------------------------------------------------------------------
# Configuration – read once at startup
# ------------------------------------------------------------------
REGION            = "us-east-2"#os.getenv("AWS_REGION", "us-east-2")          # Bedrock region
PROMPT_ARN        = "arn:aws:bedrock:us-east-2:381492212823:prompt/QSG8T98UZM"#os.getenv("BEDROCK_PROMPT_ARN", "arn:aws:bedrock:us-east-2:381492212823:prompt/QSG8T98UZM")               # required!
PROMPT_VAR_NAME   = "user_input"#os.getenv("PROMPT_VAR_NAME", "user_input")    # name inside {{ }} in your prompt
if not PROMPT_ARN:
    raise RuntimeError("BEDROCK_PROMPT_ARN must be set")

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

# ------------------------------------------------------------------
# Flask application
# ------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "2C8F2652583FBC2637D7090A175B18A1"

HTML_SKELETON = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Claude Chatbot</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    .msg {{ margin: .8em 0; }}
    .user {{ color: blue; font-weight: bold; }}
    .assistant {{ color: green; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Chat with Claude via Amazon Bedrock</h1>
  {conversation}
  <form method="POST">
    <input type="text" name="message" placeholder="Type your message…" required autofocus>
    <button type="submit">Send</button>
  </form>
</body>
</html>
"""

def render_conversation(conv):
    """Return HTML for the conversation list."""
    parts = []
    for turn in conv:
        role_cls = "user" if turn["role"] == "user" else "assistant"
        label    = "You"   if turn["role"] == "user" else "Claude"
        text     = html.escape(turn["text"])
        parts.append(f'<div class="msg"><span class="{role_cls}">{label}:</span> {text}</div>')
    return "\n".join(parts)

@app.route("/", methods=["GET", "POST"])
def index():
    # init session history
    if "conversation" not in session:
        session["conversation"] = []

    if request.method == "POST":
        user_text = request.form.get("message", "").strip()
        if user_text:
            # store user turn
            session["conversation"].append({"role": "user", "text": user_text})
            print(user_text)

            try:
                print(user_text)
                resp = bedrock.converse(
                    modelId=PROMPT_ARN,
                    promptVariables={ PROMPT_VAR_NAME: { "text": user_text } }
                    # contentType="application/json",
                    # body=json.dumps(payload)
                )
                print(resp)
                assistant_text = resp["output"]["message"]["content"][0]["text"]
            except Exception as exc:
                print(exc)
                assistant_text = f"Error: {exc}"

            session["conversation"].append({"role": "assistant", "text": assistant_text})

        return redirect(url_for("index"))

    # GET → render page
    html_page = HTML_SKELETON.format(conversation=render_conversation(session["conversation"]))
    return make_response(html_page, 200, {"Content-Type": "text/html"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # App Runner injects PORT
    app.run(host="0.0.0.0", port=port)