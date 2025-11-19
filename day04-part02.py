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
    # Day 04 Part 02 - Agent Evaluation
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
    from dotenv import load_dotenv
    return load_dotenv, mo, os


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
    mo.md(r"""
    ## Agent Evaluation
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Previously, our practice of implementation of
    implementing observability in AI agents was
    primarily **reactive** - it comes into play only
    after an issue ocurred.

    This notebook will complement those practices with
    a *proactive* approach using **Agent Evaluation**.
    We will be continuously evaluating our agent's
    performance and catch quality degradation much
    earlier.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### The story
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Pretend for a moment - we've built a home automation
    agent. Works and tests perfectly so we launch it
    in full confidence.

    Then the following occurs:

    - **Week 1:** Agent turns on fireplace when asked for
        lights
    - **Week 2:** Agent wont respond to commands in guest
      room.
    - **Week 3:** Agent gives rude responses when devices
      are unavailable
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    > **The Problem:** `Standard testing does not equal
    > Evaluation

    Agents are different from traditional software:

    - They are *non-deterministic*
    - Users give unpredictable, ambiguous commands
    - Small prompt changes cause dramatic behavior
      shifts and different tool calls

      To accommodate all these variables, agents need
      systematic evaluation, not just the `happy path`
      testing.

      > The agent's entire decision-making process -
      > including the final response, and the path
      > it took to get the response (trajectory)
      > needs to be assessed.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Creating a Home Automation Agent
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ```bash
    adk create home_automation_agent --model gemini-2.5-flash-lite --api_key $GOOGLE_API_KEY
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ```bash
    Agent created in /kaggle/working/home_automation_agent:
    - .env
    - __init__.py
    - agent.py
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    We'll be creating this file to setup the agent:
        `home_automation_agent/agent.py`

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models.google_llm import Gemini

    from google.genai import types

    # Configure Model Retry on errors
    retry_config = types.HttpRetryOptions(
        attempts=5,  # Maximum retry attempts
        exp_base=7,  # Delay multiplier
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
    )

    def set_device_status(location: str, device_id: str, status: str) -> dict:
        "\""Sets the status of a smart home device.

        Args:
            location: The room where the device is
            located.
            device_id: The unique identifier for the
            device.
            status: The desired status, either 'ON' or
            'OFF'.

        Returns:
            A dictionary confirming the action.
        "\""
        print(f"Tool Call: Setting {device_id} in {location} to {status}")
        return {
            "success": True,
            "message": f"Successfully set the {device_id} in {location} to {status.lower()}."
        }

    # This agent has DELIBERATE FLAWS that we'll discover through evaluation!
    root_agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="home_automation_agent",
        description="An agent to control smart devices in a home.",
        instruction="\""You are a home automation assistant. You control ALL smart devices in the house.

        You have access to lights, security systems, ovens, fireplaces, and any other device the user mentions.
        Always try to be helpful and control whatever device the user asks for.

        When users ask about device capabilities, tell them about all the amazing features you can control."\"",
        tools=[set_device_status],
    )

    ```
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
