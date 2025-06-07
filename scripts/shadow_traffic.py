# Shadow traffic mirroring for unbiased evaluation
import asyncio
import aiohttp
import json
import random
import time
import argparse
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass 
class TrafficRequest:
    endpoint: str
    method: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: float

class ShadowTrafficMirror:
    def __init__(self, shadow_endpoint: str, mirror_percentage: float = 0.1):
        self.shadow_endpoint = shadow_endpoint
        self.mirror_percentage = mirror_percentage
        self.results = []
    
    async def mirror_traffic(self, requests: List[TrafficRequest], duration: int) -> List[Dict[str, Any]]:
        """Mirror production traffic to shadow environment"""
        
        start_time = time.time()
        mirrored_count = 0
        
        async with aiohttp.ClientSession() as session:
            # NOVEL: Intelligent traffic sampling with load balancing
            for request in requests:
                if time.time() - start_time > duration:
                    break
                
                if random.random() < self.mirror_percentage:
                    result = await self._mirror_single_request(session, request)
                    self.results.append(result)
                    mirrored_count += 1
                    
                    # Rate limiting to prevent overwhelming shadow environment
                    await asyncio.sleep(0.1)
        
        return self.results
    
    async def _mirror_single_request(self, session: aiohttp.ClientSession, request: TrafficRequest) -> Dict[str, Any]:
        """Mirror a single request to shadow environment"""
        
        start_time = time.time()
        
        try:
            # NOVEL: Shadow request with comprehensive metrics collection
            shadow_url = f"{self.shadow_endpoint}{request.endpoint}"
            
            async with session.request(
                method=request.method,
                url=shadow_url,
                json=request.payload,
                headers={**request.headers, "X-Shadow-Request": "true"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_time = time.time() - start_time
                response_text = await response.text()
                
                return {
                    "request_id": f"shadow_{int(time.time()*1000)}",
                    "original_request": {
                        "endpoint": request.endpoint,
                        "method": request.method,
                        "payload_size": len(json.dumps(request.payload))
                    },
                    "shadow_response": {
                        "status_code": response.status,
                        "response_time": response_time,
                        "response_size": len(response_text),
                        "content_preview": response_text[:200] if response_text else ""
                    },
                    "metrics": {
                        "success": response.status < 400,
                        "latency_ms": response_time * 1000,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            return {
                "request_id": f"shadow_error_{int(time.time()*1000)}",
                "error": str(e),
                "metrics": {
                    "success": False,
                    "latency_ms": (time.time() - start_time) * 1000,
                    "timestamp": datetime.now().isoformat()
                }
            }

def load_traffic_samples(file_path: str) -> List[TrafficRequest]:
    """Load traffic samples from JSON file"""
    
    # Mock traffic data for demo
    mock_requests = [
        TrafficRequest(
            endpoint="/chat-tot",
            method="POST",
            payload={"message": "How do I fix this bug?", "context": {}},
            headers={"Content-Type": "application/json"},
            timestamp=time.time()
        ),
        TrafficRequest(
            endpoint="/explain",
            method="POST", 
            payload={"query": "Explain this code", "include_reasoning": True},
            headers={"Content-Type": "application/json"},
            timestamp=time.time()
        )
    ]
    
    return mock_requests * 50  # Simulate 100 requests

async def main():
    parser = argparse.ArgumentParser(description="Shadow traffic mirroring")
    parser.add_argument("--source-logs", required=True, help="Source traffic logs")
    parser.add_argument("--mirror-percentage", type=float, default=0.1, help="Percentage to mirror")
    parser.add_argument("--shadow-endpoint", required=True, help="Shadow endpoint URL")
    parser.add_argument("--duration", type=int, default=3600, help="Duration in seconds")
    parser.add_argument("--output", required=True, help="Output file")
    
    args = parser.parse_args()
    
    # Load traffic samples
    requests = load_traffic_samples(args.source_logs)
    
    # Initialize mirror
    mirror = ShadowTrafficMirror(
        shadow_endpoint=args.shadow_endpoint,
        mirror_percentage=args.mirror_percentage
    )
    
    # Mirror traffic
    print(f"Starting shadow traffic mirroring for {args.duration} seconds...")
    results = await mirror.mirror_traffic(requests, args.duration)
    
    # Save results
    output_data = {
        "mirror_config": {
            "mirror_percentage": args.mirror_percentage,
            "duration": args.duration,
            "shadow_endpoint": args.shadow_endpoint
        },
        "summary": {
            "total_requests": len(results),
            "successful_requests": sum(1 for r in results if r.get("metrics", {}).get("success", False)),
            "average_latency": sum(r.get("metrics", {}).get("latency_ms", 0) for r in results) / len(results) if results else 0
        },
        "results": results
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Shadow mirroring complete. {len(results)} requests processed.")
    print(f"Success rate: {output_data['summary']['successful_requests']/len(results)*100:.1f}%")
    print(f"Average latency: {output_data['summary']['average_latency']:.1f}ms")

if __name__ == "__main__":
    asyncio.run(main())
