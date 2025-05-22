import streamlit as st
import boto3
import json
import os
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 

# --- AWS Bedrock Configuration ---
# Best practice: Use an IAM role for App Runner.
# For local development, you might have AWS credentials configured.
# App Runner will set AWS_REGION automatically if your service is in that region.
# Ensure BEDROCK_MODEL_ID is set as an environment variable in App Runner.

try:
    BEDROCK_REGION = os.getenv("AWS_REGION", "us-east-2") # Or your specific Bedrock region
    BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID") # e.g., "anthropic.claude-v2:1"

    if not BEDROCK_MODEL_ID:
        st.error("BEDROCK_MODEL_ID environment variable not set.")
        st.stop()

    # Initialize the Bedrock runtime client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=BEDROCK_REGION
    )
except Exception as e:
    st.error(f"Error initializing AWS Bedrock client: {e}")
    st.stop()

# --- Streamlit App ---
st.title("My Bedrock Chatbot")
st.caption(f"Powered by AWS Bedrock ({BEDROCK_MODEL_ID})")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to invoke Bedrock model
def get_bedrock_response(user_prompt):
    """
    Invokes the Bedrock model with the given user prompt.
    This function now directly uses the model ID.
    The prompt structure is defined here, based on your "Prompt Management" design.
    """
    if not user_prompt:
        return "Please enter a prompt."

    # This is where you replicate the structure of your prompt from Bedrock Prompt Management.
    # Example for Anthropic Claude:
    # (Adjust this based on the model you are using and your prompt design)
    prompt_config = {
        "prompt": f"\n\nHuman: {user_prompt}\n\nAssistant:", # Claude specific
        "max_tokens_to_sample": 2000,
        "temperature": 0.7,
        "top_p": 0.9,
        # Add other parameters as needed for your model
    }
    # For other models like Amazon Titan or AI21, the 'prompt' key and structure will differ.
    # e.g., for Titan Text G1 - Express:
    # prompt_config = {
    #     "inputText": user_prompt,
    #     "textGenerationConfig": {
    #         "maxTokenCount": 2048,
    #         "temperature": 0.7,
    #         "topP": 0.9,
    #         "stopSequences": [] # Optional
    #     }
    # }

    try:
        response = bedrock_runtime.invoke_model(
            body=json.dumps(prompt_config),
            modelId=BEDROCK_MODEL_ID,
            accept='application/json',
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())

        # Extract the generated text based on the model's response structure
        # For Claude:
        completion = response_body.get('completion')
        # For Titan Text G1 - Express:
        # completion = response_body.get('results')[0].get('outputText')
        # For AI21 Jurassic-2:
        # completion = response_body.get('completions')[0].get('data').get('text')

        if completion:
            return completion.strip()
        else:
            st.error(f"Could not extract completion from response: {response_body}")
            return "Error: Could not get a valid response from Bedrock."

    except Exception as e:
        st.error(f"Error invoking Bedrock model: {e}")
        return f"Error: {e}"

# React to user input
if prompt := st.chat_input("Ask me anything..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get Bedrock response
    with st.spinner("Thinking..."):
        assistant_response = get_bedrock_response(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})