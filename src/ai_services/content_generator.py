# /home/ubuntu/neonadsai_backend/src/ai_services/content_generator.py

import os
from openai import OpenAI

# TODO: Load OpenAI API Key securely (e.g., from config/env)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI client initialized successfully.")
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
else:
    print("Warning: OPENAI_API_KEY environment variable not set. AI content generation will not function.")

def generate_ad_copy(prompt, model="gpt-4o-mini", max_tokens=150, num_variations=3):
    """Generates ad copy variations based on a given prompt using OpenAI."""
    if not client:
        print("OpenAI client not initialized. Cannot generate content.")
        return ["Error: AI client not initialized"] * num_variations

    try:
        # Construct a more specific prompt for marketing copy
        full_prompt = f"""Generate {num_variations} distinct marketing ad copy variations based on the following information. Each variation should include a headline (max 30 chars) and body text (max 90 chars). Focus on being engaging and relevant to the target audience.

Information:
{prompt}

Variations:"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert marketing copywriter specializing in short, impactful ad copy for social media and search ads."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=max_tokens * num_variations, # Adjust tokens based on expected output length
            n=1, # API generates one completion, we ask for variations within the prompt
            stop=None,
            temperature=0.7,
        )

        generated_text = response.choices[0].message.content.strip()
        print(f"Generated ad copy variations using {model}.")

        # Basic parsing assuming the AI follows the format (may need refinement)
        variations = []
        # Simple split logic, might need more robust parsing based on actual AI output format
        parts = generated_text.split("\n\n")
        for part in parts:
            if part.strip():
                variations.append(part.strip())

        # Ensure we return the requested number of variations, padding if necessary
        while len(variations) < num_variations:
            variations.append("Error: Could not generate enough variations.")

        return variations[:num_variations]

    except Exception as e:
        print(f"Error generating ad copy with OpenAI: {e}")
        return [f"Error: {e}"] * num_variations

# Example Usage:
# if __name__ == '__main__':
#     if OPENAI_API_KEY:
#         test_prompt = "Product: Eco-friendly water bottle. Target Audience: Hikers and outdoor enthusiasts. Key Selling Points: Durable, lightweight, keeps water cold for 24 hours."
#         copy_variations = generate_ad_copy(test_prompt)
#         for i, variation in enumerate(copy_variations):
#             print(f"--- Variation {i+1} ---")
#             print(variation)
#     else:
#         print("Set the OPENAI_API_KEY environment variable to run this example.")

