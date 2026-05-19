from models.model import gpt_model

llm = gpt_model()


def archit(state):
    prompt = f"""
    You are a software architect designing a project structure.

    Based on the analysis below, define:
    1. What top-level folders to create (e.g. models/, routes/, services/, tests/).
    2. What the overall architecture pattern is (MVC, layered, microservice, etc.).
    3. Any important design decisions (e.g. use of dependency injection, config separation).
    4. What external packages/libraries will be needed.

    Analysis:
    {state["intent_analyze"]}

    User's original request: {state.get("user_request")}

    Be concrete and prescriptive — this feeds directly into code generation.
    """

    res = llm.invoke(prompt)
    return {
        "architect": res.content
    }
