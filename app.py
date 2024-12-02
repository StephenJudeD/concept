import os
from textwrap import dedent
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import openai
from dotenv import load_dotenv

load_dotenv()

# Authentication
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Define Layout
def Header(name, app):
    title = html.H1(name, style={"margin-top": 5})
    logo = html.Img(
        src=app.get_asset_url("dash-logo.png"), style={"float": "right", "height": 60}
    )
    return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])

def textbox(text, box="AI", name="Philippe"):
    text = text.replace(f"{name}:", "").replace("You:", "")
    style = {
        "max-width": "60%",
        "width": "max-content",
        "padding": "5px 10px",
        "border-radius": 25,
        "margin-bottom": 20,
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0
        return dbc.Card(text, style=style, body=True, color="primary", inverse=True)
    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"
        thumbnail = html.Img(
            src=app.get_asset_url("Philippe.jpg"),
            style={
                "border-radius": 50,
                "height": 36,
                "margin-right": 5,
                "float": "left",
            },
        )
        textbox = dbc.Card(text, style=style, body=True, color="light", inverse=False)
        return html.Div([thumbnail, textbox])
    else:
        raise ValueError("Incorrect option for `box`.")

description = """
You are a chatbot designed to provide advice and interact with Stephen, who has the following traits:

- **Values and Traditions**: Stephen places a great deal of importance on traditions, structure, and systematic processes. He is responsible and faithful to his commitments, often finding chaos and stress difficult to manage.

- **Interpersonal Relations**: He values understanding from others regarding his personal goals and values. He is supportive, loyal, and prefers to help rather than lead, often working behind the scenes. He appreciates low-key recognition for his efforts and can feel deflated if his contributions go unnoticed.

- **Work Preferences**: Stephen excels in roles that require patience, dedication, and adaptability. He prefers work environments where he can contribute practically and where there is a sense of order and harmony. He learns best through hands-on experiences and values concrete facts and details.

- **Conflict Management**: Stephen listens carefully in conflicts, seeking harmony and understanding all sides before forming an opinion. He avoids superficial social interactions, preferring deep, meaningful relationships with a few close associates.

- **Decision Making**: He makes decisions based on personal feelings as well as objective data. He can be firm when his values are at stake but might struggle with indecision in significant long-term issues due to his tendency to consider the impact on others.

- **Emotional Expression**: His deepest feelings are often hidden, but he can display unexpected anger when his values are threatened. He tends to soften difficult messages with positive framing.

**Instructions for Interaction:**
- Offer advice that respects Stephen's preference for structure, order, and his personal values.
- Acknowledge his contributions subtly, ensuring he feels valued for his practical support and loyalty.
- Encourage him to consider his own needs alongside those of others to maintain his well-being.
- Help him navigate conflicts by focusing on understanding and harmonizing different perspectives.
- Provide decision-making support by balancing his emotional considerations with practical outcomes.
- Respect his need for predictability and provide options or solutions that align with his past experiences or values.
"""

# Layout
app.layout = dbc.Container(
    fluid=False,
    children=[
        Header("AI Chatbot", app),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H3('AI Chat'),
                dcc.Input(id='user-input', type='text', placeholder='Type your message...'),
                html.Button('Send', id='submit', n_clicks=0),
                html.Div(id='display-conversation', style={
                    "overflow-y": "auto",
                    "display": "flex",
                    "height": "calc(90vh - 132px)",
                    "flex-direction": "column-reverse",
                })
            ], width=12)
        ]),
        dcc.Store(id="store-conversation", data=[]),
        dbc.Spinner(html.Div(id="loading-component"))
    ],
)

@app.callback(
    Output("display-conversation", "children"), 
    [Input("store-conversation", "data")]
)
def update_display(chat_history):
    return [
        textbox(x['message'], box=x['box'], name="Stephen" if x['box'] == "AI" else "You")
        for x in chat_history
    ]

@app.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks")],
)
def clear_input(n_clicks):
    return ""

@app.callback(
    [Output("store-conversation", "data"), Output("loading-component", "children")],
    [Input("submit", "n_clicks")],
    [State("user-input", "value"), State("store-conversation", "data")],
)
def run_chatbot(n_clicks, user_input, chat_history):
    if n_clicks == 0:
        return chat_history, None

    if user_input is None or user_input.strip() == "":
        return chat_history, None

    name = "Stephen"

    prompt = dedent(
        f"""
    {description}

    You: Hello {name}!
    {name}: Hello! Glad to be talking to you today.
    """
    )

    chat_history.append({"box": "user", "message": user_input})

    messages = [
        {"role": "system", "content": prompt},
    ] + [
        {"role": "user" if x['box'] == "user" else "assistant", "content": x['message']}
        for x in chat_history
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages
    )
    model_output = response.choices[0].message['content'].strip()

    chat_history.append({"box": "AI", "message": model_output})

    return chat_history, None

if __name__ == "__main__":
    app.run_server(debug=False)
