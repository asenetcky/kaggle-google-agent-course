# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "google-adk==1.18.0",
#     "python-dotenv==1.2.1",
# ]
# ///

import marimo

__generated_with = "0.17.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import os
    from dotenv import load_dotenv
    return load_dotenv, os


@app.cell
def _(load_dotenv, os):
    load_dotenv()

    try:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        print("✅ Gemini API key setup complete.")
    except Exception as e:
        print(f"Auth Error: No 'GOOGLE_API_KEY' found. Details: {e}")
    return


@app.cell
def _():
    from google.adk.agents import Agent
    from google.adk.models.google_llm import Gemini
    from google.adk.runners import InMemoryRunner
    from google.adk.tools import google_search
    from google.genai import types

    print("✅ ADK components imported successfully.")
    return Agent, Gemini, InMemoryRunner, google_search, types


@app.cell
def _(types):
    retry_config = types.HttpRetryOptions(
        attempts=5,  # Maximum retry attempts
        exp_base=7,  # Delay multiplier
        initial_delay=1,  # Initial delay before first retry (in seconds)
        http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
    )
    return (retry_config,)


@app.cell
def _(Agent, Gemini, google_search, retry_config):
    root_agent = Agent(
        name="helpful_assistant",
        model=Gemini(
            model="gemini-2.5-flash-lite",
            retry_options=retry_config,
        ),
        description="My first agent - for answering general questions",
        instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
        tools=[google_search],
    )

    print("✅ Root Agent defined.")
    return (root_agent,)


@app.cell
def _(InMemoryRunner, root_agent):
    runner = InMemoryRunner(agent=root_agent)

    print("Runner created.")
    return (runner,)


@app.cell
async def _(runner):
    _response = await runner.run_debug(
        "What is Agent Development Kit from Google? What languages is the SDK available in?"
    )
    return


@app.cell
async def _(runner):
    _response = await runner.run_debug("What is the weather in Hawaii?")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
