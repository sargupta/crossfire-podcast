"""
Test client for ADK WebSocket streaming endpoint
"""

import asyncio
import websockets
import json

async def test_adk_stream():
    uri = "ws://localhost:8000/api/debate/stream-adk"
    
    print("Connecting to ADK debate stream...")
    
    async with websockets.connect(uri) as websocket:
        # Send debate request
        request = {
            "topic": "Should AI Replace Human Jobs?",
            "turns": 6
        }
        
        await websocket.send(json.dumps(request))
        print(f"Sent request: {request['topic']}")
        print("="*70)
        
        # Receive streaming events
        while True:
            try:
                message = await websocket.recv()
                event = json.loads(message)
                
                if event["type"] == "complete":
                    print("\n" + "="*70)
                    print("✅ Debate Complete!")
                    break
                
                if event["type"] == "error":
                    print(f"\n❌ Error: {event['message']}")
                    break
                
                # Display event
                print(f"\n[{event['type'].upper()}] Turn {event['turn']} - {event.get('agent_name', 'N/A')}")
                print(f"{event.get('text', '')}")
                print("-"*70)
                
            except websockets.ConnectionClosed:
                print("\nConnection closed")
                break

if __name__ == "__main__":
    print("ADK Stream Test Client")
    print("="*70)
    asyncio.run(test_adk_stream())
