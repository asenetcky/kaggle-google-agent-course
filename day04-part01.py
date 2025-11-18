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


@app.cell
def _(mo):
    mo.md("""
    # Day 04 Part 01 Agent Observability
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Setup
    """)
    return


@app.cell
def _():
    import marimo as mo

    import os
    import logging
    from dotenv import load_dotenv
    return load_dotenv, logging, mo, os


@app.cell
def _(load_dotenv, os):
    load_dotenv()

    try:
        GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    except Exception as e:
        print(
            f"Auth Error: Please make sure 'GOOGLE_API_KEY' is in environment. Details: {e}"
        )
    return


@app.cell
def _(mo):
    mo.md("""
    ### Logging Setup
    """)
    return


@app.cell
def _(logging, os):
    # clean up any previous logs
    for log_file in ["logger.log", "web.log", "tunnel.log"]:
        if os.path.exists(log_file):
            os.remove(log_file)
            print(f"Cleaned up {log_file}")

    # configure logging with DEBUG log level
    logging.basicConfig(
        filename="logger.log",
        level=logging.DEBUG,
        format="%(filename)s:%(lineno)s %(levelname)s: %(message)s",
    )

    print("logging configured! :)")
    return


@app.cell
def _(mo):
    mo.md("""
    ## Hands-On Debugging with ADK Web UI
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Create a 'Research Paper Finder' Agent
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    **Our goal:** Build a research paper finder agent
    that helps users find academic papers on any
    topic.

    First, lets intentionally create an *incorrect*
    version of the agent to practice debugging...yay!

    Okay to make it more fun we'll mix it up a bit.
    We'll use the ADK cli to do this
    with `adk create`.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ```bash
    adk create research-agent --model gemini-2.5-flash-lite --api_key $GOOGLE_API_KEY
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ```bash
    Agent created in /home/alex/repos/kaggle-google-agent-course/research-agent:
    - .env
    - __init__.py
    - agent.py
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Agent Definition
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    - We'll configure it as an LlmAgent, give it a
    name, model and instruction.
    - The root_agent gets the user prompt and
    delegates the search to the google_search_agent.
    - Then, the agent uses the count_papers tool to
    count the number of papers returned.

    Pay attention to the root agent's instructions
    and the count_papers tool parameter!

    We're going to temporarily overwrite the
    `agent.py` created by the ADK cli.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    file looks like this (with the error)

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models.google_llm import Gemini
    from google.adk.tools.agent_tool import AgentTool
    from google.adk.tools.google_search_tool import google_search

    from google.genai import types
    from typing import List

    retry_config = types.HttpRetryOptions(
        attempts=5,  # Maximum retry attempts
        exp_base=7,  # Delay multiplier
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
    )

    # ---- Intentionally pass incorrect datatype - `str` instead of `List[str]` ----
    def count_papers(papers: str):
        "\""
        This function counts the number of papers in a list of strings.
        Args:
          papers: A list of strings, where each string is a research paper.
        Returns:
          The number of papers in the list.
        "\""
        return len(papers)


    # Google Search agent
    google_search_agent = LlmAgent(
        name="google_search_agent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        description="Searches for information using Google search",
        instruction="\""Use the google_search tool to find information on the given topic. Return the raw search results.
        If the user asks for a list of papers, then give them the list of research papers you found and not the summary."\"",
        tools=[google_search]
    )


    # Root agent
    root_agent = LlmAgent(
        name="research_paper_finder_agent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="\""Your task is to find research papers and count them.

        You MUST ALWAYS follow these steps:
        1) Find research papers on the user provided topic using the 'google_search_agent'.
        2) Then, pass the papers to 'count_papers' tool to count the number of papers returned.
        3) Return both the list of research papers and the total number of papers.
        "\"",
        tools=[AgentTool(agent=google_search_agent), count_papers]
    )
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    We'll start the adk web UI in the terminal. Default port is `8000` - choose whatever works for you.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ```bash
    adk web --log_level DEBUG --port 8002
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Test the agent in ADK web UI
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Do: In the ADK web UI**

    1. Select "research-agent" from the dropdown in
        the top-left.

    1. In the chat interface, type: Find latest
        quantum computing papers

    1. Send the message and observe the response.
        The agent should return a list of research
        papers and their count.

    It looks like our agent works and we got a response!
    But wait, isn't the count of papers unusually large?
    Let's look at the logs and trace.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ...series of steps on the gui...
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Logging in production
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    That was all well and good... but what about
    production?

    You probably won't have web ui access and even if you
    did you can't manually check the logs fast enough...

    We need some new observability methods like adding
    **logs to our code**.

    The approach isn't that much different than adding
    log statements in python functions - with agents
    there is a common approach **Plugins**.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### How to add logs for production observability

    A Plugin is a custom code module that runs
    automaticallt at various stages. Plugins are
    composed of callbacks with provide hooks
    to interrupt an agent's flow.

    Think of it like this:


    - Your agent workflow: User message → Agent thinks →
      Calls tools → Returns response
    - Plugin hooks into this: Before agent starts → After
      tool runs → When LLM responds → etc.
    - Plugin contains your custom code: Logging,
      monitoring, security checks, caching, etc.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Callbacks are the atomic components inside a Plugin.
    Callbacks that are grouped together are a plugin.

    So what does a plugin look like?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ```python
    print("----- EXAMPLE PLUGIN - DOES NOTHING ----- ")

    import logging
    from google.adk.agents.base_agent import BaseAgent
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models.llm_request import LlmRequest
    from google.adk.plugins.base_plugin import BasePlugin


    # Applies to all agent and model calls
    class CountInvocationPlugin(BasePlugin):
        "\"\"A custom plugin that counts agent and tool invocations."\"\"

        def __init__(self) -> None:
            "\"\"Initialize the plugin with counters."\"\"
            super().__init__(name="count_invocation")
            self.agent_count: int = 0
            self.tool_count: int = 0
            self.llm_request_count: int = 0

        # Callback 1: Runs before an agent is called. You can add any custom logic here.
        async def before_agent_callback(
            self, *, agent: BaseAgent, callback_context: CallbackContext
        ) -> None:
            "\"\"Count agent runs."\"\"
            self.agent_count += 1
            logging.info(f"[Plugin] Agent run count: {self.agent_count}")

        # Callback 2: Runs before a model is called. You can add any custom logic here.
        async def before_model_callback(
            self, *, callback_context: CallbackContext, llm_request: LlmRequest
        ) -> None:
            "\"\"Count LLM requests."\"\"
            self.llm_request_count += 1
            logging.info(f"[Plugin] LLM request count: {self.llm_request_count}")
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plugins are registered *once* on a runner and then it
    applies automatically to *every agent, tool call, and
    llm request** on that runner.

    Thankfully you do not need to define all the callbacks
    for *standard* observability data in ADK. ADK provides
    a built-in **LoggingPlugin** that automatically
    captures all agent activity.

    Let's put it into action - using our previous demo
    agent - the Research paper finder!
    """)
    return


@app.cell
def _():
    from google.adk.agents import LlmAgent
    from google.adk.models.google_llm import Gemini
    from google.adk.tools.agent_tool import AgentTool
    from google.adk.tools.google_search_tool import google_search

    from google.genai import types
    from typing import List

    retry_config = types.HttpRetryOptions(
        attempts=5,  # Maximum retry attempts
        exp_base=7,  # Delay multiplier
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
    )


    def count_papers(papers: List[str]):
        """
        This function counts the number of papers in a list of strings.
        Args:
          papers: A list of strings, where each string is a research paper.
        Returns:
          The number of papers in the list.
        """
        return len(papers)


    # Google search agent
    google_search_agent = LlmAgent(
        name="google_search_agent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        description="Searches for information using Google search",
        instruction="Use the google_search tool to find information on the given topic. Return the raw search results.",
        tools=[google_search],
    )

    # Root agent
    research_agent_with_plugin = LlmAgent(
        name="research_paper_finder_agent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""Your task is to find research papers and count them. 
   
       You must follow these steps:
       1) Find research papers on the user provided topic using the 'google_search_agent'. 
       2) Then, pass the papers to 'count_papers' tool to count the number of papers returned.
       3) Return both the list of research papers and the total number of papers.
       """,
        tools=[AgentTool(agent=google_search_agent), count_papers],
    )

    print("✅ Agent created")
    return (research_agent_with_plugin,)


@app.cell
def _(mo):
    mo.md("""
    ### Add Looging Plugin to Runner
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    We're going to use the `InMemoryRunner` to invoke
    the agent. To use the `LoggingPlugin` in the
    agent above we will:

    1. Import the plug
    1. Add it when initializing the `InMemoryRunner`
    """)
    return


@app.cell
def _(research_agent_with_plugin):
    from google.adk.runners import InMemoryRunner
    from google.adk.plugins.logging_plugin import (
        LoggingPlugin,
    )  # <---- 1. Import the Plugin
    import asyncio

    runner = InMemoryRunner(
        agent=research_agent_with_plugin,
        plugins=[
            LoggingPlugin()
        ],  # <---- 2. Add the plugin. Handles standard Observability logging across ALL agents
    )

    print("✅ Runner configured")
    return (runner,)


@app.cell
async def _(runner):
    print("🚀 Running agent with LoggingPlugin...")
    print("📊 Watch the comprehensive logging output below:\n")

    response = await runner.run_debug("Find recent papers on quantum computing")
    return


@app.cell
def _(mo):
    mo.md("""
    Question to self: No timestamps?!?

    anywho...

    Summary:

    When to use which type of logging?

    1. **Development debugging** -
    use `adk web --log_level DEBUG`

    1. **Common production observability** -
    use `LoggingPlugin()`

    1. **Custom requirements** - Build your
    own custom callbacks and bundle into
    a plugin
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
