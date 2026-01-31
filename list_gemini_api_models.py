
import google.generativeai as genai
import os

def main():
    # Ensure GOOGLE_API_KEY is set in environment variables
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please set it to your Gemini API key before running this script.")
        return

    genai.configure(api_key=api_key)

    print("Available Gemini Models:")
    try:
        for model in genai.list_models():
            print(f"- {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
        print("Please ensure your GOOGLE_API_KEY is valid and has access to the Gemini API.")

if __name__ == "__main__":
    main()
