import asyncio
import json
from typing import Dict, Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def simulate_task_planning_flow():
    """Simulate a complete flow through the planning process"""
    
    # Configure connection to our orchestrator server
    server_params = StdioServerParameters(
        command="python",
        args=["orchestrator.py"],
    )

    # Connect to the server via stdio
    async with stdio_client(server_params) as (read, write):
        # Create a client session
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("Connected to Agent Orchestrator")
            
            # Check the initial state
            print("\n=== Initial State ===")
            content, _ = await session.read_resource("state://current")
            print(content)
            
            # Get initial prompt
            print("\n=== Initial Prompt ===")
            initial_state = "IDLE"
            prompt, _ = await session.read_resource(f"state://{initial_state}/prompt")
            print(prompt)
            
            # Add a user message to start task planning
            print("\n=== User Request ===")
            user_message = "I need help creating a weekly content calendar for my blog"
            await session.call_tool("add_user_message", arguments={"message": user_message})
            print(f"User: {user_message}")
            
            # Store the task description
            await session.call_tool("store_task_data", arguments={
                "key": "task_description", 
                "value": "Create a weekly content calendar for a blog"
            })
            
            # Transition to PLANNING state
            print("\n=== Transitioning to PLANNING ===")
            result = await session.call_tool("transition_state", arguments={"new_state": "PLANNING"})
            print(result)
            
            # Get planning prompt
            print("\n=== Planning Prompt ===")
            prompt, _ = await session.read_resource("state://PLANNING/prompt")
            print(prompt)
            
            # Simulate assistant's planning response
            print("\n=== Assistant Planning ===")
            planning_response = """
            I've analyzed your request for a weekly content calendar. Here's my plan:
            
            1. Determine blog topics and categories
            2. Define content types (articles, videos, etc.)
            3. Create a weekly schedule template
            4. Assign topics to specific days
            5. Add metadata (keywords, target audience)
            
            We should start by researching content strategies.
            """
            await session.call_tool("add_assistant_message", arguments={"message": planning_response})
            print(f"Assistant: {planning_response}")
            
            # Store the action plan
            await session.call_tool("store_task_data", arguments={
                "key": "action_plan", 
                "value": planning_response
            })
            
            # Transition to RESEARCHING state
            print("\n=== Transitioning to RESEARCHING ===")
            result = await session.call_tool("transition_state", arguments={"new_state": "RESEARCHING"})
            print(result)
            
            # Store research topic
            await session.call_tool("store_task_data", arguments={
                "key": "research_topic", 
                "value": "Effective content calendar strategies"
            })
            
            # Get researching prompt
            print("\n=== Researching Prompt ===")
            prompt, _ = await session.read_resource("state://RESEARCHING/prompt")
            print(prompt)
            
            # Simulate research findings
            print("\n=== Research Results ===")
            research_findings = """
            Research findings on content calendars:
            
            1. Consistency is key - regular posting schedule increases engagement
            2. Theme days help organize content (e.g., Tutorial Tuesdays)
            3. Mix content types for variety (how-to, listicles, case studies)
            4. Plan content around key events and holidays
            5. Allow flexibility for trending topics
            """
            await session.call_tool("add_assistant_message", arguments={"message": research_findings})
            print(f"Assistant: {research_findings}")
            
            # Store findings in knowledge base
            await session.call_tool("store_knowledge", arguments={
                "key": "content_calendar_best_practices", 
                "value": research_findings
            })
            
            # Transition to EXECUTING state
            print("\n=== Transitioning to EXECUTING ===")
            result = await session.call_tool("transition_state", arguments={"new_state": "EXECUTING"})
            print(result)
            
            # Update the action plan based on research
            refined_plan = """
            Refined action plan based on research:
            
            1. Create a template with:
               - Monday: Industry news roundup
               - Tuesday: How-to tutorial
               - Wednesday: Case study
               - Thursday: Listicle or resource guide
               - Friday: Expert interview or opinion piece
            
            2. Schedule around upcoming events:
               - Plan special content for industry conferences
               - Create seasonal themes (summer series, etc.)
            
            3. Implement tracking:
               - Tag each piece with keywords and categories
               - Set performance metrics to track
            """
            await session.call_tool("store_task_data", arguments={
                "key": "action_plan", 
                "value": refined_plan
            })
            
            # Get executing prompt
            print("\n=== Executing Prompt ===")
            prompt, _ = await session.read_resource("state://EXECUTING/prompt")
            print(prompt)
            
            # Simulate execution results
            print("\n=== Execution Results ===")
            execution_result = """
            I've created your weekly content calendar:
            
            MONDAY: Industry News Roundup
            - Format: 5-7 key news items with brief commentary
            - Time: Publish by 9am
            
            TUESDAY: Tutorial Tuesday
            - Format: Step-by-step guide with images
            - Time: Publish by 11am
            
            WEDNESDAY: Case Study
            - Format: Problem-solution format, 1000-1500 words
            - Time: Publish by 2pm
            
            THURSDAY: Resource Roundup
            - Format: List of 7-10 useful resources with descriptions
            - Time: Publish by 11am
            
            FRIDAY: Expert Insights
            - Format: Q&A style or guest post, 800-1200 words
            - Time: Publish by 1pm
            
            WEEKEND: No new content, but schedule social media promotion of week's posts
            
            I've also prepared a Google Sheet template that you can use to plan specific topics for each slot.
            """
            await session.call_tool("add_assistant_message", arguments={"message": execution_result})
            print(f"Assistant: {execution_result}")
            
            # Transition to REVIEWING state
            print("\n=== Transitioning to REVIEWING ===")
            result = await session.call_tool("transition_state", arguments={"new_state": "REVIEWING"})
            print(result)
            
            # Get reviewing prompt
            print("\n=== Reviewing Prompt ===")
            prompt, _ = await session.read_resource("state://REVIEWING/prompt")
            print(prompt)
            
            # Simulate review
            print("\n=== Review Results ===")
            review_result = """
            Let's review what we've accomplished:
            
            1. We've created a comprehensive weekly content calendar with:
               - Specific content types for each day
               - Recommended formats and word counts
               - Publishing times
            
            2. The plan follows best practices identified in our research:
               - Consistent schedule
               - Themed days
               - Variety of content types
            
            3. The calendar provides structure while allowing flexibility for:
               - Trending topics
               - Seasonal content
               - Special events
            
            This meets your original request for a weekly content calendar. Is there anything specific you'd like to adjust or any questions about implementation?
            """
            await session.call_tool("add_assistant_message", arguments={"message": review_result})
            print(f"Assistant: {review_result}")
            
            # Simulate user feedback
            print("\n=== User Feedback ===")
            user_feedback = "This looks great! I think this will really help me stay organized. Can you recommend any tools for managing this calendar?"
            await session.call_tool("add_user_message", arguments={"message": user_feedback})
            print(f"User: {user_feedback}")
            
            # Transition back to RESEARCHING for tool recommendations
            print("\n=== Transitioning back to RESEARCHING ===")
            result = await session.call_tool("transition_state", arguments={"new_state": "RESEARCHING"})
            print(result)
            
            # Update research topic
            await session.call_tool("store_task_data", arguments={
                "key": "research_topic", 
                "value": "Content calendar management tools"
            })
            
            # Get researching prompt
            print("\n=== New Research Prompt ===")
            prompt, _ = await session.read_resource("state://RESEARCHING/prompt")
            print(prompt)
            
            # Simulate final response with tool recommendations
            print("\n=== Final Recommendations ===")
            final_response = """
            Here are some excellent tools for managing your content calendar:
            
            1. Trello - Visual board style organization, good for seeing your content pipeline
            2. Asana - More robust project management features, good for team collaboration
            3. CoSchedule - Specialized for content marketing, integrates with WordPress
            4. Google Calendar + Sheets - Free, flexible, and familiar interface
            5. Airtable - Combines spreadsheet with database features, highly customizable
            
            For your needs, I'd recommend starting with either Trello (simpler) or Airtable (more powerful) as they're both user-friendly and have free tiers.
            """
            await session.call_tool("add_assistant_message", arguments={"message": final_response})
            print(f"Assistant: {final_response}")
            
            # Transition back to IDLE state to complete the flow
            print("\n=== Completing Task - Returning to IDLE ===")
            result = await session.call_tool("transition_state", arguments={"new_state": "IDLE"})
            print(result)
            
            # Get final state info
            print("\n=== Final State ===")
            content, _ = await session.read_resource("state://current")
            print(content)
            
            # Get the orchestration history
            print("\n=== Conversation History Summary ===")
            history, _ = await session.read_resource("orchestration://history")
            history_data = json.loads(history)
            print(f"Total messages: {len(history_data)}")
            print(f"Message distribution: {count_roles(history_data)}")


def count_roles(messages):
    """Count the number of messages by role"""
    counts = {}
    for message in messages:
        role = message.get("role", "unknown")
        counts[role] = counts.get(role, 0) + 1
    return counts


if __name__ == "__main__":
    asyncio.run(simulate_task_planning_flow()) 