from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from utils.math_base import add, subtract, multiply, divide
model = ChatOpenAI(
    model="qwen3-8b",
    api_key="sk-87c58597f63d4001949476d28bc9c553",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    streaming=True,
    temperature=0.7,
    extra_body={
        "enable_thinking": False,
    },
)
# output = model.invoke("1+1=?")
# print(output.content)
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model=model,
    tools=[get_weather,add,subtract,multiply,divide],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?我有三个工厂，每个工厂6个人，一共多少人？"}]}
)
print(result)
print(result["messages"][-1].content_blocks)