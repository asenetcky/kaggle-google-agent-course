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
    return


if __name__ == "__main__":
    app.run()
