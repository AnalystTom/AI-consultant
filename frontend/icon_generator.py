
def create_icon(project_name, client):

    user_prompt = f"""
Create a colorful, modern SVG icon for an MVP project called {{{project_name}}}. The icon should visually represent the core idea of the project in a minimalistic style, suitable for a tech application. Ensure the icon has clean lines, balanced proportions, and is easy to recognize at small sizes. The design should convey innovation and be versatile for digital products.

Output: Just output the xml as a string and NOTHING else. i.e
<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
...
</svg>
        """
    response = client.chat.completions.create(
            model="o1-mini",
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=2000,
        )

    if response and response.choices:
        message = response.choices[0].message.content.strip("```").strip("xml\n").strip("svg\n")
        return message

    return None