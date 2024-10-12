from openai import OpenAI

def generate_letter(issue, title, name):
    client = OpenAI()
    
    # Construct the prompt for the letter
    prompt = f"""
    You are a helpful assistant that assists in writing letters to local politicians. Please write a formal, concise, 2-paragraph letter addressing the issue of {issue}. Emphasize the seriousness of the problem and how it poses potential harm to municipal citizens like myself. Highlight why a problem like {issue} would be . 

    Convey that I trust public officials like {title} {name} to address and resolve these issues for the benefit of the community. Format the letter appropriately for email communication to a politician, ensuring it is professional and concise.
    """

    # Send the request to OpenAI
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You help me write formal emails."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the letter from the completion and return it
    print(completion.choices[0])
    return completion.choices[0].message.content

# Example usage
issue = "potholes"
title = "Senator"
name = "Jane Doe"

letter = generate_letter(issue, title, name)
print(letter)