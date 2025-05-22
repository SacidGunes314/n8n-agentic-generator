import streamlit as st
from openai import OpenAI
import json
import os
import re

# Setup Streamlit page
st.set_page_config(page_title="n8n Agentic Workflow Generator", layout="centered")
st.title("🤖 n8n Agentic Workflow Generator")

st.markdown("""
Describe the AI-based workflow you want, and this tool will generate a valid `n8n` JSON template using OpenAI GPT-4o.

Example:  
> "Build a workflow that accepts uploaded PDFs, extracts key answers using GPT, and stores results in Notion."
""")

# Load API key from Streamlit secrets
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# Text input for the workflow description
desc = st.text_area("📝 Describe your agentic workflow", height=200)

# Button to trigger generation
if st.button("⚙️ Generate n8n Workflow"):
    if not desc:
        st.warning("Please describe your workflow first.")
    else:
        with st.spinner("Generating..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert in generating complex n8n workflows in JSON."
                        },
                        {
                            "role": "user",
                            "content": f"""
Generate a valid n8n JSON template for this agentic AI workflow:

\"\"\" 
{desc}
\"\"\"

Include:
- OpenAI agent nodes (with system/user prompts)
- JSON parsing logic
- HTTP/API or conditional logic as needed

Return ONLY valid n8n JSON, no explanation.
"""
                        }
                    ],
                    temperature=0.3
                )

                content = response.choices[0].message.content.strip()

                # Try to extract JSON from inside triple backticks if present
                match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
                json_str = match.group(1) if match else content

                try:
                    parsed_json = json.loads(json_str)
                    st.success("✅ Valid JSON generated!")
                    st.code(json.dumps(parsed_json, indent=2), language='json')
                except Exception as parse_error:
                    st.error("⚠️ Couldn't parse valid JSON. Here's the raw output:")
                    st.text(json_str)

            except Exception as e:
                st.error(f"❌ OpenAI API error: {str(e)}")
