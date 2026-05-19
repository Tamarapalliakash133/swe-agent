from models.model import gpt_model

llm = gpt_model()


def analyzer(state):
    prompt = f"""
    You are a senior software architect analyzing a user's project request.

    Analyze the following and provide a clear breakdown:
    1. What programming language(s) should be used and why.
    2. What frameworks are needed (if any).
    3. What databases are required (if any) and which ones fit best.
    4. What are the core features to implement.
    5. What is the estimated complexity — single file or multi-file project.
    6. What type of project is this (REST API, CLI tool, web app, etc.).

    User request: {state.get("user_request")}

    Be specific and concise. Your analysis will guide the rest of the system.
    """

    res = llm.invoke(prompt)
    return {
        "intent_analyze": res.content
    }
