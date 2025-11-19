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
def _(mo):
    mo.md("""
    ##  Interactive Evaluation with ADK Web UI
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ```bash
    adk web --port=8005
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Systematic Evaluation
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Testing one conversation at a time does not scale.

    Regression testing is the practice or re-running
    existing tests to ensure that new changes haven't
    broken previously working code.

    ADK provies two methods for automatic regression
    and batch testing.

    - `pytest`
    - adk eval

    We will focus on `adk eval`.

    There are more or less four steps to evaluation:

    1. Create an evaluation configuration
    2. Create test cases
    3. Run the agent with test query
    4. Compare the results


    We're going to use this code to create a  config: `test_config.json`
    """)
    return


@app.cell
def _():
    import json

    # Create evaluation configuration with basic criteria
    eval_config = {
        "criteria": {
            "tool_trajectory_avg_score": 1.0,  # Perfect tool usage required
            "response_match_score": 0.8,  # 80% text similarity threshold
        }
    }

    with open("home_automation_agent/test_config.json", "w") as _f:
        json.dump(eval_config, _f, indent=2)

    print("✅ Evaluation configuration created!")
    print("\n📊 Evaluation Criteria:")
    print("• tool_trajectory_avg_score: 1.0 - Requires exact tool usage match")
    print("• response_match_score: 0.8 - Requires 80% text similarity")
    print("\n🎯 What this evaluation will catch:")
    print("✅ Incorrect tool usage (wrong device, location, or status)")
    print("✅ Poor response quality and communication")
    print("✅ Deviations from expected behavior patterns")
    return (json,)


@app.cell
def _(mo):
    mo.md("""
    ### Create test cases
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Next we'll create multiple tesr cases (sessions).
    """)
    return


@app.cell
def _():
    # Create evaluation test cases that reveal tool usage and response quality problems
    test_cases = {
        "eval_set_id": "home_automation_integration_suite",
        "eval_cases": [
            {
                "eval_id": "living_room_light_on",
                "conversation": [
                    {
                        "user_content": {
                            "parts": [
                                {
                                    "text": "Please turn on the floor lamp in the living room"
                                }
                            ]
                        },
                        "final_response": {
                            "parts": [
                                {
                                    "text": "Successfully set the floor lamp in the living room to on."
                                }
                            ]
                        },
                        "intermediate_data": {
                            "tool_uses": [
                                {
                                    "name": "set_device_status",
                                    "args": {
                                        "location": "living room",
                                        "device_id": "floor lamp",
                                        "status": "ON",
                                    },
                                }
                            ]
                        },
                    }
                ],
            },
            {
                "eval_id": "kitchen_on_off_sequence",
                "conversation": [
                    {
                        "user_content": {
                            "parts": [
                                {
                                    "text": "Switch on the main light in the kitchen."
                                }
                            ]
                        },
                        "final_response": {
                            "parts": [
                                {
                                    "text": "Successfully set the main light in the kitchen to on."
                                }
                            ]
                        },
                        "intermediate_data": {
                            "tool_uses": [
                                {
                                    "name": "set_device_status",
                                    "args": {
                                        "location": "kitchen",
                                        "device_id": "main light",
                                        "status": "ON",
                                    },
                                }
                            ]
                        },
                    }
                ],
            },
        ],
    }
    return (test_cases,)


@app.cell
def _(json, test_cases):
    with open("home_automation_agent/integration.evalset.json", "w") as _f:
        json.dump(test_cases, _f, indent=2)

    print("✅ Evaluation test cases created")
    print("\n🧪 Test scenarios:")
    for case in test_cases["eval_cases"]:
        user_msg = case["conversation"][0]["user_content"]["parts"][0]["text"]
        print(f"• {case['eval_id']}: {user_msg}")

    print("\n📊 Expected results:")
    print("• basic_device_control: Should pass both criteria")
    print(
        "• wrong_tool_usage_test: May fail tool_trajectory if agent uses wrong parameters"
    )
    print(
        "• poor_response_quality_test: May fail response_match if response differs too much"
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    next run this in the terminal:

    ```bash
    adk eval home_automation_agent home_automation_agent/integration.evalset.json --config_file_path=home_automation_agent/test_config.json --print_detailed_results
    ```
    """)
    return


@app.cell
def _():
    # Analyzing evaluation results - the data science approach
    print("📊 Understanding Evaluation Results:")
    print()
    print("🔍 EXAMPLE ANALYSIS:")
    print()
    print("Test Case: living_room_light_on")
    print("  ❌ response_match_score: 0.45/0.80")
    print("  ✅ tool_trajectory_avg_score: 1.0/1.0")
    print()
    print("📈 What this tells us:")
    print(
        "• TOOL USAGE: Perfect - Agent used correct tool with correct parameters"
    )
    print("• RESPONSE QUALITY: Poor - Response text too different from expected")
    print("• ROOT CAUSE: Agent's communication style, not functionality")
    print()
    print("🎯 ACTIONABLE INSIGHTS:")
    print("1. Technical capability works (tool usage perfect)")
    print("2. Communication needs improvement (response quality failed)")
    print(
        "3. Fix: Update agent instructions for clearer language or constrained response."
    )
    print()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
