import http.server
import json
import urllib.request
import sys

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override to log to stdout for debugging
        sys.stdout.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

    def do_POST(self):
        if self.path.startswith('/v1/messages'):
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                anthropic_req = json.loads(post_data)
                
                # Extract messages and map roles if necessary
                messages = []
                for m in anthropic_req.get("messages", []):
                    role = m.get("role", "user")
                    content = m.get("content", "")
                    # If content is a list (Claude style), join it
                    if isinstance(content, list):
                        content = " ".join([c.get("text", "") for c in content if c.get("type") == "text"])
                    messages.append({"role": role, "content": content})

                # Map Anthropic to OpenAI/Ollama format
                openai_req = {
                    "model": "gemma4:latest",
                    "messages": messages,
                    "stream": False, # Keep it simple for ping test
                    "max_tokens": anthropic_req.get("max_tokens", 1024)
                }
                
                # Forward to Ollama's OpenAI-compatible endpoint
                req = urllib.request.Request(
                    "http://localhost:11434/v1/chat/completions",
                    data=json.dumps(openai_req).encode(),
                    headers={"Content-Type": "application/json"}
                )
                
                with urllib.request.urlopen(req) as response:
                    res_data = response.read()
                    ollama_res = json.loads(res_data)
                    
                    # Map OpenAI/Ollama response back to Anthropic
                    # Ollama/OpenAI: choices[0].message.content
                    content_text = ollama_res["choices"][0]["message"]["content"]
                    
                    anthropic_res = {
                        "id": "msg_" + ollama_res.get("id", "0"),
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "text", "text": content_text}],
                        "model": "gemma4",
                        "stop_reason": "end_turn",
                        "stop_sequence": None,
                        "usage": {
                            "input_tokens": ollama_res.get("usage", {}).get("prompt_tokens", 0),
                            "output_tokens": ollama_res.get("usage", {}).get("completion_tokens", 0)
                        }
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(anthropic_res).encode())

            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    port = 4000
    print(f"Starting Anthropic->Ollama bridge on port {port}...")
    http.server.HTTPServer(('localhost', port), ProxyHandler).serve_forever()
