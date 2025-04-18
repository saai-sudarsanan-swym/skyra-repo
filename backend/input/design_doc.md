## **Design Document: Intelligent Search AI \- Shopify App**

**Project:** Intelligent Search AI \- Shopify App

**Version:** 1.0

**Date:** April 18, 2025

**Prepared By:** Awesome Senior Engineering Manager

### **1\. System Architecture**

We will adopt a microservice architecture to ensure scalability, maintainability, and independent deployability of different functionalities. The core services are:

* **Shopify Data Sync Service:** Responsible for maintaining a consistent and up-to-date representation of the Shopify store's product catalog within our system.  
* **Search Backend Service:** The main service that handles user search queries, interacts with the LLM, and orchestrates the product matching process.  
* **Product Catalog Service (ML Model Hosting):** Hosts the machine learning model responsible for cataloging product data and matching LLM-generated product lists to the store's inventory.  
* **Frontend Service (Shopify Storefront Injection):** Contains the frontend code that will be injected into the Shopify storefront to provide the smart search bar UI.

Code snippet

```
graph LR
    A[Shopify Store] --> B(Shopify Data Sync Service);
    B -- Webhooks (Create/Update/Delete) --> C(Our Product Database);
    D(Shopify Storefront) --> E[Frontend Service (Injected)];
    E -- User Query --> F(Search Backend Service);
    F -- LLM Prompt --> G(LLM Provider);
    G -- Product List --> F;
    F --> H(Product Catalog Service);
    H -- Product Data & LLM List --> I(Matched Product IDs);
    I --> F;
    F --> E -- Search Results --> D;
```

**1.1. Technology Stack (Tentative):**

* **Shopify Data Sync Service:** Python (with a framework like Flask or Django), PostgreSQL.  
* **Search Backend Service:** Python (with a framework like FastAPI or Flask), Redis (for caching).  
* **Product Catalog Service:** Python, PyTorch/TensorFlow (depending on the ML model), potentially a vector database like ChromaDB or FAISS for efficient similarity search.  
* **Frontend Service:** React or Vue.js, JavaScript/TypeScript.  
* **Message Queue (for asynchronous communication):** Kafka or RabbitMQ.  
* **Containerization:** Docker.  
* **Orchestration:** Kubernetes (or Docker Compose for initial development).  
* **Cloud Provider:** AWS, GCP, or Azure (to be decided based on cost and existing infrastructure).

### **2\. Service Design Details**

**2.1. Shopify Data Sync Service:**

* **Responsibilities:**  
  * Registering and managing Shopify webhooks for `products/create`, `products/update`, and `products/delete` events for each installed Shopify store.  
  * Receiving and processing webhook payloads from Shopify.  
  * Maintaining a normalized and structured representation of the Shopify product catalog in our persistent storage (PostgreSQL). This will include relevant attributes like title, description, tags, variants, images, vendor, product type, etc.  
  * Handling initial sync of the entire product catalog upon app installation using the Shopify Admin API.  
  * Implementing robust error handling and retry mechanisms for webhook processing failures.  
  * Providing an API endpoint for other services to query the latest product data.  
* **Data Model (Conceptual):**

```
products_table:
    - store_id (INT, FK to stores_table)
    - product_id (BIGINT, Unique within store)
    - title (TEXT)
    - description (TEXT)
    - product_type (TEXT)
    - vendor (TEXT)
    - tags (ARRAY of TEXT)
    - variants (JSONB)
    - images (JSONB)
    - created_at (TIMESTAMP)
    - updated_at (TIMESTAMP)
    - ... (other relevant attributes)

stores_table:
    - id (SERIAL, PRIMARY KEY)
    - shopify_domain (VARCHAR, UNIQUE)
    - access_token (VARCHAR)
    - ... (other store-specific configurations)
```

* 

* **Webhooks:** We will register for the following Shopify webhook topics:  
  * `products/create`  
  * `products/update`  
  * `products/delete`

**2.2. Search Backend Service:**

* **Responsibilities:**  
  * Receiving user search queries from the Frontend Service.  
  * Authenticating and authorizing requests.  
  * Formulating prompts for the LLM based on the user's natural language query.  
  * Interacting with the chosen LLM provider via their API.  
  * Receiving the list of potential product keywords or concepts from the LLM.  
  * Orchestrating the call to the Product Catalog Service to match these keywords/concepts with actual products in the store.  
  * Applying basic filtering and ranking of the matched product results.  
  * Returning the relevant product IDs and potentially some basic product information to the Frontend Service.  
  * Implementing caching mechanisms (Redis) for frequently used queries or LLM responses to improve performance.  
  * Publishing search query and result information to the message queue for analytics and learning purposes.  
* **API Endpoints:**  
  * `/search` (POST): Accepts a user query and returns a list of matching product IDs and basic information.

**2.3. Product Catalog Service (ML Model Hosting):**

* **Responsibilities:**  
  * Hosting and serving the machine learning model responsible for understanding and cataloging the product data.  
  * Providing an API endpoint to receive a list of product keywords/concepts from the Search Backend Service and the `store_id`.  
  * Querying the local product database (maintained by the Shopify Data Sync Service) for the product data of the specified store.  
  * Using the ML model to map the LLM-generated keywords/concepts to the products present in the store. This might involve techniques like:  
    * **Text Embeddings:** Generating vector embeddings for product titles, descriptions, and the LLM output, then performing similarity search (e.g., using a vector database).  
    * **Keyword Matching with Semantic Expansion:** Combining traditional keyword matching with the LLM's understanding of synonyms and related terms.  
  * Returning a ranked list of matching product IDs to the Search Backend Service.  
* **ML Model Training (Out of Scope for this initial design, but important for future iterations):** This would involve training a model on a large dataset of product descriptions and natural language queries to understand the semantic relationships between them.  
* **API Endpoints:**  
  * `/match_products` (POST): Accepts a list of keywords/concepts and a `store_id`, returns a ranked list of matching product IDs.

**2.4. Frontend Service (Shopify Storefront Injection):**

* **Responsibilities:**  
  * Providing the UI elements for the smart search bar that will be injected into the Shopify storefront (e.g., using Shopify ScriptTags or a Shopify App Block).  
  * Capturing user input from the search bar.  
  * Making asynchronous calls to the Search Backend Service with the user's query.  
  * Receiving the search results (product IDs and basic information) from the Search Backend Service.  
  * Rendering the search results to the user within the storefront, ideally with features like autocomplete suggestions and a dedicated search results page.  
  * Tracking user interactions with the search bar (e.g., queries, clicks) and potentially sending this data (anonymized) back to our backend for analytics.  
* **Integration with Shopify Theme:** The frontend code needs to be designed to be compatible with various Shopify themes and potentially offer customization options.  
* **Security Considerations:** Ensure that the injected frontend code is secure and does not introduce any vulnerabilities to the Shopify storefront. Avoid exposing sensitive data directly in the frontend.

### **3\. Sample Flow (User Search)**

1. A customer on a Shopify store with our app installed enters a natural language query into the smart search bar (provided by the Frontend Service).  
2. The Frontend Service sends this query to the **Search Backend Service** via an authenticated API request.  
3. The Search Backend Service receives the query.  
4. The Search Backend Service formulates a prompt based on the user's query and sends it to the **LLM Provider**.  
5. The LLM Provider processes the prompt and returns a list of potential product keywords, concepts, or categories.  
6. The Search Backend Service takes this list and the `store_id` of the Shopify store and sends it to the **Product Catalog Service** via an authenticated API request.  
7. The Product Catalog Service queries its local product database for the product data of the specified store.  
8. The Product Catalog Service uses its ML model to match the LLM-generated keywords/concepts with the products in the store's catalog.  
9. The Product Catalog Service returns a ranked list of matching product IDs to the **Search Backend Service**.  
10. The Search Backend Service might perform some basic ranking or filtering on these results.  
11. The Search Backend Service sends the list of relevant product IDs (and potentially some basic product information like title and image URL fetched from its cache or by querying the Shopify Data Sync Service) back to the **Frontend Service**.  
12. The Frontend Service receives the results and renders them to the customer in the Shopify storefront.

Code snippet

```
sequenceDiagram
    actor Customer
    participant Frontend as Frontend Service (Injected)
    participant SearchBackend as Search Backend Service
    participant LLM
    participant ProductCatalog as Product Catalog Service
    participant ProductDB as Product Database (Our System)

    Customer->>Frontend: Enters natural language query
    Frontend->>SearchBackend: Sends user query
    SearchBackend->>LLM: Formulates and sends LLM prompt
    LLM-->>SearchBackend: Returns list of product keywords/concepts
    SearchBackend->>ProductCatalog: Sends keywords/concepts and store_id
    ProductCatalog->>ProductDB: Queries product data for the store
    ProductDB-->>ProductCatalog: Returns product data
    ProductCatalog->>ProductCatalog: Matches keywords/concepts using ML model
    ProductCatalog-->>SearchBackend: Returns ranked list of product IDs
    SearchBackend->>Frontend: Sends search results (product IDs, basic info)
    Frontend->>Customer: Renders search results
```

### **4\. Security Considerations**

* **Authentication and Authorization:**  
  * **Frontend to Backend:** The Frontend Service will need a secure way to authenticate requests to the Search Backend Service. This could involve API keys managed per Shopify store during app installation.  
  * **Backend Services:** Internal communication between microservices (Search Backend to Product Catalog Service, Search Backend to Shopify Data Sync Service) should be secured using mutual TLS (mTLS) or JWT (JSON Web Tokens).  
  * **Access Control:** Implement proper authorization mechanisms to ensure each service only has access to the resources it needs.  
* **Shopify API Security:**  
  * Store the Shopify access token securely (e.g., using encryption at rest).  
  * Follow Shopify's best practices for API usage and rate limiting.  
* **LLM API Security:**  
  * Use secure API keys and follow the LLM provider's security guidelines.  
  * Sanitize user input before sending it to the LLM to prevent potential injection attacks.  
* **Data Security:**  
  * Encrypt sensitive data at rest and in transit.  
  * Follow data privacy regulations (e.g., GDPR, CCPA) regarding the collection and storage of user data (even if anonymized).  
* **Webhook Security:**  
  * Verify the authenticity of Shopify webhook requests using the `X-Shopify-Hmac-Sha256` header.  
* **Rate Limiting:** Implement rate limiting on all external and internal API endpoints to prevent abuse and ensure service stability.  
* **Regular Security Audits:** Conduct regular security audits and vulnerability scanning of our infrastructure and code.

### **5\. Observability, Logging, and Monitoring**

A robust observability strategy is crucial for understanding system behavior, debugging issues, and ensuring performance.

* **Logging:**  
  * **Structured Logging:** Implement structured logging (e.g., using JSON format) across all services to make logs easily searchable and analyzable. Include relevant context such as timestamp, service name, request ID, user ID (if applicable), and log level.  
  * **Centralized Logging:** Aggregate logs from all microservices into a centralized logging system (e.g., ELK stack \- Elasticsearch, Logstash, Kibana or Grafana Loki with Promtail).  
  * **Correlation IDs:** Use correlation IDs to track requests across multiple services, making it easier to trace the flow of a user interaction.  
* **Monitoring:**  
  * **Metrics Collection:** Collect key performance indicators (KPIs) for each service, such as:  
    * Request latency  
    * Error rates  
    * CPU and memory utilization  
    * Network traffic  
    * Queue lengths (for message queues)  
    * Database performance metrics  
    * LLM API response times and error rates  
  * **Monitoring Tools:** Utilize monitoring tools like Prometheus and Grafana or cloud-specific monitoring services (e.g., AWS CloudWatch, GCP Cloud Monitoring, Azure Monitor) to visualize these metrics and set up alerts.  
  * **Health Checks:** Implement health check endpoints for each service that can be used by the orchestration platform (Kubernetes) to monitor service availability and perform automatic restarts if necessary.  
  * **Alerting:** Configure meaningful alerts based on critical metrics to notify the team of potential issues proactively.  
* **Tracing:**  
  * Implement distributed tracing (e.g., using Jaeger or Zipkin) to visualize the path of requests across different microservices and identify performance bottlenecks.  
* **Application Performance Monitoring (APM):** Consider using APM tools (e.g., Datadog, New Relic) for deeper insights into application performance, including code-level tracing and profiling.

### **6\. System Design Considerations**

* **Scalability:** The microservice architecture inherently supports horizontal scaling. Each service can be scaled independently based on its resource demands. Use Kubernetes for automated scaling and orchestration.  
* **Fault Tolerance:** Design services to be resilient to failures. Implement retry mechanisms, circuit breakers, and graceful degradation strategies. Use message queues for asynchronous communication to buffer against temporary service outages.  
* **Idempotency:** Ensure that webhook processing and other critical operations are idempotent to prevent unintended side effects from duplicate requests.  
* **Configuration Management:** Use a centralized configuration management system (e.g., HashiCorp Consul, Spring Cloud Config) to manage application configurations across all services.  
* **Deployment:** Implement a robust CI/CD pipeline for automated building, testing, and deployment of microservices (e.g., using Jenkins, GitLab CI/CD, or GitHub Actions).  
* **Database Considerations:**  
  * **Shopify Product Data:** PostgreSQL is a good choice for storing the structured product data.  
  * **Caching:** Redis will be used for caching frequently accessed data and LLM responses.  
  * **Vector Database (Potential):** For efficient similarity search in the Product Catalog Service, consider a dedicated vector database like ChromaDB or FAISS.  
* **Message Queue:** Using a message queue like Kafka or RabbitMQ for asynchronous communication (e.g., between the Search Backend and an Analytics/Learning service \- not detailed in this initial design but a future consideration) will improve decoupling and resilience.

This detailed design document provides the engineering team with a solid foundation for building the "Intelligent Search AI" Shopify app. We will iterate on this design as needed during the development process. Let's discuss any questions and begin planning the implementation.