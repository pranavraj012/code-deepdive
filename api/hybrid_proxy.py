import httpx
import logging
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class HybridProxy:
    def __init__(self, local_url: Optional[str] = None):
        self.local_url = local_url.rstrip("/") if local_url else None

    async def check_health(self) -> bool:
        if not self.local_url:
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.local_url}/")
                return response.status_code == 200
        except Exception:
            return False

    async def proxy_post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        if not self.local_url:
            raise ValueError("LOCAL_RAG_URL not configured")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{self.local_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()

    async def proxy_websocket(self, client_ws: WebSocket, endpoint: str):
        if not self.local_url:
            await client_ws.send_text("Error: LOCAL_RAG_URL not configured")
            await client_ws.close()
            return

        import websockets
        import asyncio

        # convert http/https to ws/wss
        ws_url = self.local_url.replace("http://", "ws://").replace("https://", "wss://")
        target_url = f"{ws_url}{endpoint}"

        try:
            async with websockets.connect(target_url) as server_ws:
                # Forwarding tasks
                async def forward_to_local():
                    try:
                        while True:
                            message = await client_ws.receive_text()
                            await server_ws.send(message)
                    except WebSocketDisconnect:
                        await server_ws.close()
                    except Exception as e:
                        logger.error(f"Error forwarding to local: {e}")

                async def forward_to_client():
                    try:
                        async for message in server_ws:
                            await client_ws.send_text(message)
                    except Exception as e:
                        logger.error(f"Error forwarding to client: {e}")
                    finally:
                        await client_ws.close()

                await asyncio.gather(forward_to_local(), forward_to_client())
        except Exception as e:
            logger.error(f"WebSocket proxy error: {e}")
            await client_ws.send_text(f"Proxy error: {str(e)}")
            await client_ws.close()
