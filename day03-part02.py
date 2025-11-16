# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "protobuf==6.33.1",
#     "python-dotenv==1.2.1",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")

with app.setup:
    # Initialization code that runs before all other cells
    import marimo as mo
    import os
    from dotenv import load_dotenv
    from google.adk.agents import LlmAgent
    from google.adk.models.google_llm import Gemini
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.memory import InMemoryMemoryService
    from google.adk.tools import load_memory, preload_memory
    from google.genai import types


@app.cell
def _():
    mo.md("""
    ## Environment setup:
    """)
    return


@app.cell
def _():
    ### environment setup
    load_dotenv()

    try:
        GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    except Exception as e:
        print(
            f"Auth Error: Please make sure 'GOOGLE_API_KEY' is in environment. Details: {e}"
        )

    retry_config = types.HttpRetryOptions(
        attempts=5,  # Maximum retry attempts
        exp_base=7,  # Delay multiplier
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
    )
    return


@app.cell
def _():
    mo.md("""
    ## Helper Functions:
    """)
    return


@app.cell
def _(APP_NAME, USER_ID, session_service):
    async def run_session(
        runner_instance: Runner,
        user_queries: list[str] | str,
        session_id: str = "default",
    ):
        """Helper function to run queries in a session and display responses."""
        print(f"\n### Session: {session_id}")

        # Create or retrieve session
        try:
            session = await session_service.create_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=session_id
            )
        except:
            session = await session_service.get_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=session_id
            )

        # Convert single query to list
        if isinstance(user_queries, str):
            user_queries = [user_queries]

        # Process each query
        for query in user_queries:
            print(f"\nUser > {query}")
            query_content = types.Content(
                role="user", parts=[types.Part(text=query)]
            )

            # Stream agent response
            async for event in runner_instance.run_async(
                user_id=USER_ID, session_id=session.id, new_message=query_content
            ):
                if (
                    event.is_final_response()
                    and event.content
                    and event.content.parts
                ):
                    text = event.content.parts[0].text
                    if text and text != "None":
                        print(f"Model: > {text}")


    print("✅ Helper functions defined.")
    return


@app.cell
def _():
    mo.md("""
    ## Memory Workflow
    """)
    return


@app.cell
def _():
    mo.md("""
    **Three-step integration process:**
    1. **Initialize:** Create a `MemoryService` and
        provide it to your agent via the `Runner`
    1. **Ingest:** Transfer *session* data to *memory*
        using `add_session_to_memory()`
    1. **Retrieve:** Search stored memories using
        `search_memory()`
    """)
    return


@app.cell
def _():
    mo.md("""
    ## Initialize `MemoryService`
    """)
    return


@app.cell
def _():
    mo.md("""
    ### Initailize Memory

    ADK has multiple `MemoryService` implmentations
    through the `BaseMemoryService` interface:

    - `InMemoryMemoryService` - Built-in for
        prototyping and testing (keyword matching,
        no persistence)

    - `VertexAiMemoryBankService` - Managed cloud
        service with LLM-powered consolidation
        and semantic search

    - **Custom Implementations** - You can build
        your own using databases (managed services
        are recommended)
    """)
    return


@app.cell
def _():
    # ADK's built-in Memory Service for dev/test
    memory_service = InMemoryMemoryService()
    return


@app.cell
def _():
    mo.md("""
    ### Adding Memory to Agent
    """)
    return


@app.cell
def _():
    mo.md("""
    First, create a simple agent.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
