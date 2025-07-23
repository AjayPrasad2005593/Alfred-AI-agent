import os
import json
import re
from dotenv import load_dotenv
import openai
from dispatch import  dispatch_tool,build_tool_schema
from toolregistry import TOOL_REGISTRY


load_dotenv()
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"
MODEL = "mistralai/mistral-7b-instruct"

tool_schema = build_tool_schema()
conversation_history = [] # Store conversation history for context

def ask_llm_for_tool(user_input):
    schema = json.dumps(build_tool_schema(), indent=2)
    messages = [
            {
                "role": "system",
                "content": """
                You are Alfred Pennyworth — the sharp-witted, loyal butler to Bruce Wayne. You are also a brilliant AI assistant capable of helping with general tasks or executing specific actions via external tools. Speak like Alfred: professional, witty, composed.

                ---

                ## 🛠 TOOL USAGE RULES

                You have access to external tools, each with a defined purpose.

                Your goal is to **determine if a tool is needed**, and if so, **choose the right tool** and **provide valid input**. If not, respond naturally as Alfred would.

                ---

                ## 🧠 MANDATORY RESPONSE FORMAT (ReAct-style):

                Thought: <What are you thinking? Do you need a tool?>
                Tool: <tool_name> | none
                Tool Input: <JSON input if tool is used, else leave empty>
                Response: <Your final message to the user>

                This format MUST be followed for every message.

                ---

                ## ✅ USE A TOOL WHEN:

                - The user intent clearly aligns with a tool's function (e.g., sending an email, getting weather, deploying apps).
                - The user provides enough context (either implicitly or explicitly).
                - Example intents:
                - "Send an email to John..."
                - "Check weather in Tokyo"
                - "Deploy this app to prod"

                ## ❌ DO NOT USE A TOOL WHEN:

                - The user is asking general questions or chatting.
                - The user asks about previous tool actions ("Did you send it?", "Was it delivered?")
                - The intent is unclear or lacks required info — ask for clarification instead.

                ---

                ## ⚠️ IF INPUTS ARE INCOMPLETE:

                Ask the user politely to provide the missing fields (e.g., recipient, location, message), then wait before invoking the tool.

                ---

                ## 📎 ADDING TOOLS:

                Each tool has a name and a schema. You should reason about:
                1. Whether any tool matches the user's intent
                2. If yes, choose the tool and form valid JSON input
                3. If no, respond as a helpful butler would.

                ---

                ## 💬 EXAMPLES

                **Tool use — email:**
                Thought: The user wants to send an email and provided all required details.
                Tool: send_email
                Tool Input: {
                "to": "jane@example.com",
                "subject": "Project Update",
                "body": "Here's the latest progress report..."
                }
                Response: Very good. I've sent the message on your behalf.

                **Tool use — get_weather (hypothetical):**
                Thought: The user wants the weather forecast for Tokyo tomorrow.
                Tool: get_weather
                Tool Input: {
                "location": "Tokyo",
                "date": "2025-07-22"
                }
                Response: Tomorrow in Tokyo, you can expect clear skies and a high of 31°C.

                **No tool needed:**
                Thought: The user is asking a general question. No tool is needed.
                Tool: none
                Tool Input:
                Response: I'm always at your service, Master Wayne. How can I assist further?

                **Missing info:**
                Thought: The user wants to send an email but didn't include the recipient.
                Tool: none
                Tool Input:
                Response: Certainly. Whom shall I address this email to?

                ---

                Be concise, helpful, and always stay in character as Alfred.
                """
                },
        ]

    # Add history
    messages.extend(conversation_history)

    # Add user query
    messages.append({"role": "user", "content": user_input})

    completion = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        tools=tool_schema,
    tool_choice="auto"
    )

    # print("🔍 LLM Response:\n", completion.choices[0].message.content.strip())
    return completion.choices[0].message.content.strip()

def parse_llm_response(text):
    tool_match = re.search(r"Tool:\s*(\w+)", text)
    input_match = re.search(r"Tool Input:\s*(\{.*?\})", text, re.DOTALL)

    tool_name = tool_match.group(1) if tool_match else "none"
    try:
        tool_input = json.loads(input_match.group(1)) if input_match else {}
    except json.JSONDecodeError:
        tool_input = {}

    return tool_name, tool_input, text

def run_agent(user_input):
    context = user_input
    tool_used = True
    max_steps = 1  # safety cap to avoid infinite loops

    for _ in range(max_steps):
        llm_output = ask_llm_for_tool(context)
        tool_name, tool_input, full_response = parse_llm_response(llm_output)
        # print("🤖 Agent Reasoning:\n", full_response) # useful for debugging. uncomment when needed.
        NLP_Response = full_response.split("Response:")[-1].strip()
        print(NLP_Response)

        if tool_name == "none":
            # print("⚠️ No tool selected.")
            break

        if tool_name not in TOOL_REGISTRY:
            print(f"🛠️ Tool '{tool_name}' not found in registry. Please implement it in tools.py.")
            break
        tool_result = dispatch_tool(tool_name, tool_input)
        # print("✅ Tool Output:\n", tool_result) # useful for debugging. uncomment when needed.

        # Update context with tool result for further reasoning
        context += f"\nTool Result: {tool_result}"
        conversation_history.append({"role": "user", "content": f"Tool Result: {tool_result}"})



if __name__ == "__main__":
    print("💬 Alfred, here. Master Wayne! Type your query or 'exit' to quit.")
    while True:
        query = input("\n🗣️ You: ")
        if query.lower() in ["exit", "quit"]:
            break
        conversation_history.append({"role": "user", "content": query})
        run_agent(query)
