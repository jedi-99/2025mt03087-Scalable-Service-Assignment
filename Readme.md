## 1. Project Overview
This project implements and deploys a lightweight, scalable microservices-based application representing an **E-Commerce Store**. The system is decomposed into two decoupled, independently deployable services:
- **Product Service:** Manages catalog items, prices, and inventory levels.
- **Order Service:** Handles order placement, calculates transaction totals, and validates product availability synchronously via REST API calls against the Product Service.
Both services are containerized using **Docker** and deployed onto a local **Kubernetes (Minikube)** cluster with service discovery, isolated datastores, and declarative deployment configurations.

## 2. Architecture & Design

### 2.1 System Architecture
                         +-----------------------------+
                         |      Postman / Client       |
                         +-----------------------------+
                                        |
               HTTP POST /orders        |  HTTP GET /products
               (Port-Forward: 5002)     |  (Port-Forward: 5001)
                                        v
  +--------------------------------------------------------------------------+
  | Kubernetes Cluster (Minikube)                                            |
  |                                                                          |
  |  +------------------------+             +-----------------------------+  |
  |  |     Order Service      |  HTTP GET   |       Product Service       |  |
  |  |  (Deployment & Pods)   | ----------> |    (Deployment & Pods)      |  |
  |  +------------------------+             +-----------------------------+  |
  |              ^                                         ^                 |
  |              |                                         |                 |
  |    [ svc/order-service ]                     [ svc/product-service ]     |
  +--------------------------------------------------------------------------+

### 2.2 System Operations (Commands & Queries)
- **Product Service:**
  - `GET /products` (*Query*): List all catalog items and available stock.
  - `GET /products/<id>` (*Query*): Retrieve details and inventory for a specific product ID.
  - `POST /products` (*Command*): Create a new product entry in the catalog.
- **Order Service:**
  - `POST /orders` (*Command*): Validates product inventory via internal HTTP request to `http://product-service:5001/products/<id>` and registers a new order.
  - `GET /orders/<id>` (*Query*): Fetch order details and order fulfillment status.

## 3. Repository Structure
Each microservice is maintained in an independent codebase:

├── product-service/
│   ├── app.py                  # Product service business logic & SQLite layer
│   ├── requirements.txt        # Python dependencies (Flask, requests)
│   ├── Dockerfile              # Container image definition
│   └── k8s-deployment.yaml     # Kubernetes Deployment & ClusterIP Service
│
└── order-service/
    ├── app.py                  # Order service business logic & REST client
    ├── requirements.txt        # Python dependencies (Flask, requests)
    ├── Dockerfile              # Container image definition
    └── k8s-deployment.yaml     # Kubernetes Deployment & NodePort Service

## 4. Prerequisites & Setup
Following tools are installed and utilised on the system:
- **Docker Desktop**
- **Minikube**
- **kubectl**
- **Python** (v3.10+)
- **Postman**

## 5. Build and Deployment Instructions
### Step 1: Start Minikube
Initialize local Kubernetes cluster: **minikube start --driver=docker**

### Step 2: Build Docker Images
Navigate to each service directory and build the respective container images:

# Build Product Service Image
**cd product-service**
**docker build -t product-service:v1 .**

# Build Order Service Image
**cd ../order-service**
**docker build -t order-service:v1 .**

### Step 3: Deploy to Kubernetes
Apply the deployment and service manifests to Minikube:
**kubectl apply -f product-service/k8s-deployment.yaml**
**kubectl apply -f order-service/k8s-deployment.yaml**

### Step 4: Verify Deployment Status
Ensure pods are in the `Running` state and services have been assigned cluster ports:

**kubectl get deployments**
**kubectl get pods -o wide**
**kubectl get svc**

## 5. Accessing the Application & API Testing

### 5.1 Expose Services Locally
In two separate terminal, expose the cluster services via port-forwarding:

**Terminal 1 (Product Service):**
kubectl port-forward svc/product-service 5001:5001

**Terminal 2 (Order Service):**
kubectl port-forward svc/order-service 5002:5002

### 5.2 Sample API Requests & Responses

#### 1. Fetch All Products
- **Endpoint:** `GET http://localhost:5001/products`

#### 2. Create an Order (Success Case)
- **Endpoint:** `POST http://localhost:5002/orders`
- **Headers:** `Content-Type: application/json`
- **Body:**
  json
  {
    "product_id": 1,
    "quantity": 2
  }

#### 3. Create an Order (Invalid Product ID)
- **Endpoint:** `POST http://localhost:5002/orders`
- **Headers:** `Content-Type: application/json`
- **Body:**
  json
  {
    "product_id": 999,
    "quantity": 1
  }

## 7. Kubernetes Dashboard Analysis

To inspect cluster health, resource utilization, and pod status in a browser: **minikube dashboard**

- Navigate to **Workloads > Deployments** to verify `product-service-deployment` and `order-service-deployment`.