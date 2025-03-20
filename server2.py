from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import FastMCP
from mcp import McpError
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import os

# 加载环境变量
load_dotenv()

# 设置代理环境变量
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

# 初始化FastMCP服务器
mcp = FastMCP("weather")

@mcp.tool(
    name="get_weather",
    description="获取中国城市天气预报"
)
async def get_weather(args: dict):
    """天气查询工具实现"""
    city = args.get("city")
    api_key = os.getenv("WEATHER_API_KEY")
    base_url = "https://api.seniverse.com/v3/weather/now.json"
    
    if not city:
        raise McpError("必须提供城市名称")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                base_url,
                params={
                    "key": api_key,
                    "location": city,
                    "language": "zh-Hans",
                    "unit": "c"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            weather_info = data["results"][0]["now"]
            return {
                "text": f"{city}当前天气：{weather_info['text']}",
                "temperature": f"{weather_info['temperature']}℃",
                "humidity": f"{weather_info['humidity']}%",
                "update_time": data["results"][0]["last_update"]
            }
        except httpx.HTTPError as e:
            raise McpError(f"天气API请求失败: {str(e)}")


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
