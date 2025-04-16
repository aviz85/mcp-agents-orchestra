# MCP Agent Orchestration System

This project demonstrates how to build an agent orchestration system using the Model Context Protocol (MCP) Python SDK. It implements a state machine pattern to manage agent behavior and transitions between different operational modes.

## Overview

The orchestration system defines a set of states that an agent can be in:

- **IDLE**: Waiting for instructions
- **PLANNING**: Creating a structured plan for a task
- **RESEARCHING**: Gathering information needed for a task
- **EXECUTING**: Carrying out planned actions
- **REVIEWING**: Evaluating results and determining next steps
- **ERROR**: Handling errors or unexpected situations

Each state has its own set of behaviors, appropriate prompts, and available transitions to other states.

## Core Features

- **State Management**: Transition between different agent states
- **Context Preservation**: Maintain conversation history and state across transitions
- **Dynamic Prompting**: State-specific prompts that adapt to the current context
- **Knowledge Base**: Store and retrieve information found during research
- **Task Data Management**: Track task-specific information as it evolves

## Architecture

The system is built on three main components:

1. **Orchestrator MCP Server**: Manages state transitions, provides prompts, and maintains context
2. **Client**: Interacts with the orchestrator to drive the agent's behavior
3. **State Machine**: Defines the states and valid transitions between them

## Getting Started

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Demo

Start the orchestration server:

```bash
python orchestrator.py
```

In a separate terminal, run the client to see a demonstration of the state transitions:

```bash
python orchestrator_client.py
```

## Implementing Custom Flows

To create your own agent flows, you can:

1. Add new states to the `AgentState` enum
2. Define new prompts for these states
3. Update the transition rules in `_get_available_transitions`
4. Create custom tools specific to your application

## Example Use Cases

This orchestration pattern is useful for:

- **Complex Task Planning**: Breaking down complex tasks into manageable steps
- **Research Agents**: Agents that need to gather, analyze, and synthesize information
- **Multi-stage Workflows**: Processes that involve different modes of operation
- **Conversational Context Management**: Maintaining appropriate context as a conversation evolves

## License

This project is licensed under the MIT License - see the LICENSE file for details. 