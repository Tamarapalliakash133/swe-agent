from models.model import gpt_model

llm = gpt_model()


def agent_plan(state):
    prompt = f"""
    You are a project planner. Break the architecture below into a numbered list of concrete implementation tasks.

    Rules:
    - Each task should map to a specific piece of code to write.
    - Order tasks by dependency (config/models first, routes next, tests last).
    - Keep tasks atomic — one responsibility per task.
    - Do not include setup steps like "install pip" or "create virtualenv".

    Example output format:
    1. Create database connection config in config/database.py
    2. Define User model with id, email, password fields in models/user.py
    3. Define Post model with id, title, body, author_id in models/post.py
    4. Implement JWT auth helpers in services/auth.py
    5. Create /register and /login routes in routes/auth.py
    6. Create CRUD routes for posts in routes/posts.py
    7. Write unit tests for auth in tests/test_auth.py
    8. Write unit tests for posts API in tests/test_posts.py

    Architecture to plan:
    {state["architect"]}

    Return only the numbered task list.
    """

    res = llm.invoke(prompt)
    return {
        "tasks": res.content,
        "plan": res.content
    }
