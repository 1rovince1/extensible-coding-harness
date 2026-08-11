# # # from openai import OpenAI
# # # import os
# # # import sys

# # # _USE_COLOR = sys.stdout.isatty() and os.getenv("NO_COLOR") is None
# # # _REASONING_COLOR = "\033[90m" if _USE_COLOR else ""
# # # _RESET_COLOR = "\033[0m" if _USE_COLOR else ""

# # # client = OpenAI(
# # #   base_url = "https://integrate.api.nvidia.com/v1",
# # #   api_key = "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"
# # # )


# # # completion = client.chat.completions.create(
# # #   model="z-ai/glm-5.2",
# # #   messages=[{"role":"user","content":"hi"}],
# # #   temperature=1,
# # #   top_p=1,
# # #   max_tokens=16384,
# # #   seed=42,
# # #   reasoning_effort="minimal",
# # #   stream=True
# # # )

# # # for chunk in completion:
# # #   if not getattr(chunk, "choices", None):
# # #     continue
# # #   if len(chunk.choices) == 0 or getattr(chunk.choices[0], "delta", None) is None:
# # #     continue
# # #   delta = chunk.choices[0].delta
# # #   if getattr(delta, "content", None) is not None:
# # #     print(delta.content, end="")



# # import requests

# # invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
# # stream = True

# # headers = {
# #     "Authorization": "Bearer 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",
# #     "Accept": "text/event-stream" if stream else "application/json",
# # }

# # payload = {
# # #   "prompt": "",
# #   "messages": [
# #     {
# #       "role": "user",
# #       "content": ""
# #     }
# #   ],
# #   "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
# #   "max_tokens": 65536,
# #   "reasoning_budget": 16384,
# #   "stream": stream,
# #   "temperature": 0.6,
# #   "top_p": 0.95
# # }

# # response = requests.post(invoke_url, headers=headers, json=payload, stream=stream)
# # if stream:
# #     for line in response.iter_lines():
# #         if line:
# #             print(line.decode("utf-8"))
# # else:
# #     print(response.json())



import requests

url = "https://integrate.api.nvidia.com/v1/chat/completions"

payload = {
    "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "temperature": 1,
    "top_p": 0.9,
    "max_tokens": 16384,
    "seed": None,
    "stream": False,
    "tools": [
        {
            "type": "function",
            "function": {
                "parameters": { "command": "the command to execute" },
                "description": "A bash command line tool with limited commands",
                "name": "execute_shell_command"
            }
        }
    ],
    "messages": [
        {
            "role": "system",
            "content": "sfgsg"
        },
        {
            "role": "user",
            "content": "call toool to print 4 words"
        }
    ]
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer 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"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)