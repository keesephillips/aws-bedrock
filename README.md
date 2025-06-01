# AWS Bedrock

# Background 
The AWS Bedrock offers an ability to easily scale AI LLMs as a production pathway. This specific implementation uses AWS App Runner to host the frontend while employing Bedrock to use the LLMs.

# Pipeline
The pipeline for this implementation is as follows: 
1. AWS App Runner
2. AWS Bedrock (via custom prompt)
3. Claude 3.5 Haiku v1

In this implementation, the Claude 3.5 Haiku v1 can easily be switched out for a different model from a variety of sources. Similarly, the prompt created for the model can be altered very easily without disrupting the pipeline. The AWS App Runner allows for a frontend that can quickly and easily scale to user demand based on the traffic. 

# Bedrock Prompt
In Bedrock the following was used to create a custom prompt before passing to an LLM:

```
Provide a detailed answer to the following question:

{{user_input}}

Provide a structured analysis including:
1. Executive summary 
2. Main themes
3. Key points
4. Tone analysis
5. Suggested improvements

Format the response using clear headers and bullet points
```
*{{user_input}} is the variable which the user will use as the input in the frontend*

# Demo
[Demo Video](https://youtu.be/spfRu4GzEGQ)

# Author
Keese Phillips
