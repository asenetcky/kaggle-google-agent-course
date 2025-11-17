# /// script
# requires-python = ">=3.14"
# dependencies = [
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
def _():
    return


if __name__ == "__main__":
    app.run()
