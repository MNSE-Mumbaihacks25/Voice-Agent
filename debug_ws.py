import sys
import websockets
print(f"Python: {sys.version}")
print(f"Websockets version: {websockets.version}")
print(f"Websockets file: {websockets.__file__}")
try:
    import websockets.asyncio
    print("websockets.asyncio imported successfully")
except ImportError as e:
    print(f"Failed to import websockets.asyncio: {e}")
