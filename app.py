import streamlit as st
import boto3
import json
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 


app = Flask(__name__)

# Initialize Bedrock runtime client
# Ensure your App Runner service role has Bedrock permissions
# or configure credentials appropriately.
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv("AWS_REGION", "us-east-2") # Or your Bedrock region
)

PROMPT_ARN = os.getenv('BEDROCK_PROMPT_ARN') # Set this in App Runner

if not PROMPT_ARN:
    raise ValueError("BEDROCK_PROMPT_ARN environment variable not set.")

@app.route('/invoke-prompt', methods=['POST'])
def invoke_prompt():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload received"}), 400

        # 'promptVariables' should contain the keys and values
        # for the variables defined in your managed prompt.
        # Example: if your prompt is "Tell me a joke about {{topic}}.",
        # the input should be: {"promptVariables": {"topic": "cats"}}
        prompt_variables = data.get('promptVariables', {})

        body = json.dumps({
            "promptVariables": prompt_variables
        })

        response = bedrock_runtime.invoke_model(
            modelId=PROMPT_ARN, # Using the managed prompt ARN as the modelId
            body=body,
            contentType='application/json',
            accept='application/json' # Or the accept type expected by your model
        )

        response_body = json.loads(response.get('body').read())

        # The structure of response_body depends on the underlying model
        # and how Bedrock wraps the managed prompt response.
        # You might need to inspect it and extract the relevant generated text.
        # For many models, the output might be in a 'completion' or 'generation' field.
        # For Claude 3 via managed prompt, it's often in response_body['output']['text']
        # or similar, depending on the template.
        # Let's assume a common structure for demonstration:
        generated_text = response_body # Adjust based on actual response

        return jsonify({"response": generated_text})

    except Exception as e:
        app.logger.error(f"Error invoking Bedrock prompt: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080)) # App Runner typically sets PORT
    app.run(host='0.0.0.0', port=port)