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
    return


if __name__ == "__main__":
    app.run()
