import os
from dotenv import load_dotenv

from typing import Any, Dict

from google.adk.agents import Agent, LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.models.google_llm import Gemini
from google.adk.sessions import DatabaseSessionService
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.tool_context import ToolContext
from google.genai import types

### environment setup
load_dotenv()

try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
except Exception as e:
    print(f"Auth Error: Please make sure 'GOOGLE_API_KEY' is in environment. Details: {e}")

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)


# Day 3
## Agent Sessions (Short Term)
### Part 1

### helper functions
# define helper functions that will be reused throughout the notebook
async def run_session(
    runner_instance: Runner,
    user_queries: list[str] | str = None,
    session_name: str = "default",
):
    print(f"\n ### Session: {session_name}")

    # Get app name from the Runner
    app_name = runner_instance.app_name

    # Attempt to create a new session or retrieve an existing one
    try:
        session = await session_service.create_session(
            app_name=app_name, user_id=USER_ID, session_id=session_name
        )
    except:
        session = await session_service.get_session(
            app_name=app_name, user_id=USER_ID, session_id=session_name
        )

    # Process queries if provided
    if user_queries:
        # Convert single query to list for uniform processing
        if type(user_queries) == str:
            user_queries = [user_queries]

        # Process each query in the list sequentially
        for query in user_queries:
            print(f"\nUser > {query}")

            # Convert the query string to the ADK Content format
            query = types.Content(role="user", parts=[types.Part(text=query)])

            # Stream the agent's response asynchronously
            async for event in runner_instance.run_async(
                user_id=USER_ID, session_id=session.id, new_message=query
            ):
                # Check if the event contains valid content
                if event.content and event.content.parts:
                    # Filter out empty or "None" responses before printing
                    if (
                        event.content.parts[0].text != "None"
                        and event.content.parts[0].text
                    ):
                        print(f"{MODEL_NAME} > ", event.content.parts[0].text)
    else:
        print("No queries!")

### building a stateful agent
APP_NAME = "default"
USER_ID = "default"
SESSION = "deault"

MODEL_NAME = "gemini-2.5-flash-lite"

# step 1: create the LLM Agent
root_agent = Agent(
    model=Gemini(
        model= MODEL_NAME,
        retry_options=retry_config
    ),
    name="text_chat_bot",
    description="A text chatbot"
)


# step 2: set up session management
# InMemorySessionService stores conversions in RAM

session_service = InMemorySessionService()


# step 3: Create the Runner
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

print("✅ Stateful agent initialized!")
print(f"   - Application: {APP_NAME}")
print(f"   - User: {USER_ID}")
print(f"   - Using: {session_service.__class__.__name__}")

# testing our stateful agent
# run a conversation with two queries in the same session
# notice: both queries are part of the SAME session, so context is maintained

await run_session(
    runner,
    [
        "Hi, I am asenetcky! What is the capital of United States?",
        "Hello! What is my name?" # This time, the agent should remember...
    ],
    "stateful-agentic-session",
)

# testing agent forgetfulness
# restart the kernel rereun everything except run_session
# and run the following:

# Run this cell after restarting the kernel. All this history will be gone...
await run_session(
    runner,
    ["What did I ask you about earlier?", "And remind me, what's my name?"],
    "stateful-agentic-session",
)  # Note, we are using same session name

# Persistent Sessions with `DatabaseSessionService`

#|Service 	|Use Case 	|Persistence 	|Best For|
#|InMemorySessionService 	|Development & Testing 	|❌ Lost on restart 	|Quick prototypes|
#|DatabaseSessionService 	|Self-managed apps 	|✅ Survives restarts 	|Small to medium apps|
#|Agent Engine Sessions 	|Production on GCP 	|✅ Fully managed 	|Enterprise scale|





### Part 2 Agent Memory (Long Term)

