# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "ipython==9.7.0",
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

    from google.genai import types
    from google.adk.agents import LlmAgent
    from google.adk.models.google_llm import Gemini
    from google.adk.runners import InMemoryRunner, Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import google_search, AgentTool, ToolContext
    from google.adk.code_executors import BuiltInCodeExecutor
    from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import (
        StdioConnectionParams,
        StdioServerParameters,
    )

    from google.adk.apps.app import App, ResumabilityConfig
    from google.adk.tools.function_tool import FunctionTool

    from google.adk.tools.mcp_tool.mcp_session_manager import (
        StreamableHTTPServerParams,
        StreamableHTTPConnectionParams,
    )

    # Google AI Studio API Key
    try:
        load_dotenv()
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    except Exception as e:
        print(f"Auth Error: No 'GOOGLE_API_KEY' found. Details: {e}")


    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )


@app.cell
def _():
    mo.md("""
    ## 🎯 Exercise: Build an Image Generation Agent with Cost Approval

    **The scenario:**

    Build an agent that generates images using the
    MCP server, but requires approval for "bulk"
    image generation:

    - Single image request (1 image): Auto-approve,
        generate immediately

    - Bulk request (>1 image): Pause and ask for
        approval before generating multiple images

    - Explore different publicly available Image
        Generation MCP Servers
    """)
    return


@app.cell
def _():
    mo.md("""
    using pollinations.ai mcp server
    """)
    return


@app.cell
def _():
    # pollinations_tool_filter = [
    #     "generateImageUrl",
    #     "generateImage",
    #     "editImage",
    #     "generateImageFromReference",
    #     "listImageModels",
    # ]


    # mcp_image_server = McpToolset(
    #     connection_params=StdioConnectionParams(
    #         server_params=StdioServerParameters(
    #             command="npx",
    #             args=["-y", "@pollinations/model-context-protocol"],
    #             tool_filter=pollinations_tool_filter,
    #         ),
    #         timeout=30,
    #     )
    # )


    # pollinations_mcp = McpToolset(
    #     connection_params=StreamableHTTPConnectionParams(
    #         # This is the public, unauthenticated endpoint
    #         url="https://mcp.sequa.ai/v1/pollinations/contribute"
    #     ),
    #     # Pass your list of strings to the tool_filter
    #     tool_filter=pollinations_tool_filter,
    # )

    mcp_image_server = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",  # Run MCP server via npx
                args=[
                    "-y",  # Argument for npx to auto-confirm install
                    "@modelcontextprotocol/server-everything",
                ],
                tool_filter=["getTinyImage"],
            ),
            timeout=30,
        )
    )
    return (mcp_image_server,)


@app.cell
def _(mcp_image_server):
    image_agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="image_agent",
        instruction="Use the MCP Tool to generate images for user queries",
        tools=[mcp_image_server],  # [mcp_image_server],
    )
    return (image_agent,)


@app.cell
def _(image_agent):
    mcp_runner = InMemoryRunner(agent=image_agent)
    return (mcp_runner,)


@app.cell
async def _(mcp_runner):
    image_response = await mcp_runner.run_debug(
        "Proivide a sample tiny image",
        verbose=True,
    )
    return (image_response,)


@app.cell
def _(image_response):
    from IPython.display import display, Image as IPImage
    import base64

    for event in image_response:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "function_response") and part.function_response:
                    for item in part.function_response.response.get(
                        "content", []
                    ):
                        if item.get("type") == "image":
                            display(IPImage(data=base64.b64decode(item["data"])))
    return


app._unparsable_cell(
    r"""
    def generate_image(
        prompt: str, num_images: int, tool_context: ToolContext
    ) -> dict:
        \"\"\"Creates a generate image request. Requires
        approval if more than 1 image is requested.

        Args:
            prompt: User prompt for image content
            num_images: Number of images to generate

        Returns:
            Dictionary with image status
        \"\"\"
        # ^ placeholder stuff for now

        if num_images > 1:
        
    """,
    name="_"
)


if __name__ == "__main__":
    app.run()
