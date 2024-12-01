import streamlit as st
from openai import OpenAI


## With LLM query and context seperately
def llm_response(
    formatted_prompt,
    api_key,
    temperature=0.2,
):
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
    page_title="LLM Answer Judge", layout="wide", initial_sidebar_state="collapsed"
)


# Sidebar for OpenAI API key
st.sidebar.header("OpenAI API Key")
openai_api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")


# Function to initialize OpenAI API key
def init_openai_api(api_key):
    OpenAI.api_key = api_key


# Initialize API key if provided
if openai_api_key:
    init_openai_api(openai_api_key)
else:
    st.sidebar.warning("Please enter your OpenAI API key.")

st.title("LLM Answer Judge")

# Section 1: Prompt Template
with st.expander("Evalution Prompt Template (Default)"):
    default_prompt_template = """You are an AI assistant that compares an expected answer with an AI-generated answer.
    Your task is to evaluate the correctness of the AI-generated answer based on the expected answer.
    Identify factual discrepancies, missing information, and errors.
    Provide a score out of 10 and a brief explanation.

    Expected Answer:
    {expected_answer}

    AI-Generated Answer:
    {ai_generated_answer}

    Example Output:
    Score: 6/10

    Explanation:

    Factual Discrepancies:

    The AI-generated answer correctly explains why blue light scatters more, which is due to its shorter wavelength. However, it doesn't explicitly mention that sunlight is made up of a spectrum of many colors, which is a key point in the expected answer.
    The AI-generated answer does not mention the concept of Rayleigh scattering by name, which is a specific term used in the expected answer.
    Missing Information:

    The AI-generated answer does not explicitly state that sunlight is made up of a spectrum of many colors, like a rainbow, which is an important part of the expected answer.
    It also omits the explanation that blue and violet have the shortest wavelengths and red has the longest, which is part of the expected answer.
    Errors:

    There are no significant factual errors in the AI-generated answer, but it lacks some of the detailed explanations provided in the expected answer.

    Evaluation:"""

    prompt_template = st.text_area(
        "Enter the prompt template:", height=200, value=default_prompt_template
    )

col_1, col_2 = st.columns(2)
evaluation_result = None
tokens_used = None
with col_1:
    # Section 2: Expected Answer
    st.header("Expected Answer")
    expected_answer = st.text_area(
        "Enter the expected answer:",
        height=200,
        placeholder="Type the expected answer here...",
    )

    # Section 3: AI-Generated Answer
    st.header("AI-Generated Answer")
    ai_generated_answer = st.text_area(
        "Enter the AI-generated answer:",
        height=200,
        placeholder="Type the AI-generated answer here...",
    )
    if st.button("Evaluate"):
        if not openai_api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
        elif not expected_answer.strip():
            st.error("Expected answer is empty.")
        elif not ai_generated_answer.strip():
            st.error("AI-generated answer is empty.")
        else:
            # Format the prompt with user inputs
            formatted_prompt = prompt_template.format(
                expected_answer=expected_answer.strip(),
                ai_generated_answer=ai_generated_answer.strip(),
            )
            evaluation_result, tokens_used = llm_response(
                formatted_prompt, openai_api_key
            )
if evaluation_result:
    with col_2:
        st.header("Evaluation Results")
        st.markdown(evaluation_result)
        st.subheader("Tokens Used")
        # $2.50/milllion
        approx_cost = round(tokens_used["total_tokens"] * 0.0000025, 6)
        st.write(f"Total tokens Used: {tokens_used['total_tokens']}")
        st.write(f"Approximate cost: ${approx_cost}")
