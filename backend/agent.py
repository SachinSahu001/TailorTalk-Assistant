import os
import dateparser
from dotenv import load_dotenv  # type: ignore
from datetime import datetime, timedelta

from backend.calendar_utils import get_free_slots, create_event
from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent  # type: ignore
from langchain.tools import tool  # type: ignore
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder  # type: ignore

# ✅ Load environment variables
load_dotenv()

# 🔐 Gemini config
model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise EnvironmentError("❌ GOOGLE_API_KEY is missing in .env")

# ✅ Initialize Gemini model
llm = ChatGoogleGenerativeAI(model=model, temperature=0.2)
print(f"✅ Gemini model loaded: {model}")

# ✅ Tool: Check calendar availability
@tool
def check_availability(time_range: str) -> str:
    """Returns available calendar slots in the next 3 days."""
    try:
        start = datetime.now()
        end = start + timedelta(days=3)
        slots = get_free_slots(start, end)
        if not slots:
            return "No available slots in the next 3 days."
        return "\n".join([
            f"{s.strftime('%Y-%m-%d %I:%M %p')} to {e.strftime('%I:%M %p')}"
            for s, e in slots
        ])
    except Exception as e:
        return f"❌ Error checking availability: {str(e)}"

# ✅ Tool: Book a meeting
@tool
def book_meeting(start_time: str) -> str:
    """Books a 30-min meeting using natural language time (e.g. 'tomorrow at 3 PM')."""
    try:
        start = dateparser.parse(start_time)
        if not start:
            return "❌ Couldn't parse time. Try saying 'tomorrow at 4 PM'."
        end = start + timedelta(minutes=30)
        create_event(start, end)
        return f"✅ Meeting booked for {start.strftime('%Y-%m-%d %I:%M %p')}"
    except Exception as e:
        return f"❌ Failed to book meeting: {str(e)}"

# ✅ Define tools
tools = [check_availability, book_meeting]

# ✅ Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that manages Google Calendar bookings."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# ✅ Create Gemini-compatible agent
base_agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# ✅ Wrap agent into executor
agent = AgentExecutor(
    agent=base_agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=True
)

# ✅ Unified runner for API or CLI
def run_agent(user_input: str) -> str:
    if not user_input.strip():
        return "⚠️ Please enter something to book or check availability."

    try:
        response = agent.invoke({"input": user_input})

        # Preferred: LLM output
        if "output" in response and response["output"]:
            return response["output"]

        # Fallback: last tool response
        steps = response.get("intermediate_steps", [])
        if steps and len(steps[-1]) > 1:
            return f"✅ {steps[-1][1]}"

        return "⚠️ No meaningful response from the agent."

    except Exception as e:
        return f"❌ Agent crashed: {str(e)}"
