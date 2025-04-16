from enum import Enum, auto
from typing import Dict, Optional, List, Callable, Any
from dataclasses import dataclass
import asyncio
import json

from mcp.server.fastmcp import FastMCP, Context

# Define the possible agent states
class AgentState(Enum):
    IDLE = auto()
    PLANNING = auto()
    RESEARCHING = auto()
    EXECUTING = auto()
    REVIEWING = auto()
    ERROR = auto()


@dataclass
class OrchestrationContext:
    """Context shared across the orchestration system"""
    # Current state of the agent
    current_state: AgentState = AgentState.IDLE
    # Store for conversation history
    conversation_history: List[Dict[str, str]] = None
    # Store for task-specific data
    task_data: Dict[str, Any] = None
    # Store for research/knowledge data
    knowledge_base: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.task_data is None:
            self.task_data = {}
        if self.knowledge_base is None:
            self.knowledge_base = {}
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def get_last_n_messages(self, n: int = 5) -> List[Dict[str, str]]:
        """Get the last N messages from the conversation history"""
        return self.conversation_history[-n:] if len(self.conversation_history) >= n else self.conversation_history[:]


# Create an MCP server for agent orchestration
mcp = FastMCP("Agent Orchestrator")

# Create a shared orchestration context
orchestration_ctx = OrchestrationContext()


# --- State Management Tools ---

@mcp.tool()
def transition_state(new_state: str, ctx: Context) -> str:
    """Transition the agent to a new state
    
    Args:
        new_state: The name of the state to transition to (IDLE, PLANNING, RESEARCHING, EXECUTING, REVIEWING, ERROR)
    """
    try:
        # Convert string to enum value
        target_state = AgentState[new_state.upper()]
        old_state = orchestration_ctx.current_state
        orchestration_ctx.current_state = target_state
        
        return f"Transitioned from {old_state.name} to {target_state.name}"
    except KeyError:
        valid_states = [state.name for state in AgentState]
        return f"Invalid state: {new_state}. Valid states are: {', '.join(valid_states)}"


@mcp.tool()
def get_current_state(ctx: Context) -> str:
    """Get the current state of the agent"""
    return orchestration_ctx.current_state.name


# --- Conversation Management Tools ---

@mcp.tool()
def add_user_message(message: str, ctx: Context) -> str:
    """Add a user message to the conversation history
    
    Args:
        message: The user's message content
    """
    orchestration_ctx.add_message("user", message)
    return "User message added to conversation history"


@mcp.tool()
def add_assistant_message(message: str, ctx: Context) -> str:
    """Add an assistant message to the conversation history
    
    Args:
        message: The assistant's message content
    """
    orchestration_ctx.add_message("assistant", message)
    return "Assistant message added to conversation history"


@mcp.tool()
def add_system_message(message: str, ctx: Context) -> str:
    """Add a system message to the conversation history
    
    Args:
        message: The system message content
    """
    orchestration_ctx.add_message("system", message)
    return "System message added to conversation history"


@mcp.tool()
def get_conversation_history(ctx: Context, max_messages: int = 10) -> str:
    """Get the conversation history
    
    Args:
        ctx: The MCP context
        max_messages: Maximum number of messages to return
    """
    history = orchestration_ctx.get_last_n_messages(max_messages)
    return json.dumps(history, indent=2)


# --- Task Management Tools ---

@mcp.tool()
def store_task_data(key: str, value: str, ctx: Context) -> str:
    """Store data in the task data store
    
    Args:
        key: The key to store the data under
        value: The data to store
    """
    orchestration_ctx.task_data[key] = value
    return f"Stored value under key: {key}"


@mcp.tool()
def get_task_data(key: str, ctx: Context) -> str:
    """Get data from the task data store
    
    Args:
        key: The key to retrieve data from
    """
    if key in orchestration_ctx.task_data:
        return str(orchestration_ctx.task_data[key])
    return f"No data found for key: {key}"


@mcp.tool()
def list_task_data_keys(ctx: Context) -> str:
    """List all keys in the task data store"""
    return json.dumps(list(orchestration_ctx.task_data.keys()))


# --- Knowledge Base Tools ---

@mcp.tool()
def store_knowledge(key: str, value: str, ctx: Context) -> str:
    """Store information in the knowledge base
    
    Args:
        key: The key to store the information under
        value: The information to store
    """
    orchestration_ctx.knowledge_base[key] = value
    return f"Stored knowledge under key: {key}"


@mcp.tool()
def get_knowledge(key: str, ctx: Context) -> str:
    """Get information from the knowledge base
    
    Args:
        key: The key to retrieve information from
    """
    if key in orchestration_ctx.knowledge_base:
        return str(orchestration_ctx.knowledge_base[key])
    return f"No knowledge found for key: {key}"


@mcp.tool()
def list_knowledge_keys(ctx: Context) -> str:
    """List all keys in the knowledge base"""
    return json.dumps(list(orchestration_ctx.knowledge_base.keys()))


# --- State-specific Prompts ---

@mcp.prompt()
def idle_prompt() -> str:
    """Prompt for the IDLE state"""
    return """
    I am currently in IDLE state, waiting for instructions.
    
    What would you like me to do? I can:
    
    1. Help you plan a task (transition to PLANNING)
    2. Research a topic (transition to RESEARCHING)
    3. Execute a specific action (transition to EXECUTING)
    
    Please provide your instructions, and I'll assist you accordingly.
    """


@mcp.prompt()
def planning_prompt(task_description: str) -> str:
    """Prompt for the PLANNING state
    
    Args:
        task_description: Description of the task to plan
    """
    return f"""
    I am currently in PLANNING state.
    
    Task to plan: {task_description}
    
    I'll break this down into steps:
    
    1. First, I'll analyze what the task requires
    2. Then, I'll identify the necessary sub-tasks
    3. Finally, I'll create a structured plan with clear steps
    
    After completing the plan, I can:
    - Move to RESEARCHING if we need more information
    - Move to EXECUTING if we're ready to act
    - Return to IDLE if we need to reconsider
    """


@mcp.prompt()
def researching_prompt(research_topic: str) -> str:
    """Prompt for the RESEARCHING state
    
    Args:
        research_topic: Topic to research
    """
    return f"""
    I am currently in RESEARCHING state.
    
    Research topic: {research_topic}
    
    I'll gather information on this topic by:
    
    1. Recalling relevant knowledge I already have
    2. Finding authoritative sources of information
    3. Organizing the information in a structured way
    
    Once research is complete, I can:
    - Return to PLANNING with new insights
    - Move to EXECUTING if we have enough information
    - Go to REVIEWING if we need to assess the findings
    """


@mcp.prompt()
def executing_prompt(action_plan: str) -> str:
    """Prompt for the EXECUTING state
    
    Args:
        action_plan: Plan of actions to execute
    """
    return f"""
    I am currently in EXECUTING state.
    
    Action plan:
    {action_plan}
    
    I'll now execute this plan step by step, providing updates as I go.
    
    I'll focus on:
    1. Following the plan precisely
    2. Handling any unexpected situations
    3. Recording the results of each step
    
    After execution, I'll move to REVIEWING to evaluate the results.
    """


@mcp.prompt()
def reviewing_prompt() -> str:
    """Prompt for the REVIEWING state"""
    return """
    I am currently in REVIEWING state.
    
    I'll now review what has been done so far:
    
    1. Examine the actions taken and their outcomes
    2. Compare results against the original objectives
    3. Identify any gaps or areas for improvement
    
    Based on this review, I can:
    - Return to PLANNING if adjustments are needed
    - Move to EXECUTING for further actions
    - Return to IDLE if the task is complete
    """


@mcp.prompt()
def error_prompt(error_description: str) -> str:
    """Prompt for the ERROR state
    
    Args:
        error_description: Description of the error
    """
    return f"""
    I am currently in ERROR state.
    
    Error: {error_description}
    
    I'll help resolve this issue by:
    
    1. Analyzing what went wrong
    2. Suggesting possible solutions
    3. Providing guidance on next steps
    
    After addressing the error, we can transition to an appropriate state to continue.
    """


# --- State-based Resource Access ---

@mcp.resource("state://current")
def get_state_info(ctx: Context) -> str:
    """Get information about the current state"""
    current_state = orchestration_ctx.current_state
    state_descriptions = {
        AgentState.IDLE: "Waiting for instructions. Ready to accept a new task.",
        AgentState.PLANNING: "Creating a structured plan to accomplish the task.",
        AgentState.RESEARCHING: "Gathering information needed to complete the task.",
        AgentState.EXECUTING: "Carrying out the planned actions step by step.",
        AgentState.REVIEWING: "Evaluating the results and determining next steps.",
        AgentState.ERROR: "Handling an error or unexpected situation."
    }
    
    return f"""
    Current State: {current_state.name}
    
    Description: {state_descriptions.get(current_state, "Unknown state")}
    
    Available Transitions:
    {_get_available_transitions(current_state)}
    """


@mcp.resource("state://{state_name}/prompt")
def get_state_prompt(state_name: str, ctx: Context) -> str:
    """Get the prompt for a specific state
    
    Args:
        state_name: Name of the state to get the prompt for
    """
    try:
        state = AgentState[state_name.upper()]
        prompt_getters = {
            AgentState.IDLE: lambda: idle_prompt(),
            AgentState.PLANNING: lambda: planning_prompt(
                orchestration_ctx.task_data.get("task_description", "No task description provided")
            ),
            AgentState.RESEARCHING: lambda: researching_prompt(
                orchestration_ctx.task_data.get("research_topic", "No research topic provided")
            ),
            AgentState.EXECUTING: lambda: executing_prompt(
                orchestration_ctx.task_data.get("action_plan", "No action plan provided")
            ),
            AgentState.REVIEWING: lambda: reviewing_prompt(),
            AgentState.ERROR: lambda: error_prompt(
                orchestration_ctx.task_data.get("error_description", "Unknown error")
            )
        }
        
        if state in prompt_getters:
            return prompt_getters[state]()
        return f"No prompt defined for state: {state_name}"
    except KeyError:
        valid_states = [state.name for state in AgentState]
        return f"Invalid state: {state_name}. Valid states are: {', '.join(valid_states)}"


@mcp.resource("orchestration://history")
def get_orchestration_history(ctx: Context) -> str:
    """Get the history of the orchestration process"""
    history = orchestration_ctx.conversation_history
    return json.dumps(history, indent=2)


# --- Helper Functions ---

def _get_available_transitions(current_state: AgentState) -> str:
    """Get available state transitions from the current state"""
    transitions = {
        AgentState.IDLE: [AgentState.PLANNING, AgentState.RESEARCHING, AgentState.EXECUTING],
        AgentState.PLANNING: [AgentState.IDLE, AgentState.RESEARCHING, AgentState.EXECUTING],
        AgentState.RESEARCHING: [AgentState.PLANNING, AgentState.EXECUTING, AgentState.REVIEWING],
        AgentState.EXECUTING: [AgentState.REVIEWING],
        AgentState.REVIEWING: [AgentState.PLANNING, AgentState.EXECUTING, AgentState.IDLE],
        AgentState.ERROR: [AgentState.IDLE, AgentState.PLANNING, AgentState.RESEARCHING, AgentState.EXECUTING]
    }
    
    available = transitions.get(current_state, [])
    if not available:
        return "No transitions available"
    
    return "\n".join([f"- {state.name}" for state in available])


# Run the server if executed directly
if __name__ == "__main__":
    mcp.run() 