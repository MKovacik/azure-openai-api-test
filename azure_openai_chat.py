#!/usr/bin/env python3
"""
Azure OpenAI Environment Guide & Chat Client

A command-line tool designed to act as a go-to reference for developers
in this specific Azure environment. It provides detailed, static documentation
for available models and a client for interactive chat that handles model-specific
parameter requirements.
"""

import os
import sys
import argparse
import time
from dotenv import load_dotenv
import openai
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

# --- Configuration & Setup ---

# Initialize Rich console for beautiful terminal output
console = Console()

# Load environment variables from a .env file if it exists
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

# --- Static Model Documentation ---
# This section serves as a replacement for the official Azure documentation
# for the models deployed in this environment. It includes model-specific
# API parameter names to prevent runtime errors.

MODEL_DOCUMENTATION = {
    # NOTE: "gpt-4.1" is your internal name for the gpt-4o model deployment.
    "gpt-4.1": {
        "official_name": "gpt-4o",
        "description": "Flagship multimodal model. Best performance, supports text and image analysis.",
        "api_version": "2024-05-01-preview",
        "context_window": "128,000 tokens",
        "max_output_tokens": "8,192 tokens",
        "token_param_name": "max_completion_tokens", # CORRECTED: Newer models use this parameter
        "supports_vision": True,
        "supports_function_calling": True,
        "documentation_url": "https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#gpt-4-and-gpt-4-turbo-models"
    },
    # NOTE: "gpt-4.1-nano" is one of your internal names for the gpt-4o-mini deployment.
    "gpt-4.1-nano": {
        "official_name": "gpt-4o-mini",
        "description": "A smaller, faster, and more economical model. Excellent for high-throughput tasks.",
        "api_version": "2024-12-01-preview",
        "context_window": "128,000 tokens",
        "max_output_tokens": "16,384 tokens",
        "token_param_name": "max_completion_tokens", # CORRECTED: Newer models use this parameter
        "supports_vision": False,
        "supports_function_calling": True,
        "documentation_url": "https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#gpt-4o-and-gpt-4o-mini"
    },
    # NOTE: "o4-mini" is another internal name for the gpt-4o-mini deployment.
    "o4-mini": {
        "official_name": "gpt-4o-mini",
        "description": "A smaller, faster, and more economical model. Excellent for high-throughput tasks.",
        "api_version": "2024-12-01-preview",
        "context_window": "128,000 tokens",
        "max_output_tokens": "16,384 tokens",
        "token_param_name": "max_completion_tokens", # CORRECTED: Newer models use this parameter
        "supports_vision": False,
        "supports_function_calling": True,
        "documentation_url": "https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#gpt-4o-and-gpt-4o-mini"
    }
}


# --- Core Functions ---

def display_documentation():
    """
    Displays the static, detailed documentation for the environment's models.
    """
    panel_content = (
        "This is a guide to the Azure OpenAI models configured for our environment.\n"
        "Use the [bold cyan]Deployment Name[/bold cyan] with the `--model` flag to start a chat."
    )
    console.print(Panel(panel_content, title="[bold blue]Developer's Guide to Our Azure OpenAI Models[/bold blue]", border_style="blue"))

    table = Table(title="[bold]Model Configuration & Capabilities[/bold]", title_style="bold magenta", padding=(0, 1))
    table.add_column("Deployment Name", style="cyan", no_wrap=True)
    table.add_column("Official Model", style="green")
    table.add_column("Required API Version", style="yellow")
    table.add_column("Token Param", style="red") # ADDED this column for clarity
    table.add_column("Max Output Tokens", style="blue")
    table.add_column("Vision Support", style="magenta")
    table.add_column("Details & Description", style="white")

    for name, details in MODEL_DOCUMENTATION.items():
        vision_status = "Yes" if details["supports_vision"] else "No"
        url = details['documentation_url']
        description = f"{details['description']}\n[dim][link={url}]Official Docs[/link][/dim]"
        
        table.add_row(
            name,
            details["official_name"],
            details["api_version"],
            details["token_param_name"],
            details["max_output_tokens"],
            vision_status,
            description
        )
    console.print(table)
    console.print(f"\n[bold]Client Endpoint Configured:[/bold] {AZURE_OPENAI_ENDPOINT or '[bold red]Not Set[/bold red]'}")


def create_azure_openai_client(api_version):
    """Creates and returns an Azure OpenAI client."""
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        console.print(
            "[bold red]Error:[/bold red] Environment variables [cyan]AZURE_OPENAI_ENDPOINT[/cyan] and "
            "[cyan]AZURE_OPENAI_API_KEY[/cyan] must be set to run a chat."
        )
        sys.exit(1)
    return openai.AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=api_version,
    )

def verify_model_availability(client, model_name):
    """Checks if the specified model deployment exists on Azure."""
    try:
        available_models = [model.id for model in client.models.list().data]
        if model_name not in available_models:
            console.print(f"[bold red]Error:[/bold red] Deployment '[bold]{model_name}[/bold]' not found on the Azure endpoint.")
            console.print("[bold]Available deployments found:[/bold]", ", ".join(available_models) or "None")
            sys.exit(1)
        return True
    except Exception as e:
        console.print(f"[bold red]Error connecting to Azure to verify model:[/bold red] {e}")
        sys.exit(1)

def run_chat_session(model_name):
    """Runs an interactive chat session with the specified model."""
    if model_name not in MODEL_DOCUMENTATION:
        console.print(f"[bold red]Error:[/bold red] '{model_name}' is not a known model in this script's documentation.")
        console.print("[yellow]Available models are:[/yellow]", ", ".join(MODEL_DOCUMENTATION.keys()))
        sys.exit(1)

    model_info = MODEL_DOCUMENTATION[model_name]
    api_version = model_info["api_version"]
    
    client = create_azure_openai_client(api_version)

    with console.status("[bold green]Connecting to Azure and verifying model deployment...[/bold green]"):
        verify_model_availability(client, model_name)

    panel_title = f"[bold green]Chat with {model_info['official_name']} ({model_name})[/bold green]"
    panel_content = f"API Version: [cyan]{api_version}[/cyan]\nType 'exit', 'quit', or 'q' to end."
    console.print(Panel(panel_content, title=panel_title, border_style="green"))

    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Ending chat session. Goodbye![/yellow]")
                break

            messages.append({"role": "user", "content": user_input})
            
            with console.status("[bold green]Assistant is thinking...[/bold green]"):
                start_time = time.time()

                # --- DYNAMIC PARAMETER HANDLING ---
                # Build the request parameters dynamically based on the model's documentation
                token_param_name = model_info["token_param_name"]
                max_tokens_value = int(model_info["max_output_tokens"].split()[0].replace(",", ""))

                chat_params = {
                    "model": model_name,
                    "messages": messages,
                    token_param_name: max_tokens_value
                }
                
                response = client.chat.completions.create(**chat_params)
                # --- END DYNAMIC HANDLING ---

                assistant_message = response.choices[0].message.content
                elapsed_time = time.time() - start_time
            
            messages.append({"role": "assistant", "content": assistant_message})
            console.print(f"\n[bold green]Assistant[/bold green] [dim]({elapsed_time:.2f}s)[/dim]:")
            console.print(Markdown(assistant_message))

        except KeyboardInterrupt:
            console.print("\n[yellow]Chat interrupted.[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]An error occurred:[/bold red] {e}")
            messages.pop()

# --- Main Execution ---

def main():
    """Main function to parse arguments and run the application."""
    parser = argparse.ArgumentParser(
        description="Azure OpenAI Guide and Chat Client.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Display the detailed documentation for configured models and exit."
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        help="The deployment name of the model to chat with (e.g., gpt-4.1)."
    )
    args = parser.parse_args()

    if args.list:
        display_documentation()
        return

    if args.model:
        run_chat_session(args.model)
    else:
        console.print("[bold]Welcome to the Azure OpenAI Client![/bold]")
        console.print("To start a chat, use the [cyan]--model <deployment_name>[/cyan] argument.")
        console.print("To see the guide with all model details, use the [cyan]--list[/cyan] flag.")

if __name__ == "__main__":
    main()