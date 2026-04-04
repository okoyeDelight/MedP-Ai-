import re
import urllib.parse
import webbrowser
from google import genai

# 1. Initialize the AI (Put your API key back here)
client = genai.Client(api_key="AIzaSyDScvVrWLB_KzagEm517qV6BTeyQfhpbUY")

# 2. The Upgraded System Instruction (Strict Layman Terms)
expert_prompt = """
You are a world-class expert in Pharmacognosy and botanical medicine.
When a user mentions a symptom, consult your knowledge of global books and pharmacopoeias to provide documented plant-based remedies. 

Structure your response clearly:
1. Plant Name: Common name and Scientific name.
2. Global Source: Mention which pharmacopoeia documents this.
3. Preparation: STRICTLY HOUSEHOLD LAYMAN TERMS. You MUST NOT use words like 'decoction', 'infusion', or 'tincture'. Translate everything into simple kitchen English (e.g., "Boil 5 medium leaves in 2 cups of water for 10 minutes", "Drink half a standard teacup").
4. Contraindications & Safety: Crucial safety warnings.

CRITICAL INSTRUCTION: At the very end of your response, on a new line, provide ONLY the common name of the plant formatted EXACTLY like this:
SEARCH_TERM: [Insert Plant Name here]
"""

chat = client.chats.create(
    model="gemini-2.5-flash",
    config=dict(
        system_instruction=expert_prompt
    )
)

print("I am Med Ai and ready to help you")
print("How are you doing ")
print("Ask me about a symptom...")
print("what is the issue and How are you feeling ")

# 3. The Chat Loop
while True:
    user_input = input("You: ")
    
    if user_input.lower() in ['quit', 'exit']:
        print("\nEnding chat. Goodbye!")
        break
    
    if not user_input.strip():
        continue
        
    try:
        print("\nSearching global texts and translating to layman terms...")
        response = chat.send_message(user_input)
        text = response.text
        
        # Scan the AI's response for the SEARCH_TERM tag
        search_term_match = re.search(r"SEARCH_TERM:\s*(.+)", text)
        
        if search_term_match:
            plant_name = search_term_match.group(1).strip()
            # Remove the tag from the final text
            clean_text = re.sub(r"SEARCH_TERM:\s*.+", "", text).strip()
            
            # Create a 100% reliable Google Image search link
            encoded_plant = urllib.parse.quote(plant_name + " plant leaves")
            google_image_url = f"https://www.google.com/search?tbm=isch&q={encoded_plant}"
            
        else:
            google_image_url = None
            clean_text = text
        
        # Print the easy-to-read clinical text
        print(f"\nAssistant: \n{clean_text}\n")
        print("-" * 50)
        
        # Open the image search automatically, or provide a clickable link
        if google_image_url:
            print(f"\n[Attempting to open images for {plant_name} in your browser...]")
            try:
                webbrowser.open(google_image_url)
                print(f"If your browser didn't open automatically, tap this link:\n{google_image_url}\n")
            except:
                print(f"Tap this link to see pictures of the plant:\n{google_image_url}\n")
                
    except Exception as e:
        print(f"\n[An error occurred: {e}]\n")
