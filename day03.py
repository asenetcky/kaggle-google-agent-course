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

# let's use DatabaseSessionService with SQLite.

# step 1: create the same agent (notice we it's LlmAgent)
chatbot_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="text_chat_bot",
    description="A text chatbot with persistent memory",
)

# step 2: switch to DatabaseSessionService
# SQLite database created automatically

db_url = "sqlite:///my_agent_data.db" # local sqlite file
session_service = DatabaseSessionService(db_url=db_url)

# step 3: create new runner w/ persistant storage
runner = Runner(agent=chatbot_agent, app_name=APP_NAME, session_service=session_service)

print("✅ Upgraded to persistent sessions!")
print(f"   - Database: my_agent_data.db")
print(f"   - Sessions will survive restarts!")


# verify persistence
await run_session(
    runner,
    ["Hi, I am asenetcky! What is your purpose?", "Hello! What is my name?"],
    "test-db-session-01"
)

# restart kernal

await run_session(
    runner,
    ["What is the capital of India?", "Hello! What is my name?"],
    "test-db-session-01",
)

# verify session isolation
await run_session(
    runner, ["Hello! What is my name?"], "test-db-session-02"
)  # Note, we are using new session name

# lets take a look a the DB shall we?

import sqlite3

def check_data_in_db():
    with sqlite3.connect("my_agent_data.db") as connection:
        cursor = connection.cursor()
        result = cursor.execute(
            "select app_name, session_id, author, content from events"
        )
        print([_[0] for _ in result.description])
        for each in result.fetchall():
            print(each)

check_data_in_db()


# pretty cool but that all adds up fast. which leads us to...
# Conext Compaction

# basic idea:

# 1. create an app
# 2. pass app to chatbot_agent
# 3. create config to do context compaction.
# this defines how often to compact and how many
# previous conversaitons to retain

# re-define our app with Events Compaction enabled

research_app_compacting = App(
    name="research_app_compacting",
    root_agent=chatbot_agent,
    #this is new
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3, # Trigger compaction ever 3 invocations
        overlap_size=1, # keep 1 previous turn for context
    ),
)

db_url = "sqlite:///my_agent_data.db"  # Local SQLite file
session_service = DatabaseSessionService(db_url=db_url)

research_runner_compacting = Runner(
    app=research_app_compacting, session_service=session_service
)

print("✅ Research App upgraded with Events Compaction!")

# demo
# Turn 1
await run_session(
    research_runner_compacting,
    "What is the latest news about AI in healthcare?",
    "compaction_demo",
)

# Turn 2
await run_session(
    research_runner_compacting,
    "Are there any new developments in drug discovery?",
    "compaction_demo",
)

# Turn 3 - Compaction should trigger after this turn!
await run_session(
    research_runner_compacting,
    "Tell me more about the second development you found.",
    "compaction_demo",
)

# Turn 4
await run_session(
    research_runner_compacting,
    "Who are the main companies involved in that?",
    "compaction_demo",
)


### Part 2 Agent Memory (Long Term)

