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
def _():
    return


if __name__ == "__main__":
    app.run()
