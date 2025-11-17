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
    return (retry_config,)


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
    return (run_session,)


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
    return (memory_service,)


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
def _(retry_config):
    # Constants that will be used throughout
    APP_NAME = "MemoryDemoApp"
    USER_ID = "demo_user"

    # Agent
    user_agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="MemoryDemoAgent",
        instruction="Answer user questions in simple words.",
    )

    print("Agent created! :)")
    return APP_NAME, USER_ID, user_agent


@app.cell
def _():
    mo.md("""
    ### Creating the Runner
    """)
    return


@app.cell
def _():
    mo.md("""
    **Key configuration considerations:**

    The `Runner` will need the following services
    to enable memory functionality:

    - `session_service`: Manages conversation threads
    and events

    - `memory_service`: Provides long-term knowledge
    storage

    Both work together: Sessions capture convos,
    Memory stores knowledge for retreival across
    sessions.
    """)
    return


@app.cell
def _(memory_service, user_agent):
    # Create Session Service
    session_service = InMemorySessionService()  # Handles convos

    # Runner with BOTH services
    runner = Runner(
        agent=user_agent,
        app_name="MemoryDemoApp",
        session_service=session_service,
        memory_service=memory_service,  # now available!
    )


    print("Agent and Runner created with memory support! :)")
    return runner, session_service


@app.cell
def _():
    mo.callout(
        kind="warn",
        value=mo.md(
            """
            **Important**

            Configuration vs Usage:

            Adding `memory_service` to the `Runner`
            makes memory *available* but not automatically
            use it.

            It must be explicitly:

            1. **Ingest data** using 
            `add_session_to_memory()`

            1. **Enable retrieval** by giving your
            agent memory tools
            (`load_memory` or `preload_memory`)

            """
        ),
    )
    return


@app.cell
def _():
    mo.md("""
    ### `MemoryService` Implementation Options
    """)
    return


@app.cell
def _():
    mo.md("""
    - This notebook: `InMemoryMemoryService`

        - Stores raw convo events *w/o* consolidation

        - Keyword-based search (simple word matching)

        - In-memory storage (resets on restart)

        - Ideal for learning/local dev

    - Production: `VertexAiMeoryBankService`

        - LLM-powered extraction of *key facts*

        - Semantic search (meaning-based retrieval)

        - Persistent cloud storage

        - Integrates external knowledge sources

    - NOTE: There is nice API consistency/ DX - both
    implementations use *identical* methods
    (`add_session_to_memory()`, `search_memory()`).
    So this single workflow will apply to all
    memory services.
    """)
    return


@app.cell
def _():
    mo.md("""
    ## Ingest Session Data into Memory
    """)
    return


@app.cell
def _():
    mo.md("""
    > Why should you transfer Session data to Memory?
    """)
    return


@app.cell
def _():
    mo.md("""
    - Now that memory is initialized, it's time
    to start populating with *knowledge*.

    - `MemoryService` starts empty.

    - All convos stored in *Sessions*

    - Sessions contain *raw events*

    - raw events are: messages, tool calls and
    metadata

    - To make available to memory explicitly
    transfer information with
    `add_session_to_memory()`

    - Prod will perform intelligent consolidation

    - Let's get some data to store...
    """)
    return


@app.cell
async def _(run_session, runner):
    # example: user tells agent their fav color
    await run_session(
        runner,
        "My favorite color is sea-green. Can you write a Haiku about it?",
        "conversation-01",  # Session ID
    )
    return


@app.cell
async def _(APP_NAME, USER_ID, session_service):
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id="conversation-01"
    )

    # Let's see what's in the session
    print("📝 Session contains:")
    for event in session.events:
        text = (
            event.content.parts[0].text[:60]
            if event.content and event.content.parts
            else "(empty)"
        )
        print(f"  {event.content.role}: {text}...")
    return (session,)


@app.cell
def _():
    mo.md("""
    confirmed above - our session contains our convo. Now lets transfer it to memory.
    """)
    return


@app.cell
async def _(memory_service, session):
    # Key method
    await memory_service.add_session_to_memory(session)
    print("session added! :)")
    return


@app.cell
def _():
    mo.md("""
    ### Enable Memory Retrieval in Our Agent
    """)
    return


@app.cell
def _():
    mo.md("""
    Memory has been transferred. However, agents
    **cannot directly access `MemoryService`**
    they need tools to search it.  This is by
    design - for fine grain control.
    """)
    return


@app.cell
def _():
    mo.md("""
    **Memory Retrieval in ADK**

    - `load_memory` (**Reactive**)

        - Agent decides when to search memory

        - Only retrieves when agent thinks is needed

        - More efficient/saves tokens

        - Risk: Agent might forget to search

    - `preload_memory` (**Proactive**)

        - Automatically searches before every turn

        - Memory always available to agent

        - Guaranteed context, but less efficient

        - Searches even when not needed
    """)
    return


@app.cell
def _():
    mo.md("""
    ### Add Load Memory Tool to Agent
    """)
    return


@app.cell
def _():
    mo.md("""
    Recreate the agent, but with `load_memory` tool. Simply add to `tools` - no custom implementation needed.
    """)
    return


@app.cell
def _(retry_config):
    memory_user_agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="MemoryDemoAgent",
        instruction="Answer user questions in simple words. User load_memory tool if you need to recall past conversations",
        tools=[load_memory],  # Agent now has access to memory
    )

    print("Agent with load_memory tool created :)")
    return (memory_user_agent,)


@app.cell
def _(APP_NAME, memory_service, memory_user_agent, session_service):
    # create new runner with new agent
    memory_runner = Runner(
        agent=memory_user_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )
    return (memory_runner,)


@app.cell
async def _(memory_runner, run_session):
    await run_session(memory_runner, "What is my favorite color?", "color-test")
    return


@app.cell
def _():
    mo.md("""
    woohoo it works! :)
    """)
    return


@app.cell
def _():
    mo.md("""
    ### Complete Manual Workflow Test
    """)
    return


@app.cell
def _():
    mo.md("""
    Let's see the complete workflow in action.
    We will:

    1. Have a conversation about a birthday
    1. Manually Save it to memory
    1. Test retrieval in a *new session*

    This demonstrates the full cycle:
    **ingest -> store -> retrieve**
    """)
    return


@app.cell
async def _(memory_runner, run_session):
    await run_session(
        memory_runner,
        "My friend Unix's birthday is January 1st, 1970.",
        "birthday-session-01",
    )
    return


@app.cell
def _():
    mo.md("""
    Now manually save this to memory to transfer short-term to long-term memory storage
    """)
    return


@app.cell
async def _(APP_NAME, USER_ID, memory_service, session_service):
    # manually save session
    birthday_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id="birthday-session-01"
    )

    await memory_service.add_session_to_memory(birthday_session)

    print("Birthday session saved to memory!")
    return


@app.cell
def _():
    mo.md("""
    Now the crucial test - start a new session, with a new id and ask the agent to recall the birthday.
    """)
    return


@app.cell
async def _(memory_runner, run_session):
    await run_session(
        memory_runner,
        "When is Unix's birthday?",
        "birthday-session-02",  # note the different ID
    )
    return


@app.cell
def _():
    mo.md("""
    So what just happened?

    1. Agent recieves: "When is Unix's birthday?"
    1. Agent recognizes: This requires past
    conversation context.
    1. Agent calls: `load_memory("birthday")`
    1. Memory returns: Previous conversation
    containing "January 1st, 1970"
    1. Agent responds: "Unix's birthday is
    January 1st, 1970"

    The memory worked, even though it is a
    completely different session!
    """)
    return


@app.cell
def _():
    mo.md("""
    ### Experimenting with `preload_memory`
    """)
    return


@app.cell
def _():
    mo.md("""
    We are going to experiment with swapping
    `load_memory` with `preload_memory` in
    the tool array.
    """)
    return


@app.cell
def _(retry_config):
    preload_user_agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="MemoryDemoAgent",
        instruction="Answer user questions in simple words. User preload_memory tool if you need to recall past conversations",
        tools=[preload_memory],
    )
    return (preload_user_agent,)


@app.cell
def _(APP_NAME, memory_service, preload_user_agent, session_service):
    # create the new runner
    preload_runner = Runner(
        agent=preload_user_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )
    return (preload_runner,)


@app.cell
def _():
    mo.md("""
    So what actually changes?

    Remember that `load_memory` is reactive, and
    `preload_memory` is proactive.
    """)
    return


@app.cell
def _():
    mo.md("""
    Now we are going to test it out.
    """)
    return


@app.cell
async def _(preload_runner, run_session):
    await run_session(
        preload_runner,
        "What is my favorite color?",
        "test-preload-session-01",
    )
    return


@app.cell
async def _(preload_runner, run_session):
    await run_session(
        preload_runner,
        "When is it the best time to visit Acadia National park in Maine?",
        "test-preload-session-01",
    )
    return


@app.cell
async def _(APP_NAME, USER_ID, session_service):
    # let's take a look at that session
    preloaded_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id="test-preload-session-01"
    )


    # Let's see what's in the session
    def session_look(session):
        for event in session.events:
            text = (
                event.content.parts[0].text[:60]
                if event.content and event.content.parts
                else "(empty)"
            )
            print(f"  {event.content.role}: {text}...")


    session_look(preloaded_session)
    return


@app.cell
def _():
    mo.md("""
    ### Manual Memory Search
    """)
    return


@app.cell
def _():
    mo.md("""
    Users can search memories directly in code.

    This is useful for:

    - Debugging memory contents
    - Building analytics dashboards
    - Creating custom memory management UIs

    The `search_memory()` method takes a text query
    and returns `SearchMemoryResponse` with
    matching memories.

    Let us test by searching for color preferences!
    """)
    return


@app.cell
async def _(APP_NAME, USER_ID, memory_service):
    # search for color preferences

    search_response = await memory_service.search_memory(
        app_name=APP_NAME,
        user_id=USER_ID,
        query="What is the user's favorite color?",
    )

    print("🔍 Search Results:")
    print(f"  Found {len(search_response.memories)} relevant memories")
    print()

    for memory in search_response.memories:
        if memory.content and memory.content.parts:
            _text = memory.content.parts[0].text[:80]
            print(f"  [{memory.author}]: {_text}...")
    return


@app.cell
def _():
    mo.md("""
    very cool!
    """)
    return


@app.cell
def _(APP_NAME, USER_ID, memory_service):
    async def member_berries(query):
        search_response = await memory_service.search_memory(
            app_name=APP_NAME,
            user_id=USER_ID,
            query=query,
        )

        print(f"🔍 Search Results for {query}:")
        print(f"  Found {len(search_response.memories)} relevant memories")
        print()

        for memory in search_response.memories:
            if memory.content and memory.content.parts:
                _text = memory.content.parts[0].text[:80]
                print(f"  [{memory.author}]: {_text}...")
    return (member_berries,)


@app.cell
async def _(member_berries):
    await member_berries("haiku")
    await member_berries("preferred hue")
    await member_berries("age")
    await member_berries("park")
    await member_berries("maine")
    return


@app.cell
def _():
    mo.md("""
    Notice acadia didn't pop up, because it wasn't commited to memory.
    """)
    return


@app.cell
def _():
    mo.md("""
    ### How Does Search Work?
    """)
    return


@app.cell
def _():
    mo.md("""
    **InMemoryService (this notebook):**

    - **Method:** Keyword matching
        - *e.g.* "favorite color" matches
        because those exact words exist
        - **Limitation:** age won't match even
        though it's relevant to the memory

    **VertexAiMemoryBankService/Production**:
    - **Method:** Semantic search via *embeddings*
        - *e.g.* "age" will likely match birthday
        conversations
        - **Advantage:** Understands meaning, not
        just keywords
    """)
    return


@app.cell
def _():
    mo.md("""
    ### Automating Memory Storage
    """)
    return


@app.cell
def _():
    mo.md("""
    **Callbacks**
    ADK has a callback system that hooks into
    key execution moments.

    - callbacks are **python functions** that are
    attached to agents.

    - ADK automatically calls them at specific
    stages - sort of like checkpoints during
    the execution flow.

    - **Think of callbacks as event listeners in
    the agent lifecyle**

    - e.g. When agent processes a request...
        - Agent receives input
        - Agent calls the LLM
        - Agent invokes tools
        - Agent generates the response
    - Callbacks let users insert custom logic at
    each of the stages above *without* modifying
    core agent code.
    """)
    return


@app.cell
def _():
    mo.md("""
    **Available callback types and usecases:**

    - Runs before OR after agent completes
    processing a request

        - `before_agent_callback`
        - `after_agent_callback`

    - Around tool invocations

        - `before_tool_callback`
        - `after_tool_callback`

    - Around LLM calls
        - `before_model_callback`
        - `after_model_callback`

    - When errors occur: `on_model_error_callback`
    """)
    return


@app.cell
def _():
    mo.md("""
    **Common Uses:**

    - Logging and observabnility of agent actions
    - Automatic data persistence
    - Custom validation/filtering
    - Performance monitoring

    [ADK Callbacks Doco](https://google.github.io/adk-docs/agents/callbacks/)
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
