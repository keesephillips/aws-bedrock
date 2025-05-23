from flask import Flask, render_template, request, session, redirect, url_for
import boto3, json, os

app = Flask(__name__)
app.secret_key = 'replace-with-a-secret-key'  # Needed for session data; use a secure key in production

# Route for the chatbot UI and interaction
@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize conversation history in session if not present
    if 'conversation' not in session:
        session['conversation'] = []
    if request.method == 'POST':
        user_message = request.form.get('message')
        if user_message:
            # Add the user's message to the conversation history
            session['conversation'].append({'role': 'user', 'text': user_message})
            # Prepare the payload for Claude (Anthropic via Bedrock)
            messages_payload = [
                {"role": msg['role'], "content": [{"type": "text", "text": msg['text']}]} 
                for msg in session['conversation']
            ]
            payload = {
                "messages": messages_payload,
                "max_tokens": 512,
                "temperature": 0.5,
                "anthropic_version": "bedrock-2023-05-31"
            }
            # Invoke the Claude model via Amazon Bedrock
            bedrock_client = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
            model_id = "anthropic.claude-v2"  # Claude model ID (adjust if using a different version)
            try:
                response = bedrock_client.invoke_model(
                    modelId=model_id,
                    contentType="application/json",
                    body=json.dumps(payload)
                )
                # Read and decode the model's response
                response_json = json.loads(response['body'].read().decode('utf-8'))
                assistant_text = response_json["content"][0]["text"]
            except Exception as e:
                # Handle errors (e.g., permission or invocation errors)
                assistant_text = f"Error: {e}"
            # Add the model's answer to the conversation
            session['conversation'].append({'role': 'assistant', 'text': assistant_text})
        # Redirect to GET after POST (prevents form re-submission issues)
        return redirect(url_for('index'))
    # For GET requests, render the chat page with the conversation history
    return render_template('index.html', conversation=session.get('conversation', []))

if __name__ == '__main__':
    # Use the PORT provided by App Runner (default to 8080 for local testing)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
