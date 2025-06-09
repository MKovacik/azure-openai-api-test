#!/usr/bin/env python3
"""
Azure OpenAI API Chat Application
A simple command-line chat application using Azure OpenAI API.
"""

import os
import sys
from dotenv import load_dotenv
import openai
import time
import argparse
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

# Initialize Rich console for better formatting
console = Console()

def setup_azure_openai_client():
    """Set up and return the Azure OpenAI client."""
    
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://temporarytesting.openai.azure.com/")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not api_key:
        console.print("[bold red]Error:[/bold red] AZURE_OPENAI_API_KEY not found. Please set it as an environment variable or in a .env file.")
        sys.exit(1)
    
    # Configure the Azure OpenAI client
    client = openai.AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2023-12-01-preview"  # Using a recent API version
    )
    
    return client

def get_available_models(client):
    """Get list of available models from Azure OpenAI."""
    try:
        models = client.models.list()
        model_ids = [model.id for model in models]
        return model_ids
    except Exception as e:
        console.print(f"[bold red]Error listing models:[/bold red] {str(e)}")
        sys.exit(1)

def chat_with_model(client, model_name):
    """Run an interactive chat session with the specified model."""
    
    console.print(Panel.fit(
        f"[bold green]Azure OpenAI Chat[/bold green]\n"
        f"Model: [bold cyan]{model_name}[/bold cyan]\n"
        "Type your messages and press Enter. Type 'exit', 'quit', or 'q' to end the conversation.",
        title="Chat Session Started",
        border_style="green"
    ))
    
    # Initialize conversation history
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    while True:
        # Get user input
        user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
        
        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit", "q"]:
            console.print("[yellow]Ending chat session. Goodbye![/yellow]")
            break
        
        # Add user message to history
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Display thinking indicator
            with console.status("[bold green]Thinking...[/bold green]"):
                start_time = time.time()
                
                # Get response from the model
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=800,
                    temperature=0.7
                )
                
                elapsed_time = time.time() - start_time
            
            # Extract and display the assistant's response
            assistant_message = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_message})
            
            # Display the response with markdown formatting
            console.print(f"\n[bold green]Assistant[/bold green] [dim]({elapsed_time:.2f}s)[/dim]:")
            console.print(Markdown(assistant_message))
            
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
            console.print("[yellow]Try again or type 'exit' to quit.[/yellow]")

def main():
    """Main function to run the chat application."""
    parser = argparse.ArgumentParser(description="Azure OpenAI Chat Application")
    parser.add_argument("--model", "-m", help="Model to use for chat (default: auto-select first available from preferred models)")
    parser.add_argument("--list", "-l", action="store_true", help="List available models and exit")
    args = parser.parse_args()
    
    # Set up the client
    client = setup_azure_openai_client()
    
    # Get available models
    available_models = get_available_models(client)
    
    if args.list:
        console.print("[bold]Available Models:[/bold]")
        for model in available_models:
            console.print(f"- {model}")
        return
    
    # Preferred models in order of preference
    preferred_models = ["gpt-4.1", "gpt-4.1-nano", "o4-mini", "gpt-4o", "gpt-35-turbo"]
    
    # Determine which model to use
    selected_model = None
    
    if args.model:
        # User specified a model
        if args.model in available_models:
            selected_model = args.model
        else:
            console.print(f"[bold red]Error:[/bold red] Model '{args.model}' not found in available models.")
            console.print("[yellow]Available models:[/yellow]")
            for model in available_models:
                console.print(f"- {model}")
            sys.exit(1)
    else:
        # Auto-select from preferred models
        for model in preferred_models:
            if model in available_models:
                selected_model = model
                break
        
        if not selected_model:
            # If none of the preferred models are available, use the first available model
            selected_model = available_models[0]
    
    # Start chat session with the selected model
    chat_with_model(client, selected_model)

if __name__ == "__main__":
    main()
