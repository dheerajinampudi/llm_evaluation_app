import streamlit as st
from openai import OpenAI


## With LLM query and context separately
def llm_response(formatted_prompt, api_key, temperature=0.2):
    """
    formatted_prompt contains all dynamic fields
    """
    model_name = "gpt-4o"
    # Create the chat completion request
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": formatted_prompt}],
        temperature=temperature,
    )

    # Extract the AI response and token usage
    ai_response = response.choices[0].message.content.strip()
    token_usage_dict = {
        "completion_tokens": response.usage.completion_tokens,
        "prompt_tokens": response.usage.prompt_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return ai_response, token_usage_dict


# Set page configuration
st.set_page_config(
    page_title="AI Answer Evaluator", layout="wide", initial_sidebar_state="collapsed"
)

# Sidebar for OpenAI API key
st.sidebar.header("🔑 OpenAI API Key")
openai_api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")


# Function to initialize OpenAI API key
def init_openai_api(api_key):
    OpenAI.api_key = api_key


# Initialize API key if provided
if openai_api_key:
    init_openai_api(openai_api_key)
else:
    st.sidebar.warning("Please enter your OpenAI API key.")

# App Title
st.title("🤖 AI Answer Evaluator")
st.subheader("Compare and evaluate AI-generated answers with expected answers")

# Section 1: Prompt Template
with st.expander("📝 Evaluation Prompt Template (Default)", expanded=False):
    st.write("Modify the evaluation prompt template to suit your needs:")
    default_prompt_template = """You are an AI assistant that compares an expected answer with an AI-generated answer.
    Your task is to evaluate the correctness of the AI-generated answer based on the expected answer.
    Identify factual discrepancies, missing information, and errors.
    Provide a score out of 10 and a brief explanation.

    Expected Answer:
    {expected_answer}

    AI-Generated Answer:
    {ai_generated_answer}

    Evaluation:"""

    prompt_template = st.text_area(
        "Prompt Template:", height=150, value=default_prompt_template
    )

# Two-column layout for input and results
col_1, col_2 = st.columns([1, 1.2])

with col_1:
    st.header("📋 Expected Answer")
    expected_answer = st.text_area(
        "Type the expected answer:",
        height=150,
        placeholder="Enter the expected answer here...",
    )

    st.header("🤔 AI-Generated Answer")
    ai_generated_answer = st.text_area(
        "Type the AI-generated answer:",
        height=150,
        placeholder="Enter the AI-generated answer here...",
    )

    if st.button("🚀 Evaluate"):
        if not openai_api_key:
            st.error("⚠️ Please enter your OpenAI API key in the sidebar.")
        elif not expected_answer.strip():
            st.error("⚠️ Expected answer is empty.")
        elif not ai_generated_answer.strip():
            st.error("⚠️ AI-generated answer is empty.")
        else:
            # Format the prompt with user inputs
            formatted_prompt = prompt_template.format(
                expected_answer=expected_answer.strip(),
                ai_generated_answer=ai_generated_answer.strip(),
            )
            evaluation_result, tokens_used = llm_response(
                formatted_prompt, openai_api_key
            )

            # Display results in the second column
            with col_2:
                st.header("📊 Evaluation Results")
                st.markdown(evaluation_result, unsafe_allow_html=True)

                st.subheader("🔢 Token Usage")
                approx_cost = round(tokens_used["total_tokens"] * 0.0000025, 6)
                st.write(f"**Total Tokens Used:** {tokens_used['total_tokens']}")
                st.write(f"**Approximate Cost:** ${approx_cost:.6f}")

# General Formatting Improvements
st.markdown(
    """
<style>
    .stTextArea textarea {
        background-color: #000;
        border: 1px solid #ccc;
    }
    .stButton button {
        font-weight: bold;
        padding: 5px 15px;
        border-radius: 5px;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }
</style>
""",
    unsafe_allow_html=True,
)
