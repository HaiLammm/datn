# Monitoring and Observability

## Monitoring Stack

Our monitoring strategy uses a combination of platform-provided tools and dedicated services to get a complete picture of the application's health.

-   **Frontend Monitoring:** **Vercel Analytics**
    -   Provides real-time Core Web Vitals (LCP, FID, CLS) and page view metrics out-of-the-box. This gives us immediate insight into the real-world performance experienced by our users.

-   **Backend Monitoring:** **Prometheus + Grafana**
    -   **Prometheus** will be used to scrape and store time-series metrics from our self-hosted backend. A FastAPI Prometheus exporter will expose application metrics (like request latency and error rates).
    -   **Grafana** will be used to create dashboards to visualize the metrics collected by Prometheus, providing a real-time view of backend health.

-   **Error Tracking:** **Sentry**
    -   Sentry will be integrated into both the frontend and backend to capture, aggregate, and alert on exceptions in real-time. This provides much richer context than plain logs, including stack traces and user session data.

-   **Performance Monitoring:**
    -   Frontend performance is covered by Vercel Analytics.
    -   Backend API performance (latency, throughput) will be monitored via Prometheus and Grafana.

## Key Metrics

We will focus on the following key metrics to measure the health and performance of our application.

### Frontend Metrics

-   **Core Web Vitals:** LCP (Largest Contentful Paint), FID (First Input Delay), CLS (Cumulative Layout Shift).
-   **JavaScript Error Rate:** Percentage of user sessions that encounter a JavaScript error (tracked by Sentry).
-   **API Latency (Client-side):** The time it takes for API requests to complete from the user's browser perspective.
-   **User Interactions:** Tracking key user flows (e.g., CV upload initiated, job search performed) to understand feature adoption.

### Backend Metrics

-   **Request Rate:** Requests per second/minute to the API.
-   **Error Rate:** Percentage of 4xx and 5xx HTTP status codes, particularly focusing on the 5xx server error rate.
-   **API Endpoint Latency:** 95th and 99th percentile response times for all major API endpoints.
-   **Database Performance:** Slow query rate, active connections, and cache hit ratio.
-   **AI Service Performance:**
    -   **Inference Latency:** p95 latency for both the `llama3.1:8b` (generation) and `nomic-embed-text` (embedding) models.
    -   **Resource Utilization:** GPU and RAM utilization of the server hosting the Ollama service (collected via `node_exporter` for Prometheus).

---