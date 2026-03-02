"""Memory Backend Agent – Deep Agent using MemoryBackend for path-keyed storage.

Files written via the agent's filesystem tools (e.g. under /notes/) are stored
as path-keyed records in a PathMemoryStore instead of the filesystem. This
example uses an in-memory store; in production you can use PowerMemPathStore
with PowerMem or any other PathMemoryStore implementation.
"""

import argparse
import os
import sys

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from rich.console import Console
from rich.panel import Panel

from deepagents import create_deep_agent
from deepagents.backends import MemoryBackend

from store import InMemoryPathStore

load_dotenv()

console = Console()

# In-memory store shared across invocations in this process.
# Replace with PowerMemPathStore(memory) for persistent, multi-tenant storage.
_path_store = InMemoryPathStore()


def _get_model() -> BaseChatModel:
    """Use Qwen (OpenAI-compatible API) if OPENAI_API_BASE is set, else Anthropic Claude."""
    base_url = os.environ.get("OPENAI_API_BASE")
    if base_url:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            base_url=base_url.rstrip("/"),
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            model=os.environ.get("OPENAI_MODEL", "qwen-plus"),
            temperature=0,
        )
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0,
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )


def create_memory_backend_agent():
    """Create a Deep Agent that uses MemoryBackend with path-keyed storage."""
    model = _get_model()

    # BackendFactory: receives runtime at invocation time
    def backend_factory(runtime):
        return MemoryBackend(_path_store, runtime)

    agent = create_deep_agent(
        model=model,
        memory=["./AGENTS.md"],
        skills=[],
        tools=[],
        subagents=[],
        backend=backend_factory,
    )
    return agent


def main():
    parser = argparse.ArgumentParser(
        description="Deep Agent with MemoryBackend (path-keyed storage)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py "Save a note to /notes/ideas.txt with: brainstorm list"
  python agent.py "List files under /notes/"
  python agent.py "What did I save in /notes/ideas.txt?"
        """,
    )
    parser.add_argument(
        "message",
        type=str,
        nargs="?",
        default="List any files under / and tell me what's there.",
        help="User message (default: list root and describe)",
    )
    args = parser.parse_args()

    console.print(
        Panel(f"[bold cyan]Message:[/bold cyan] {args.message}", border_style="cyan")
    )
    console.print()

    console.print("[dim]Creating agent (MemoryBackend)...[/dim]")
    agent = create_memory_backend_agent()

    console.print("[dim]Invoking...[/dim]\n")
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": args.message}]}
        )
        final = result["messages"][-1]
        answer = final.content if hasattr(final, "content") else str(final)
        console.print(
            Panel(f"[bold green]Agent:[/bold green]\n\n{answer}", border_style="green")
        )
    except Exception as e:
        console.print(
            Panel(f"[bold red]Error:[/bold red]\n\n{str(e)}", border_style="red")
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
