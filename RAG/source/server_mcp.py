# {
#   "mcpServers": {
#     "math-demo": {
#       "url": "http://127.0.0.1:9000/mcp"
#     }
#   }
# }
from fastmcp import FastMCP
from utils.math_base import add, subtract, multiply, divide

mcp = FastMCP("演示 🚀")

@mcp.tool
def mcp_add(a: int, b: int) -> int:
    """两数相加"""
    return add(a, b)


@mcp.tool
def mcp_subtract(a: int, b: int) -> int:
    """两数相减"""
    return subtract(a, b)


@mcp.tool
def mcp_multiply(a: int, b: int) -> int:
    """两数相乘"""
    return multiply(a, b)


@mcp.tool
def mcp_divide(a: int, b: int) -> int:
    """两数相除"""
    return divide(a, b)



if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=9000)
