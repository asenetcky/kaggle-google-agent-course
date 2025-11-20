# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "a2a==0.44",
#     "altair==6.0.0",
#     "duckdb==1.4.2",
#     "google-adk[a2a]==1.18.0",
#     "marimo>=0.17.0",
#     "polars[pyarrow]==1.35.2",
#     "protobuf==6.33.1",
#     "pytest==9.0.1",
#     "python-dotenv==1.2.1",
#     "python-lsp-ruff==2.3.0",
#     "python-lsp-server==1.13.2",
#     "pyzmq",
#     "requests==2.32.5",
#     "ruff==0.14.5",
#     "sqlglot==28.0.0",
#     "vegafusion==2.0.3",
#     "vl-convert-python==1.8.0",
#     "websockets==15.0.1",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # Agent to Agent Communication
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Agent2Agent (A2A) Communication with ADK
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    **Overview of Agent2Agent (A2A)**

    - The Problem: As you build more complex AI
    systems:
        - A single agent can't do everything
        - You need agents to collaborate
        - Different teams build different agents
        - Agents may use different languages/
        frameworks
    - The Solution: A2A Protocol - a standard that allows agents to:
        - Communicate over networks
        - Use each other's capabilities
        - Work across frameworks
        - Maintain formal contracts
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    **Common A2A Architecture Patterns**

    1. Cross-Framework Integration: ADK agent
    communicating with other agent frameworks
    1. Cross-language Communication: Python agent
    calling Java or Node.js agent
    1. Cross-Organization Boundaries: Your internal
    agent integrating with external vendor services
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Creating a practical e-commerce integration
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    1. Product Catalog Agent
        - Exposed via A2A
        - External vendor service that provides
        product information
    1. Customer Support Agent
        - Consumer
        - Your internal agent that helps
        customers by querying product data
    1. This Justifies A2A because:
        - Product Catalog is maintained by an
        external vendor
        (you *cannot* modify their code)
        - Different organizations with
        separate systems
        - Formal contract needed between
        services
        - Product catalog could be in a
        different language/framework
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## A2A vs Local Sub-Agents
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    - Agent location
        - Use A2A: External service/ different codebase
        - Use Local: same codebase/internal
    - Ownership
        - Use A2A: different team/org
        - Use Local: your team
    - Network
        - Use A2A: agents on diff machines
        - Use Local: same process/machine
    - Performance
        - Use A2A: network latency acceptable
        - Use Local: need low latency
    -Lang/Framework
        - Use A2A: cross-lang/framework needed
        - Use Local: same languages
    - Contract
        - Use A2A: formal api contract required
        - Use Local: interneral interface
    - Example
        - Use A2A: external vendor product catalog
        - Use Local: internal order processing steps
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### What we'll build

    **How it works:**

    1. Customer asks a product question to our
    Customer Support Agent
    1. Support Agent realizes it needs product
    information
    1. Support Agent calls the Product Catalog
    Agent via A2A protocol
    1. Product Catalog Agent (external vendor)
    returns product data
    1. Support agent formulates an answer and
    responds to the customer
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    We will:

    1. Create the product catalog agent - build
    the vendor's agent with product lookup
    1. Expose via A2A - Make it accessible use
    `to_a2a()`
    1. start the server - run the agent as a
    background service
    1. create the customer support agent - build
    the consumer agent
    1. test communication - see a2a in action with
    real queries
    1. understand the flow - learn what happened
    behind the scenes
    """)
    return


@app.cell
def _():
    import os
    import logging
    from dotenv import load_dotenv

    load_dotenv()

    try:
        GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    except Exception as e:
        print(
            f"Auth Error: Please make sure 'GOOGLE_API_KEY' is in environment. Details: {e}"
        )
    
    return (os,)


@app.cell
def _():
    import json
    import requests
    import subprocess
    import time
    import uuid

    from google.adk.agents import LlmAgent
    from google.adk.agents.remote_a2a_agent import (
        RemoteA2aAgent,
        AGENT_CARD_WELL_KNOWN_PATH,
    )

    from google.adk.a2a.utils.agent_to_a2a import to_a2a
    from google.adk.models.google_llm import Gemini
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    # Hide additional warnings in the notebook
    import warnings

    warnings.filterwarnings("ignore")

    print("✅ ADK components imported successfully.")
    return (
        AGENT_CARD_WELL_KNOWN_PATH,
        Gemini,
        InMemorySessionService,
        LlmAgent,
        RemoteA2aAgent,
        Runner,
        json,
        requests,
        subprocess,
        time,
        to_a2a,
        types,
        uuid,
    )


@app.cell
def _(types):
    retry_config = types.HttpRetryOptions(
        attempts=5,  # Maximum retry attempts
        exp_base=7,  # Delay multiplier
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
    )
    return (retry_config,)


@app.cell
def _(mo):
    mo.md("""
    ## Create the Product Catalog Agent (to be exposed)
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    Why expose this agent?

    - In a real system, this would be maintained
    by an external vendor or third-party provider
    - Your interal agents (customer support, sales,
    inventory) need product data
    - The vendor controls their own codebase - you
    can't modify their implementation
    - By exposing it via A2A, any authorized agent
    can consume it using the standard protocol
    """)
    return


@app.cell
def _(Gemini, LlmAgent, retry_config):
    # Define a product catalog lookup tool
    # In a real system, this would query the vendor's product database
    def get_product_info(product_name: str) -> str:
        """Get product information for a given product.

        Args:
            product_name: Name of the product (e.g., "iPhone 15 Pro", "MacBook Pro")

        Returns:
            Product information as a string
        """
        # Mock product catalog - in production, this would query a real database
        product_catalog = {
            "iphone 15 pro": "iPhone 15 Pro, $999, Low Stock (8 units), 128GB, Titanium finish",
            "samsung galaxy s24": "Samsung Galaxy S24, $799, In Stock (31 units), 256GB, Phantom Black",
            "dell xps 15": 'Dell XPS 15, $1,299, In Stock (45 units), 15.6" display, 16GB RAM, 512GB SSD',
            "macbook pro 14": 'MacBook Pro 14", $1,999, In Stock (22 units), M3 Pro chip, 18GB RAM, 512GB SSD',
            "sony wh-1000xm5": "Sony WH-1000XM5 Headphones, $399, In Stock (67 units), Noise-canceling, 30hr battery",
            "ipad air": 'iPad Air, $599, In Stock (28 units), 10.9" display, 64GB',
            "lg ultrawide 34": 'LG UltraWide 34" Monitor, $499, Out of Stock, Expected: Next week',
        }

        product_lower = product_name.lower().strip()

        if product_lower in product_catalog:
            return f"Product: {product_catalog[product_lower]}"
        else:
            available = ", ".join([p.title() for p in product_catalog.keys()])
            return f"Sorry, I don't have information for {product_name}. Available products: {available}"


    # Create the Product Catalog Agent
    # This agent specializes in providing product information from the vendor's catalog
    product_catalog_agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="product_catalog_agent",
        description="External vendor's product catalog agent that provides product information and availability.",
        instruction="""
        You are a product catalog specialist from an external vendor.
        When asked about products, use the get_product_info tool to fetch data from the catalog.
        Provide clear, accurate product information including price, availability, and specs.
        If asked about multiple products, look up each one.
        Be professional and helpful.
        """,
        tools=[get_product_info],  # Register the product lookup tool
    )

    print("✅ Product Catalog Agent created successfully!")
    print("   Model: gemini-2.5-flash-lite")
    print("   Tool: get_product_info()")
    print("   Ready to be exposed via A2A...")
    return (product_catalog_agent,)


@app.cell
def _(mo):
    mo.md("""
    ## Expose the Product Catalog Agent via A2A
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    What does `to_a2a()` do?

    1. wraps your agent in an A2A-compatible server (FastAPI/Starlette)
    2. Auto-generates an agent card that includes:
       - agent name, description and version
       - skills (tools/functions are "skills" in A2A)
       - Protocol version and endpoints
       - input/output modes
    3. Serves the agent card at a standard path (`/.well-known/agent-card.json`)
    4. Handles all A2A protocol details
       - request/response
       - formatting
       - task endpoints
    5. it's the **easiest way** to expose an ADK agent
        via A2A!
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Key concept: Agent Cards
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    An **agent card** is a JSON document that serves
    as a *business card* for your agent.

    It describes:

        - What the agent does(name, description, version)
        - What skills/tools it has
        - How to communicate with it (URL, protocol version, endpoints)

    It is the *contract* that tells other agents
    how to work with your agent.
    """)
    return


@app.cell
def _(product_catalog_agent, to_a2a):
    # Convert the product catalog agent to an A2A-compatible application
    # This creates a FastAPI/Starlette app that:
    #   1. Serves the agent at the A2A protocol endpoints
    #   2. Provides an auto-generated agent card
    #   3. Handles A2A communication protocol
    product_catalog_a2a_app = to_a2a(
        product_catalog_agent,
        port=8001,  # Port where this agent will be served
    )

    print("✅ Product Catalog Agent is now A2A-compatible!")
    print("   Agent will be served at: http://localhost:8001")
    print(
        "   Agent card will be at: http://localhost:8001/.well-known/agent-card.json"
    )
    print("   Ready to start the server...")
    return


@app.cell
def _(mo):
    mo.md("""
    ## Start the Product Catalog Agent Server
    """)
    return


@app.cell
def _(os, requests, subprocess, time):
    # First, let's save the product catalog agent to a file that uvicorn can import
    product_catalog_agent_code = '''
    import os
    from google.adk.agents import LlmAgent
    from google.adk.a2a.utils.agent_to_a2a import to_a2a
    from google.adk.models.google_llm import Gemini
    from google.genai import types

    retry_config = types.HttpRetryOptions(
        attempts=5,  # Maximum retry attempts
        exp_base=7,  # Delay multiplier
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
    )

    def get_product_info(product_name: str) -> str:
        """Get product information for a given product."""
        product_catalog = {
            "iphone 15 pro": "iPhone 15 Pro, $999, Low Stock (8 units), 128GB, Titanium finish",
            "samsung galaxy s24": "Samsung Galaxy S24, $799, In Stock (31 units), 256GB, Phantom Black",
            "dell xps 15": "Dell XPS 15, $1,299, In Stock (45 units), 15.6\\" display, 16GB RAM, 512GB SSD",
            "macbook pro 14": "MacBook Pro 14\\", $1,999, In Stock (22 units), M3 Pro chip, 18GB RAM, 512GB SSD",
            "sony wh-1000xm5": "Sony WH-1000XM5 Headphones, $399, In Stock (67 units), Noise-canceling, 30hr battery",
            "ipad air": "iPad Air, $599, In Stock (28 units), 10.9\\" display, 64GB",
            "lg ultrawide 34": "LG UltraWide 34\\" Monitor, $499, Out of Stock, Expected: Next week",
        }

        product_lower = product_name.lower().strip()

        if product_lower in product_catalog:
            return f"Product: {product_catalog[product_lower]}"
        else:
            available = ", ".join([p.title() for p in product_catalog.keys()])
            return f"Sorry, I don't have information for {product_name}. Available products: {available}"

    product_catalog_agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="product_catalog_agent",
        description="External vendor's product catalog agent that provides product information and availability.",
        instruction="""
        You are a product catalog specialist from an external vendor.
        When asked about products, use the get_product_info tool to fetch data from the catalog.
        Provide clear, accurate product information including price, availability, and specs.
        If asked about multiple products, look up each one.
        Be professional and helpful.
        """,
        tools=[get_product_info]
    )

    # Create the A2A app
    app = to_a2a(product_catalog_agent, port=8001)
    '''

    # Write the product catalog agent to a temporary file
    with open("/tmp/product_catalog_server.py", "w") as f:
        f.write(product_catalog_agent_code)

    print("📝 Product Catalog agent code saved to /tmp/product_catalog_server.py")

    # Start uvicorn server in background
    # Note: We redirect output to avoid cluttering the notebook
    server_process = subprocess.Popen(
        [
            "uvicorn",
            "product_catalog_server:app",  # Module:app format
            "--host",
            "localhost",
            "--port",
            "8001",
        ],
        cwd="/tmp",  # Run from /tmp where the file is
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            **os.environ
        },  # Pass environment variables (including GOOGLE_API_KEY)
    )

    print("🚀 Starting Product Catalog Agent server...")
    print("   Waiting for server to be ready...")

    # Wait for server to start (poll until it responds)
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(
                "http://localhost:8001/.well-known/agent-card.json", timeout=1
            )
            if response.status_code == 200:
                print(f"\n✅ Product Catalog Agent server is running!")
                print(f"   Server URL: http://localhost:8001")
                print(
                    f"   Agent card: http://localhost:8001/.well-known/agent-card.json"
                )
                break
        except requests.exceptions.RequestException:
            time.sleep(5)
            print(".", end="", flush=True)
    else:
        print("\n⚠️  Server may not be ready yet. Check manually if needed.")

    # Store the process so we can stop it later
    globals()["product_catalog_server_process"] = server_process
    return (response,)


@app.cell
def _(json, requests, response):
    # Fetch the agent card from the running server
    try:
        _response = requests.get(
            "http://localhost:8001/.well-known/agent-card.json", timeout=5
        )

        if _response.status_code == 200:
            agent_card = _response.json()
            print("📋 Product Catalog Agent Card:")
            print(json.dumps(agent_card, indent=2))

            print("\n✨ Key Information:")
            print(f"   Name: {agent_card.get('name')}")
            print(f"   Description: {agent_card.get('description')}")
            print(f"   URL: {agent_card.get('url')}")
            print(
                f"   Skills: {len(agent_card.get('skills', []))} capabilities exposed"
            )
        else:
            print(f"❌ Failed to fetch agent card: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching agent card: {e}")
        print(
            "   Make sure the Product Catalog Agent server is running (previous cell)"
        )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Create the customer support agent
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **how ti works**

    1. We'll use `RemoteA2Agent` to create a client-side proxy for the product catalog agent
    2. the customer support agent can use the product catalog agent like any other tool
    3. adk handles all the a2a protocol communications behind the scenes

    **How remotea2aAgent works:**

    - it's a *client-side proxy* that reads the remote agent's card
    - translates sub-agent calls into A2A protocol requests (HTTP POST to `/tasks`)
    - Handlees all the protocol details so we can just use it like a regular sub-agent
    """)
    return


@app.cell
def _(AGENT_CARD_WELL_KNOWN_PATH, RemoteA2aAgent):
    # Create a RemoteA2aAgent that connects to our Product Catalog Agent
    # This acts as a client-side proxy - the Customer Support Agent can use it like a local agent
    remote_product_catalog_agent = RemoteA2aAgent(
        name="product_catalog_agent",
        description="Remote product catalog agent from external vendor that provides product information.",
        # Point to the agent card URL - this is where the A2A protocol metadata lives
        agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    print("✅ Remote Product Catalog Agent proxy created!")
    print(f"   Connected to: http://localhost:8001")
    print(f"   Agent card: http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}")
    print("   The Customer Support Agent can now use this like a local sub-agent!")
    return (remote_product_catalog_agent,)


@app.cell
def _(Gemini, LlmAgent, remote_product_catalog_agent, retry_config):
    # Now create the Customer Support Agent that uses the remote Product Catalog Agent
    customer_support_agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="customer_support_agent",
        description="A customer support assistant that helps customers with product inquiries and information.",
        instruction="""
        You are a friendly and professional customer support agent.

        When customers ask about products:
        1. Use the product_catalog_agent sub-agent to look up product information
        2. Provide clear answers about pricing, availability, and specifications
        3. If a product is out of stock, mention the expected availability
        4. Be helpful and professional!

        Always get product information from the product_catalog_agent before answering customer questions.
        """,
        sub_agents=[remote_product_catalog_agent],  # Add the remote agent as a sub-agent!
    )

    print("✅ Customer Support Agent created!")
    print("   Model: gemini-2.5-flash-lite")
    print("   Sub-agents: 1 (remote Product Catalog Agent via A2A)")
    print("   Ready to help customers!")
    return (customer_support_agent,)


@app.cell
def _(mo):
    mo.md("""
    ## Test A2A Communication
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    We're going to ask the CSA about products and it will communicate with the PCA via A2A

    **Behind the Scenes:**

    1. Customer asks SA a question about product
    1. SA realizes it needs product info
    1. SA calls the `remote_product_catalog_agent` (RemoteA2aAgent)
    1. ADK sends the A2A protocol request to `http://localhost:8001`
    1. PCA processes the request and responds
    1. SA recieves the responses and continues
    1. Customer gets the final answer
    """)
    return


@app.cell
async def _(
    InMemorySessionService,
    Runner,
    customer_support_agent,
    types,
    uuid,
):
    async def test_a2a_communication(user_query: str):
        """
        Test the A2A communication between Customer Support Agent and Product Catalog Agent.

        This function:
        1. Creates a new session for this conversation
        2. Sends the query to the Customer Support Agent
        3. Support Agent communicates with Product Catalog Agent via A2A
        4. Displays the response

        Args:
            user_query: The question to ask the Customer Support Agent
        """
        # Setup session management (required by ADK)
        session_service = InMemorySessionService()

        # Session identifiers
        app_name = "support_app"
        user_id = "demo_user"
        # Use unique session ID for each test to avoid conflicts
        session_id = f"demo_session_{uuid.uuid4().hex[:8]}"

        # CRITICAL: Create session BEFORE running agent (synchronous, not async!)
        # This pattern matches the deployment notebook exactly
        session = await session_service.create_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

        # Create runner for the Customer Support Agent
        # The runner manages the agent execution and session state
        runner = Runner(
            agent=customer_support_agent, app_name=app_name, session_service=session_service
        )

        # Create the user message
        # This follows the same pattern as the deployment notebook
        test_content = types.Content(parts=[types.Part(text=user_query)])

        # Display query
        print(f"\n👤 Customer: {user_query}")
        print(f"\n🎧 Support Agent response:")
        print("-" * 60)

        # Run the agent asynchronously (handles streaming responses and A2A communication)
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=test_content
        ):
            # Print final response only (skip intermediate events)
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text"):
                        print(part.text)

        print("-" * 60)


    # Run the test
    print("🧪 Testing A2A Communication...\n")
    await test_a2a_communication("Can you tell me about the iPhone 15 Pro? Is it in stock?")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
