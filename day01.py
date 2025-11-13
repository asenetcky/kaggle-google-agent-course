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
def _(mo):
    mo.md("""
    # Kaggle + Google Intensive Agent Course

    ## Day One - From Prompt to Action

    ### Part 1
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
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        print("✅ Gemini API key setup complete.")
    except Exception as e:
        print(f"Auth Error: No 'GOOGLE_API_KEY' found. Details: {e}")
    return


@app.cell
def _():
    from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
    from google.adk.models.google_llm import Gemini
    from google.adk.runners import InMemoryRunner
    from google.adk.tools import AgentTool, FunctionTool, google_search
    from google.genai import types

    print("✅ ADK components imported successfully.")
    return (
        Agent,
        AgentTool,
        FunctionTool,
        Gemini,
        InMemoryRunner,
        LoopAgent,
        ParallelAgent,
        SequentialAgent,
        google_search,
        types,
    )


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
    root_agent1 = Agent(
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
    return (root_agent1,)


@app.cell
def _(InMemoryRunner, root_agent1):
    runner = InMemoryRunner(agent=root_agent1)

    print("Runner created.")
    return (runner,)


@app.cell
async def _(runner):
    response1 = await runner.run_debug(
        "What is Agent Development Kit from Google? What languages is the SDK available in?"
    )
    return


@app.cell
async def _(runner):
    response1 = await runner.run_debug("What is the weather in Hawaii?")
    return


@app.cell
def _(mo):
    mo.md("""
    ### Part 2 - Multi Agents
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    Creating a Research and a Summarizer Agent:
    """)
    return


@app.cell
def _(Agent, Gemini, google_search, retry_config):
    # Research agent role:  use google_search tool and present findings

    research_agent = Agent(
        name="ResearchAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""You are a specialized research agent. Your only
        job is to use the google_search tool to find 2-3 peices of
        relevant information on the given topic and present the
        findings with citations.""",
        tools=[google_search],
        output_key="research_findings",
        # the result of this agent will be stored in the session state
        # with this key
    )

    print("✅ research_agent created.")
    return (research_agent,)


@app.cell
def _(Agent, Gemini, retry_config):
    # summarizer Agent: its job is to summarize the text it recieves.

    summarizer_agent = Agent(
        name="SummarizerAgent",
        model=Gemini(
            model="gemini-2.5-flash-lite",
            retry_options=retry_config,
        ),
        instruction="""Read the provided research finds: 
        {research_findings}
        Create a concise summary as a bulleted list with
        3-5 key points.""",
        output_key="final_summary",
    )

    print("✅ summarizer_agent created.")
    return (summarizer_agent,)


@app.cell
def _(
    Agent,
    AgentTool,
    Gemini,
    research_agent,
    retry_config,
    summarizer_agent,
):
    # Root Coordinator: Orchestrates the workflow by calling the aub-agents as tools.

    root_agent2 = Agent(
        name="ResearchCoordinator",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""You are a research coordinator.
        Yout goal is to answer the user's query by orchestating
        a workflow.
        1. First, you MUST call the 'ResearchAgent' tool
        to find the relevant information on the topic provided
        by the user.
        2. Next, after receiving the research fndings, you
        MUST call the 'SummarizerAgent' tool to create a
        concise summary.
        3. Finally, present the final summary clearly to the
        user as your response.
        """,
        tools=[AgentTool(research_agent), AgentTool(summarizer_agent)],
    )

    print("✅ root_agent created.")
    return (root_agent2,)


@app.cell
async def _(InMemoryRunner, root_agent2, runner):
    runner2 = InMemoryRunner(agent=root_agent2)
    response2 = await runner.run_debug(
        "What are the latest advancements in quantum computing and    what do they mean for AI?"
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ### Part 3

    Sequential Workflows - The Assembly Line
    """)
    return


@app.cell
def _(Agent, Gemini, retry_config):
    # Outline Agent: Create initial blog post outline

    outline_agent = Agent(
        name="OutlineAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""
        Create a blog outline for the given topic with:
        1. A catchy headline
        2. An introduction hook
        3. 3-5 Main sections with 2-3 bullet points for each
        4. A concluding thought
        """,
        output_key="blog_outline",
    )


    print("✅ outline_agent created.")
    return (outline_agent,)


@app.cell
def _(Agent, Gemini, retry_config):
    # Writer Agent: Write the full blog post based on the outline
    # from the previous agent.

    writer_agent = Agent(
        name="WriterAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""
        Following this outline strictly: {blog_outline}
        Write a brief, 200 to 300-word blod post with an engaging and
        informative tone.
        """,
        output_key="blog_draft",
    )

    print("✅ writer_agent created.")
    return (writer_agent,)


@app.cell
def _(Agent, Gemini, retry_config):
    # Editor Agent: Edits and polishes the draft from the writer agent

    editor_agent = Agent(
        name="EditorAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""
        Edit this draft: {blog_draft}
        Your task is to polish this text by fixing any
        grammatical errors, improving the flow and
        sentence structure, and enhancing overall
        clarity.
        """,
        output_key="final_blog",
    )


    print("✅ editor_agent created.")
    return (editor_agent,)


@app.cell
def _(SequentialAgent, editor_agent, outline_agent, writer_agent):
    root_agent3 = SequentialAgent(
        name="BlogPipeline",
        sub_agents=[outline_agent, writer_agent, editor_agent],
    )

    print("✅ SequentialAgent created.")
    return (root_agent3,)


@app.cell
async def _(InMemoryRunner, root_agent3, runner):
    runner3 = InMemoryRunner(agent=root_agent3)
    response3 = await runner.run_debug(
        "Wite a blog post about the benefits of multi-agent systems for software developers."
    )
    return


@app.cell
def _(mo):
    mo.md("""
    Executive Summary from Parallel Research Team
    """)
    return


@app.cell
def _(Agent, Gemini, google_search, retry_config):
    # tech researcher: foceses on ai and ml trends

    tech_researcher = Agent(
        name="TechResearcher",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""
            Research the latest AI/ML trends. Include 3 key developments,
            the main companiesinvolved, and the potential impact. Keep
            the report very concise (100 words).
        """,
        tools=[google_search],
        output_key="tech_research",
    )


    print("✅ tech_researcher created.")
    return (tech_researcher,)


@app.cell
def _(Agent, Gemini, google_search, retry_config):
    # health researcher: focus on medical breakthroughs

    health_researcher = Agent(
        name="HealthResearcher",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""
        Research recent medical breakthroughs. Include 3 significant
        advances, their practical applications, and estimated timelines.
        Keep the report concise (100 words).
        """,
        tools=[google_search],
        output_key="health_research",
    )


    print("✅ health_researcher created.")
    return (health_researcher,)


@app.cell
def _(Agent, Gemini, google_search, retry_config):
    # finance researcher: focuses on fintech trends

    finance_researcher = Agent(
        name="FinanceResearcher",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""
        Research current fintech trends. include 3 key trends,
        their market implications, and the future outlook.
        Keep the report concise (100 words).
        """,
        tools=[google_search],
        output_key="finance_research",
    )

    print("✅ finance_researcher created.")
    return (finance_researcher,)


@app.cell
def _(Agent, Gemini, retry_config):
    aggregator_agent = Agent(
        name="AggregatorAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""
        Combine these three research findings into a 
        single executive summary:

        **Technology Trends:**
        {tech_research}

        **Health Breakthroughs:**
        {health_research}

        **Finance Innovations:**
        {finance_research}

        Your summary should highlight common themes,
        surprising connections, and the most important
        key takeaways from all three reports. The final
        summary should be around 200 words.
        """,
        output_key="executive_summary",
    )


    print("✅ aggregator_agent created.")
    return (aggregator_agent,)


@app.cell
def _(
    ParallelAgent,
    SequentialAgent,
    aggregator_agent,
    finance_researcher,
    health_researcher,
    tech_researcher,
):
    # nest all these under a parallel agent, and then inside of a
    # sequential one

    # the ParallelAgent runs all its sub-agents simultaneously.

    parallel_research_team = ParallelAgent(
        name="ParallelResearchTeam",
        sub_agents=[tech_researcher, health_researcher, finance_researcher],
    )

    # SequentialAgent defines high level workflow
    # parallel team first, then the aggregator

    research_root_agent = SequentialAgent(
        name="ResearchSystem",
        sub_agents=[parallel_research_team, aggregator_agent],
    )

    print("✅ Parallel and Sequential Agents created.")
    return (research_root_agent,)


@app.cell
async def _(InMemoryRunner, research_root_agent):
    research_runner = InMemoryRunner(agent=research_root_agent)
    response = await research_runner.run_debug(
        "Run the daily executive briefing on Tech, Health and Finance."
    )
    return


@app.cell
def _(mo):
    mo.md("""
    Loop Workflows - The Refinement Cycle
    """)
    return


@app.cell
def _(Agent, Gemini, retry_config):
    # This agent runs ONCE at the beginning to create the first draft.
    initial_writer_agent = Agent(
        name="InitialWriterAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""Based on the user's prompt, write the first draft of a short story (around 100-150 words).
        Output only the story text, with no introduction or explanation.""",
        output_key="current_story",  # Stores the first draft in the state.
    )

    print("✅ initial_writer_agent created.")
    return (initial_writer_agent,)


@app.cell
def _(Agent, Gemini, retry_config):
    # This agent's only job is to provide feedback or the approval signal. It has no tools.
    critic_agent = Agent(
        name="CriticAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""You are a constructive story critic. Review the story provided below.
        Story: {current_story}

        Evaluate the story's plot, characters, and pacing.
        - If the story is well-written and complete, you MUST respond with the exact phrase: "APPROVED"
        - Otherwise, provide 2-3 specific, actionable suggestions for improvement.""",
        output_key="critique",  # Stores the feedback in the state.
    )

    print("✅ critic_agent created.")
    return (critic_agent,)


@app.cell
def _(mo):
    mo.md("""
    Now, we need a way for the loop to actually stop based on the
    critic's feedback. The `LoopAgent` itself doesn't automatically
    know that "APPROVED" means "stop."

    We need an agent to give it an explicit signal to terminate the
    loop.

    We do this in two parts:

    1. A simple Python function that the LoopAgent understands as an
    "exit" signal.

    1. An agent that can call that function when the right condition is
    met.
    """)
    return


@app.cell
def _():
    # this function is for the RefinerAgent to exit the loop


    def exit_loop():
        """Call this function ONLY when the critique is
        'APPROVED', indicating tthe story is finished and no
        more changes are needed.
        """

        return {
            "status": "approved",
            "message": "Story approved. Exiting refinement loop.",
        }


    print("✅ exit_loop function created.")
    return (exit_loop,)


@app.cell
def _(mo):
    mo.md("""
    next wrap this up in `FunctionTool`
    """)
    return


@app.cell
def _(Agent, FunctionTool, Gemini, exit_loop, retry_config):
    # RefinerAgent refines story based on critique or exits loop

    refiner_agent = Agent(
        name="RefinerAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""You are a story refiner. You have a story draft and critique.

        Story Draft: {current_story}
        Critique: {critique}

        Your task is to analyze the critique.
        - IF the critique is EXACTLY "APPROVED", you MUST call the `exit_loop` function and nothing else.
        - OTHERWISE, rewrite the story draft to fully incorporate the feedback from the critique.""",
        output_key="current_story",  # It overwrites the story with the new, refined version.
        tools=[
            FunctionTool(exit_loop)
        ],  # The tool is now correctly initialized with the function reference.
    )

    print("✅ refiner_agent created.")
    return (refiner_agent,)


@app.cell
def _(mo):
    mo.md("""
    now to tie it all together and add a max number of iterations
    """)
    return


@app.cell
def _(
    LoopAgent,
    SequentialAgent,
    critic_agent,
    initial_writer_agent,
    refiner_agent,
):
    # LoopAgent cotains the agents that will run repeatedly:
    # Critic -> Refiner

    story_refinement_loop = LoopAgent(
        name="StoryRefinementLoop",
        sub_agents=[critic_agent, refiner_agent],
        max_iterations=5,
    )


    # this root agent is sequential to define overall workflow:
    # initial write -> Refinement Loop

    story_root_agent = SequentialAgent(
        name="StoryPipeline",
        sub_agents=[initial_writer_agent, story_refinement_loop],
    )

    print("✅ Loop and Sequential Agents created.")
    return (story_root_agent,)


@app.cell
async def _(InMemoryRunner, runner, story_root_agent):
    story_runner = InMemoryRunner(agent=story_root_agent)
    story_response = await runner.run_debug(
        "Write a short story about a lighthouse keeper who discovers a mysterious, glowing map"
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
