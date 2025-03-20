#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import requests
from modelcontextprotocol.server import Server, StdioServerTransport
from modelcontextprotocol.sdk.types import (
    CallToolRequestSchema,
    ListToolsRequestSchema,
    McpError,
    ErrorCode
)

load_dotenv()

class WeatherServer:
    def __init__(self):
        self.server = Server(
            {"name": "china-weather-server", "version": "1.0.0"},
            capabilities={
                "tools": {
                    "get_weather": {
                        "description": "获取中国城市天气预报",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "city": {
                                    "type": "string",
                                    "description": "城市名称（中文）"
                                }
                            },
                            "required": ["city"]
                        }
                    }
                }
            }
        )
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = "https://api.seniverse.com/v3/weather/now.json"
        
        self.setup_handlers()
        self.setup_error_handling()

    def setup_handlers(self):
        self.server.set_request_handler(ListToolsRequestSchema, self.list_tools)
        self.server.set_request_handler(CallToolRequestSchema, self.handle_tool_call)

    def setup_error_handling(self):
        self.server.onerror = lambda error: print(f"Server Error: {error}")

    def list_tools(self, request):
        return {
            "tools": [{
                "name": "get_weather",
                "description": "获取中国城市实时天气",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    },
                    "required": ["city"]
                }
            }]
        }

    def handle_tool_call(self, request):
        if request.params.name == "get_weather":
            return self.get_weather(request.params.arguments)
        raise McpError(ErrorCode.MethodNotFound, "Unknown tool")

    def get_weather(self, args):
        city = args.get("city")
        if not city:
            raise McpError(ErrorCode.InvalidParams, "City parameter required")

        params = {
            "key": self.api_key,
            "location": city,
            "language": "zh-Hans",
            "unit": "c"
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return {
                "content": [{
                    "type": "text",
                    "text": f"当前天气：{data['results'][0]['now']['text']}\n温度：{data['results'][0]['now']['temperature']}℃\n湿度：{data['results'][0]['now']['humidity']}%"
                }]
            }
        except Exception as e:
            raise McpError(ErrorCode.InternalError, f"Weather API error: {str(e)}")

    def run(self):
        transport = StdioServerTransport()
        self.server.connect(transport)
        print("天气服务已启动")

if __name__ == "__main__":
    server = WeatherServer()
    server.run()
