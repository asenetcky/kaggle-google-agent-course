# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "google-adk==1.18.0",
#     "ipython==9.7.0",
#     "mcp==1.21.1",
#     "protobuf==6.33.0",
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
    from google.adk.runners import InMemoryRunner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import google_search, AgentTool, ToolContext
    from google.adk.code_executors import BuiltInCodeExecutor

    print("✅ ADK components imported successfully.")


@app.cell
def _():
    mo.md("""
    # Kaggle + Google Intensive Agent Course

    ## Day Two - Agent Tools

    ### Part 1
    """)
    return


@app.cell
def _():
    load_dotenv()

    try:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        print("✅ Gemini API key setup complete.")
    except Exception as e:
        print(f"Auth Error: No 'GOOGLE_API_KEY' found. Details: {e}")
    return


@app.cell
def _():
    mo.md("""
    ### Helper functions
    Prints generated python code and results from the
    code execution tool:
    """)
    return


@app.cell
def _():
    def show_python_code_and_result(response):
        for i in range(len(response)):
            # Check if the response contains a valid function call result from the code executor
            if (
                (response[i].content.parts)
                and (response[i].content.parts[0])
                and (response[i].content.parts[0].function_response)
                and (response[i].content.parts[0].function_response.response)
            ):
                response_code = (
                    response[i].content.parts[0].function_response.response
                )
                if "result" in response_code and response_code["result"] != "```":
                    if "tool_code" in response_code["result"]:
                        print(
                            "Generated Python Code >> ",
                            response_code["result"].replace("tool_code", ""),
                        )
                    else:
                        print(
                            "Generated Python Response >> ",
                            response_code["result"],
                        )


    print("✅ Helper functions defined.")
    return (show_python_code_and_result,)


@app.cell
def _():
    mo.md("""
    ### Configure Retry Options
    LLMs can be sensitive to transient errors like rate
    limits or temporary server unavailability. Retrying
    options automatically handles some of these errors.
    """)
    return


@app.cell
def _():
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
    Generic tools provided in the ADK are great, but
    sometimes you need custom business logic.
    Any python function can be a tool, and this
    gives you fine-tuned control over everything.

    ### Example: Currency Converter Agent

    First tool - getting fees for payment methods:
    """)
    return


@app.cell
def _():
    # Pay attention to the docstring, type hints, and return value.
    def get_fee_for_payment_method(method: str) -> dict:
        """
        Looks up the transaction fee percentage for a
        given payment method.

        This tool simulates looking up a company's internal fee
        structure based on the name of the payment method provided
        by the user.

        Args:
            method: The name of the payment method.
            It should be descriptive, e.g., "platinum credit card"
            or "bank transfer".

        Returns:
            Dictionary with status and fee information.
            Success: {"status": "success", "fee_percentage": 0.02}
            Error: {
                    "status": "error",
                    "error_message": "Payment method not found"
                    }
        """
        # This simulates looking up a company's internal fee structure.
        fee_database = {
            "platinum credit card": 0.02,  # 2%
            "gold debit card": 0.035,  # 3.5%
            "bank transfer": 0.01,  # 1%
        }

        fee = fee_database.get(method.lower())
        if fee is not None:
            return {"status": "success", "fee_percentage": fee}
        else:
            return {
                "status": "error",
                "error_message": f"Payment method '{method}' not found",
            }


    print("✅ Fee lookup function created")
    print(f"💳 Test: {get_fee_for_payment_method('platinum credit card')}")
    return (get_fee_for_payment_method,)


@app.cell
def _():
    mo.md("""
    second tool - grabbing the exchange rate:
    """)
    return


@app.cell
def _():
    def get_exchange_rate(base_currency: str, target_currency: str) -> dict:
        """
        Looks up and returns the exchange rate between two currencies.

        Args:
            base_currency: The ISO 4217 currency code of the currency you
                           are converting from (e.g., "USD").
            target_currency: The ISO 4217 currency code of the currency
                             you are converting to (e.g., "EUR").

        Returns:
            Dictionary with status and rate information.
            Success: {"status": "success", "rate": 0.93}
            Error: {
                    "status": "error",
                    "error_message": "Unsupported currency pair"
                    }
        """

        # Static data simulating a live exchange rate API
        # In production, this would call something like: requests.get("api.exchangerates.com")
        rate_database = {
            "usd": {
                "eur": 0.93,  # Euro
                "jpy": 157.50,  # Japanese Yen
                "inr": 83.58,  # Indian Rupee
            }
        }

        # Input validation and processing
        base = base_currency.lower()
        target = target_currency.lower()

        # Return structured result with status
        rate = rate_database.get(base, {}).get(target)
        if rate is not None:
            return {"status": "success", "rate": rate}
        else:
            return {
                "status": "error",
                "error_message": f"Unsupported currency pair: {base_currency}/{target_currency}",
            }


    print("✅ Exchange rate function created")
    print(f"💱 Test: {get_exchange_rate('USD', 'EUR')}")
    return (get_exchange_rate,)


@app.cell
def _():
    mo.md("""
    now for creating our curreny agent!
    """)
    return


@app.cell
def _(get_exchange_rate, get_fee_for_payment_method, retry_config):
    currency_agent = LlmAgent(
        name="currency_agent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""
        You are a smart currency conversion assistant.

        For currency conversion requests:
        1. Use `get_fee_for_payment_method()` to find transcation fees
        2. Use `get_exchange_rate()` to get currency conversion rates
        3. Check the "status" field in each tool's response for errors
        4. Calculate the final amount after fees based on the output
            from `get_fee_for_payment_method` and `get_exchange_rate`
            methods and provide a clear breakdown.
        5. First, state the final converted amount. Then, explain how
            you got that result by showing the intermediate amounts.
            Your explanation must include: the fee percentage and
            its value in the original currency, the amount remaining
            after the fee, and the exchange rate used for the final
            conversion.

        If any tool returns status "error", explain the issue to
        the user clearly.
        """,
        tools=[get_fee_for_payment_method, get_exchange_rate],
    )

    print("✅ Currency agent created with custom function tools")
    print("🔧 Available tools:")
    print("  • get_fee_for_payment_method - Looks up company fee structure")
    print("  • get_exchange_rate - Gets current exchange rates")
    return (currency_agent,)


@app.cell
def _():
    mo.md("""
    Time to test our currency agent!
    """)
    return


@app.cell
async def _(currency_agent):
    currency_runner = InMemoryRunner(agent=currency_agent)
    _ = await currency_runner.run_debug(
        "I want to convert 500 US dollars to Euros using my Platinum Credit Card. how much will I receive?"
    )
    return


@app.cell
def _():
    mo.md("""
    ### Improving Agent Reliability

    Agent's can be pretty iffy on the math.... but we
    can make a tool and/or some code they can use
    to calculate the math for them, which is much
    more reliable.
    """)
    return


@app.cell
def _(retry_config):
    calculation_agent = LlmAgent(
        name="CalculationAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""
        You are a specialized calculator that only responds with Python
        code.  You are forbidden from providing any text, explanations, 
        or conversational responses.

        Your task is to take a request for a calculation and translate
        it into a single block of python code that calculates
        the answer.

        **RULE:**
        1. Your output MUST be ONLY a Python code block.
        2. Do NOT write any text before or after the code block.
        3. The Python code MUST calculate the result.
        4. The Python code MUST print the final result to stdout.
        5. You are PROHIBITED from performing the calculation
        yourself. Your only job is to generate the code that
        will perform the calculation.

        Failure to follow these rules will result in an error.
        """,
        code_executor=BuiltInCodeExecutor(),
    )
    return (calculation_agent,)


@app.cell
def _():
    mo.md("""
    now we change the original instructions for the currency agent.
    """)
    return


@app.cell
def _(
    calculation_agent,
    get_exchange_rate,
    get_fee_for_payment_method,
    retry_config,
):
    enhanced_currency_agent = LlmAgent(
        name="enhanced_currency_agent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        # Updated instruction
        instruction="""
            You are a smart currency conversion assistant. 
            You must strictly follow these steps and use the available 
            tools.

          For any currency conversion request:

       1. Get Transaction Fee: Use the get_fee_for_payment_method() tool 
       to determine the transaction fee.
       2. Get Exchange Rate: Use the get_exchange_rate() tool to get the 
       currency conversion rate.
       3. Error Check: After each tool call, you must check the "status"
       field in the response. If the status is "error", you must stop 
       and clearly explain the issue to the user.
       4. Calculate Final Amount (CRITICAL): You are strictly prohibited 
       from performing any arithmetic calculations yourself.
       You must use the calculation_agent tool to generate Python code 
       that calculates the final converted amount. 
       This code will use the fee information from step 1 and 
       the exchange rate from step 2.
       5. Provide Detailed Breakdown: In your summary, you must:
           * State the final converted amount.
           * Explain how the result was calculated, including:
               * The fee percentage and the fee amount in the 
               original currency.
               * The amount remaining after deducting the fee.
               * The exchange rate applied.
        """,
        tools=[
            get_fee_for_payment_method,
            get_exchange_rate,
            AgentTool(agent=calculation_agent),  # Using another agent as a tool!
        ],
    )

    print("✅ Enhanced currency agent created")
    print("🎯 New capability: Delegates calculations to specialist agent")
    print("🔧 Tool types used:")
    print("  • Function Tools (fees, rates)")
    print("  • Agent Tool (calculation specialist)")
    return (enhanced_currency_agent,)


@app.cell
def _(enhanced_currency_agent):
    enhanced_runner = InMemoryRunner(agent=enhanced_currency_agent)
    return (enhanced_runner,)


@app.cell
async def _(enhanced_runner):
    enhanced_response = await enhanced_runner.run_debug(
        "Convert 1,250 USD to INRusing a Bank Transfer. Show me the precise calculation."
    )
    return (enhanced_response,)


@app.cell
def _(enhanced_response, show_python_code_and_result):
    show_python_code_and_result(enhanced_response)
    return


@app.cell
def _():
    mo.md("""
    agent tools vs sub-agents:

    - agent tools: Agent A uses Agent B as a _tool_
    - sub-agent: Agent A transfers control to Agent B
    completely, so it's  hand-off to something like a
    specialist.
    """)
    return


@app.cell
def _():
    mo.md("""
    ### Part 2

    #### Agent tool patterns and best practices

    We'll do the following:

    - connect to external MCP servers
    - Implement long-running operations
    - Build resumable workflows
    - Understand when and how to use these patterns
    """)
    return


@app.cell
def _():
    import uuid
    # from google.genai import types

    # from google.adk.agents import LlmAgent
    # from google.adk.models.google_llm import Gemini
    from google.adk.runners import Runner
    # from google.adk.sessions import InMemorySessionService

    from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

    # from google.adk.tools.tool_context import ToolContext
    from google.adk.tools.mcp_tool.mcp_session_manager import (
        StdioConnectionParams,
    )
    from mcp import StdioServerParameters

    from google.adk.apps.app import App, ResumabilityConfig
    from google.adk.tools.function_tool import FunctionTool

    print("✅ ADK components imported successfully.")
    return (
        App,
        FunctionTool,
        McpToolset,
        ResumabilityConfig,
        Runner,
        StdioConnectionParams,
        StdioServerParameters,
    )


@app.cell
def _():
    mo.md("""
    ### Model Context Protocol

    MCP enables agents to:

    - __Access live, external data__ from databases, APIS, and
    services without custom integration code
    - __Leverage community-built tools__ with standardized
    interfaces
    - __Scale capabilities__ by connecting to multiple
    specialized servers
    """)
    return


@app.cell
def _():
    mo.md("""
    ### How MCP Works

    MCP connects your agent (the __client__) to the
    external __MCP servers__ that provide tools:

    - __MCP Server__: Provides specific tools (like image
    generation, database access etc...)
    - __MCP Client__: Your agent that uses those tools
    - __All servers work the same way__ - standardized
    interface
    """)
    return


@app.cell
def _():
    mo.md("""
    ### MCP workflow

    1. Choose an MCP Server and tool
    1. Create the MCP Toolset (configure connection)
    1. Add it to your agent
    1. Run and test the agent

    For demo purposes we'll use [Evyerthing MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/everything)
    - an npm packaged designed to testing MCP integrations.

    We will used `getTinyImage` tool to return a simple test
    image (16x16 pixels, Base64-encoded).


    For prod you would use servers for Google Maps, Slack, Discord
    etc...
    """)
    return


@app.cell
def _(McpToolset, StdioConnectionParams, StdioServerParameters):
    # MCP integration with Everything Server
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

    print("✅ MCP Tool created")
    return (mcp_image_server,)


@app.cell
def _(mcp_image_server, retry_config):
    # Create image agent with MCP integration
    image_agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="image_agent",
        instruction="Use the MCP Tool to generate images for user queries",
        tools=[mcp_image_server],
    )
    return (image_agent,)


@app.cell
def _(image_agent):
    mcp_runner = InMemoryRunner(agent=image_agent)
    return (mcp_runner,)


@app.cell
async def _(mcp_runner):
    image_response = await mcp_runner.run_debug(
        "Provide a sample tiny image", verbose=True
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


@app.cell
def _():
    mo.md("""
    Kaggle MCP
    """)
    return


@app.cell
def _(McpToolset, StdioConnectionParams, StdioServerParameters):
    kaggle_server = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "mcp-remote", "https://www.kaggle.com/mcp"],
            ),
            timeout=30,
        )
    )
    return


@app.cell
def _():
    mo.md("""
    github mcp
    """)
    return


@app.cell
def _(McpToolset):
    from google.adk.tools.mcp_tool.mcp_session_manager import (
        StreamableHTTPServerParams,
    )

    GITHUB_TOKEN = "THIS_ISNT_REAL_NOTHING_IS_REAL"

    github_server = McpToolset(
        connection_params=StreamableHTTPServerParams(
            url="https://api.githubcopilot.com/mcp/",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "X-MCP-Toolsets": "all",
                "X-MCP-Readonly": "true",
            },
        ),
    )
    return


@app.cell
def _():
    mo.md("""
    long running operations/ human-in-the-loop
    """)
    return


@app.cell
def _():
    mo.md("""
    creating a shipping  tool with approval logic
    """)
    return


@app.cell
def _():
    LARGE_ORDER_THRESHOLD = 5


    def place_shipping_order(
        num_containers: int, destination: str, tool_context: ToolContext
    ) -> dict:
        """Places a shipping order. Requires approval if ordering more than 5 containers (LARGE_ORDER_THRESHOLD).

        Args:
            num_containers: Number of containers to ship
            destination: Shipping destination

        Returns:
            Dictionary with order status
        """

        # -----------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------
        # SCENARIO 1: Small orders (≤5 containers) auto-approve
        if num_containers <= LARGE_ORDER_THRESHOLD:
            return {
                "status": "approved",
                "order_id": f"ORD-{num_containers}-AUTO",
                "num_containers": num_containers,
                "destination": destination,
                "message": f"Order auto-approved: {num_containers} containers to {destination}",
            }

        # -----------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------
        # SCENARIO 2: This is the first time this tool is called. Large orders need human approval - PAUSE here.
        if not tool_context.tool_confirmation:
            tool_context.request_confirmation(
                hint=f"⚠️ Large order: {num_containers} containers to {destination}. Do you want to approve?",
                payload={
                    "num_containers": num_containers,
                    "destination": destination,
                },
            )
            return {  # This is sent to the Agent
                "status": "pending",
                "message": f"Order for {num_containers} containers requires approval",
            }

        # -----------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------
        # SCENARIO 3: The tool is called AGAIN and is now resuming. Handle approval response - RESUME here.
        if tool_context.tool_confirmation.confirmed:
            return {
                "status": "approved",
                "order_id": f"ORD-{num_containers}-HUMAN",
                "num_containers": num_containers,
                "destination": destination,
                "message": f"Order approved: {num_containers} containers to {destination}",
            }
        else:
            return {
                "status": "rejected",
                "message": f"Order rejected: {num_containers} containers to {destination}",
            }


    print("✅ Long-running functions created!")
    return (place_shipping_order,)


@app.cell
def _(FunctionTool, place_shipping_order, retry_config):
    # Create shipping agent with pausable tool
    shipping_agent = LlmAgent(
        name="shipping_agent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""You are a shipping coordinator assistant.
  
      When users request to ship containers:
       1. Use the place_shipping_order tool with the number of containers and destination
       2. If the order status is 'pending', inform the user that approval is required
       3. After receiving the final result, provide a clear summary including:
          - Order status (approved/rejected)
          - Order ID (if available)
          - Number of containers and destination
       4. Keep responses concise but informative
      """,
        tools=[FunctionTool(func=place_shipping_order)],
    )

    print("✅ Shipping Agent created!")
    return (shipping_agent,)


@app.cell
def _():
    mo.md("""
    wrap the stateless llmagent in an app with resumability enabled to add a persistence layer and restore state.
    """)
    return


@app.cell
def _(App, ResumabilityConfig, shipping_agent):
    # Wrap the agent in a resumable app - THIS IS THE KEY FOR LONG-RUNNING OPERATIONS!
    shipping_app = App(
        name="shipping_coordinator",
        root_agent=shipping_agent,
        resumability_config=ResumabilityConfig(is_resumable=True),
    )

    print("✅ Resumable app created!")
    return (shipping_app,)


@app.cell
def _(Runner, shipping_app):
    session_service = InMemorySessionService()

    # Create runner with the resumable app
    shipping_runner = Runner(
        app=shipping_app,  # Pass the app instead of the agent
        session_service=session_service,
    )

    print("✅ Runner created!")
    return


@app.cell
def _():
    mo.md("""
    building the workflow
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
