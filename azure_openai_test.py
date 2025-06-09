#!/usr/bin/env python3
"""
Azure OpenAI API Connection Test Script
This script tests the connection to Azure OpenAI API and verifies model availability.
"""

import os
import sys
from dotenv import load_dotenv
import openai
import time

def test_azure_openai_connection():
    """Test connection to Azure OpenAI API and verify model availability."""
    
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://temporarytesting.openai.azure.com/")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not api_key:
        print("Error: AZURE_OPENAI_API_KEY not found. Please set it as an environment variable or in a .env file.")
        sys.exit(1)
    
    # Configure the Azure OpenAI client
    client = openai.AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2023-12-01-preview"  # Using a recent API version
    )
    
    print(f"Connecting to Azure OpenAI endpoint: {endpoint}")
    print(f"Region: France Central (as configured in the Azure portal)")
    
    # Test listing models
    try:
        print("\nAttempting to list available models...")
        models = client.models.list()
        print("✅ Successfully connected to Azure OpenAI API")
        
        print("\nAvailable models:")
        expected_models = ["gpt-4.1", "gpt-4.1-nano", "o4-mini"]
        found_models = []
        
        for model in models:
            print(f"- {model.id}")
            found_models.append(model.id)
        
        # Check if expected models are available
        for model_name in expected_models:
            if model_name in found_models:
                print(f"✅ Expected model '{model_name}' is available")
            else:
                print(f"❌ Expected model '{model_name}' was NOT found")
                
    except Exception as e:
        print(f"❌ Error listing models: {str(e)}")
        sys.exit(1)
    
    # Test a simple completion with one of the models
    try:
        # Try with the first available model from the expected list that was found
        test_model = next((m for m in expected_models if m in found_models), None)
        
        if test_model:
            print(f"\nTesting completion with model: {test_model}")
            start_time = time.time()
            
            response = client.chat.completions.create(
                model=test_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, this is a test message. Please respond with a short greeting."}
                ],
                max_tokens=100
            )
            
            elapsed_time = time.time() - start_time
            
            print(f"✅ Successfully received response in {elapsed_time:.2f} seconds")
            print(f"Response: {response.choices[0].message.content}")
        else:
            print("⚠️ No expected models were found. Skipping completion test.")
    
    except Exception as e:
        print(f"❌ Error testing completion: {str(e)}")

if __name__ == "__main__":
    test_azure_openai_connection()
