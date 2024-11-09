from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import BartTokenizer, BartForConditionalGeneration
import json
import os

app = Flask(__name__)
CORS(app)

# Load the knowledge base
with open('knowledge_base.json', 'r') as f:
    knowledge_base = json.load(f)

# Initialize the BART model (without retriever)
#tokenizer = BartTokenizer.from_pretrained("facebook/bart-large")
#model = BartForConditionalGeneration.from_pretrained("facebook/bart-large")

# Initialize the BART model (with a smaller model)
tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")
model = BartForConditionalGeneration.from_pretrained("facebook/bart-base")


# Store the last destination the user asked about
last_destination = {"title": None}

def retrieve_document(query):
    query_lower = query.lower().strip()

    # Check if the user is asking about the last stored destination (contextual follow-up)
    if last_destination["title"]:
        for doc in knowledge_base:
            if doc["title"].lower() == last_destination["title"].lower():
                if "cost" in query_lower:
                    return f"The approximate cost for this trip is ${doc['cost']}."
                elif "best time" in query_lower:
                    return f"The best time to visit {last_destination['title'].split(' ')[2]} is {doc['best_time_to_visit']}."
                elif "activities" in query_lower:
                    return f"Some popular activities in {last_destination['title'].split(' ')[2]} include: {doc['activities']}."
                else:
                    return f"I'm sorry, I don't have information for that specific question about {last_destination['title'].split(' ')[2]}."

    # Loop through the knowledge base to find the trip
    for doc in knowledge_base:
        title_lower = doc['title'].lower().strip()
        
        if query_lower in title_lower or title_lower in query_lower:
            # Store the last asked destination
            last_destination['title'] = doc['title']
            
            # Return the initial response about the destination
            return f"{doc['content']} The approximate cost for this trip is ${doc['cost']}."
    
    return "Sorry, I couldn't find any relevant information."

def generate_bart_response(query):
    retrieved_doc = retrieve_document(query)
    combined_input = query + " " + retrieved_doc
    input_ids = tokenizer(combined_input, return_tensors="pt").input_ids
    outputs = model.generate(input_ids, max_new_tokens=50)
    response = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return response[0]

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    # Generate a response using the BART model
    response = generate_bart_response(user_query)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
