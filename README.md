### Coding Harness Worklfow
LangGraph graph:  
![graph.png](graph.png)

## Done:
- skills' integration
- provider agnosticism (integrated openai library - supported by multiple providers - need to also include chat-completeions API in addition to responses API for better support)
- streaming response to user - in progress (streaming of sub-agents, tools and skills remains if desired)

### TODO:
- circular import (task_delegation and sub_agent nodes) resolution once and for all
- git integration in agentic workflow
- safety guards on shell tool
- streaming should include tool calls and subagent flows
- skills' separate tools - integrations setup instead of agentic_tools and agentic_skills
- proper context setup (like claude.md or something)
- edit file tool to perform changes in specific parts in file
- langsmith -> langfuse
- context limit auto updation based on model instead of env setting