### Coding Harness Worklfow
LangGraph graph:  
![graph.png](graph.png)

## Done:
- skills' integration
- provider agnosticism (integrated openai library - supported by multiple providers - need to also include chat-completeions API in addition to responses API for better support)
- streaming response to user - in progress (streaming of sub-agents, tools and skills remains if desired)

### TODO:
- skills' separate tools - integrations setup instead of agentic_tools and agentic_skills
- streaming should include tool calls and subagent flows
- circular import (task_delegation and sub_agent nodes) resolution once and for all
- safety guards on shell tool
- git integration in agentic workflow
- proper context setup (like claude.md or something)
- edit file tool to perform changes in specific parts in file
- langsmith -> langfuse
- context limit auto updation based on model instead of env setting