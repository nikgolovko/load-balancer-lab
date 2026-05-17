# Load-Balancer Lab

This hands-on lab explores how load balancing behaves across HTTP, WebSocket, gRPC, and raw TCP traffic. Participants build a local Docker-based environment with multiple backend services, NGINX and HAProxy load balancers, Prometheus, Grafana, and a dedicated toolbox container for running experiments. Through practical exercises, they compare Layer 4 and Layer 7 balancing, observe round robin, weighted, least-connections, and sticky-session strategies, analyze the effects of long-lived connections, and validate system behavior with metrics. The lab connects protocol mechanics with architectural concerns such as scalability, availability, failure handling, and observability.

[Here is a guidance](./load-balancer-lab-guide.adoc)
