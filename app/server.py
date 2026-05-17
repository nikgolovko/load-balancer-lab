import os
import time
import threading
from concurrent import futures

from flask import Flask, Response, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

import grpc
import echo_pb2
import echo_pb2_grpc

INSTANCE = os.environ.get("INSTANCE_NAME", "unknown")
HTTP_PORT = int(os.environ.get("HTTP_PORT", "8080"))
GRPC_PORT = int(os.environ.get("GRPC_PORT", "50051"))

app = Flask(__name__)

http_requests = Counter(
    "app_http_requests_total",
    "Total HTTP requests handled by backend instance",
    ["instance", "path"]
)

ws_messages = Counter(
    "app_websocket_messages_total",
    "Total WebSocket messages handled by backend instance",
    ["instance"]
)

grpc_requests = Counter(
    "app_grpc_requests_total",
    "Total gRPC requests handled by backend instance",
    ["instance", "method"]
)

request_latency = Histogram(
    "app_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["instance", "path"]
)


@app.route("/")
def index():
    with request_latency.labels(INSTANCE, "/").time():
        http_requests.labels(INSTANCE, "/").inc()
        return f"HTTP response from {INSTANCE}\n"


@app.route("/slow")
def slow():
    delay = float(request.args.get("delay", "2"))
    with request_latency.labels(INSTANCE, "/slow").time():
        http_requests.labels(INSTANCE, "/slow").inc()
        time.sleep(delay)
        return f"Slow HTTP response from {INSTANCE} after {delay} seconds\n"


@app.route("/health")
def health():
    return "OK\n"


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/ws")
def websocket_echo():
    ws = request.environ.get("wsgi.websocket")
    if not ws:
        return "Expected WebSocket request\n", 400

    ws.send(f"Connected to {INSTANCE}")

    while True:
        message = ws.receive()
        if message is None:
            break
        ws_messages.labels(INSTANCE).inc()
        ws.send(f"{INSTANCE} received: {message}")

    return ""


class EchoService(echo_pb2_grpc.EchoServiceServicer):
    def SayHello(self, request, context):
        grpc_requests.labels(INSTANCE, "SayHello").inc()
        return echo_pb2.EchoReply(
            message=f"Hello {request.name} from {INSTANCE}",
            instance=INSTANCE
        )


def start_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    echo_pb2_grpc.add_EchoServiceServicer_to_server(EchoService(), server)
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    server.start()
    print(f"gRPC server for {INSTANCE} listening on {GRPC_PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    threading.Thread(target=start_grpc_server, daemon=True).start()
    print(f"HTTP/WebSocket server for {INSTANCE} listening on {HTTP_PORT}")
    http_server = WSGIServer(("0.0.0.0", HTTP_PORT), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
