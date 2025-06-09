# Azure OpenAI API Test Project

This project provides tools to test and interact with Azure OpenAI services. It includes a connection test script and an enhanced command-line chat application with detailed model documentation.

## Configuration

The project uses environment variables for configuration. Create a `.env` file in the project root with the following variables:

```
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
```

**Note:** For convenience, an `.env_example` file is provided. You can rename it to `.env` and update it with your actual credentials:

```
cp .env_example .env
# Then edit the .env file with your actual credentials
```

## Installation

1. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Available Scripts

### Connection Test

Run the connection test script to verify your Azure OpenAI API configuration:

```
python azure_openai_test.py
```

This script will:
- Connect to your Azure OpenAI endpoint
- List all available models
- Check if expected models are available
- Make a test completion request

### Chat Application

The chat application provides an interactive command-line interface to chat with Azure OpenAI models and includes detailed documentation about model capabilities.

```
python azure_openai_chat.py
```

Options:
- `--model` or `-m`: Specify a model to use (e.g., `--model gpt-4.1`)
- `--list` or `-l`: Display detailed documentation about available models including:
  - Required API versions
  - Max token parameters
  - Output token limits
  - Vision support
  - And other model-specific configuration details

Examples:
```
# Start a chat with the gpt-4.1 model
python azure_openai_chat.py --model gpt-4.1

# View detailed model documentation
python azure_openai_chat.py --list
```

To exit the chat, type `exit`, `quit`, or `q`.

## Available Models

The project is configured to work with the following models:
- o4-mini

However, it will work with any model available in your Azure OpenAI service.

## Region

This project is configured to use the France Central region.
