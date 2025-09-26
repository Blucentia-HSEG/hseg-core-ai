# Enterprise Deployment Guide

## Executive Summary

This guide provides comprehensive instructions for deploying the Blucentia Culture Intelligence Platform in enterprise environments. The deployment architecture supports high availability, scalability, security, and compliance requirements for organizations processing sensitive employee data under the HSEG framework.

### Deployment Options
- **Cloud-Native Kubernetes**: Recommended for scalability and resilience
- **Docker Compose**: Suitable for smaller deployments
- **Hybrid Cloud**: On-premises + cloud for regulatory compliance
- **Air-Gapped**: Completely isolated environments for maximum security

## Prerequisites

### Infrastructure Requirements
| Component | Minimum | Recommended | Enterprise |
|-----------|---------|-------------|------------|
| **Compute** | 2 vCPU, 8GB RAM | 4 vCPU, 16GB RAM | 8 vCPU, 32GB RAM |
| **Storage** | 100GB SSD | 500GB SSD | 1TB NVMe |
| **Network** | 1 Gbps | 10 Gbps | 25 Gbps |
| **Load Balancer** | Software | Hardware | Enterprise |

### Software Dependencies
- **Container Runtime**: Docker 20.10+ or containerd 1.5+
- **Orchestration**: Kubernetes 1.24+ (recommended) or Docker Compose 2.0+
- **Database**: PostgreSQL 14+ with encryption at rest
- **Cache**: Redis 7.0+ with clustering support
- **Load Balancer**: Nginx 1.20+ or enterprise equivalent
- **Monitoring**: Prometheus + Grafana stack

### Security Requirements
- **TLS Certificates**: Valid SSL/TLS certificates for all endpoints
- **Secret Management**: HashiCorp Vault or equivalent
- **Network Security**: VPC with proper firewall rules
- **Access Control**: RBAC-enabled with audit logging
- **Compliance**: GDPR, HIPAA, SOX compliance features enabled

## Kubernetes Deployment (Recommended)

### Cluster Architecture
```yaml
# cluster-architecture.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: culture-score
  labels:
    name: culture-score
    environment: production

---
# Resource Quotas
apiVersion: v1
kind: ResourceQuota
metadata:
  name: culture-score-quota
  namespace: culture-score
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 40Gi
    limits.cpu: "20"
    limits.memory: 80Gi
    persistentvolumeclaims: "10"
    services: "10"
```

### Application Deployment
```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: culture-score-api
  namespace: culture-score
  labels:
    app: culture-score-api
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: culture-score-api
  template:
    metadata:
      labels:
        app: culture-score-api
        version: v1.0.0
    spec:
      serviceAccountName: culture-score-api
      containers:
      - name: api
        image: culture-score/api:v1.0.0
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: culture-score-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: culture-score-secrets
              key: redis-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: culture-score-secrets
              key: jwt-secret
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1001
          capabilities:
            drop:
            - ALL
      imagePullSecrets:
      - name: culture-score-registry-secret

---
# Service Configuration
apiVersion: v1
kind: Service
metadata:
  name: culture-score-api-service
  namespace: culture-score
  labels:
    app: culture-score-api
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: http
    protocol: TCP
    name: http
  selector:
    app: culture-score-api

---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: culture-score-api-hpa
  namespace: culture-score
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: culture-score-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### Database Configuration
```yaml
# postgresql-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
  namespace: culture-score
spec:
  serviceName: postgresql-service
  replicas: 3  # Primary + 2 read replicas
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:14.8
        env:
        - name: POSTGRES_DB
          value: culture_score
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgresql-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgresql-secret
              key: password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        ports:
        - containerPort: 5432
          name: postgresql
        volumeMounts:
        - name: postgresql-storage
          mountPath: /var/lib/postgresql/data
        - name: postgresql-config
          mountPath: /etc/postgresql/postgresql.conf
          subPath: postgresql.conf
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 4000m
            memory: 8Gi
      volumes:
      - name: postgresql-config
        configMap:
          name: postgresql-config
  volumeClaimTemplates:
  - metadata:
      name: postgresql-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi

---
# PostgreSQL Configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgresql-config
  namespace: culture-score
data:
  postgresql.conf: |
    # Connection Settings
    listen_addresses = '*'
    port = 5432
    max_connections = 200

    # Memory Settings
    shared_buffers = 2GB
    effective_cache_size = 6GB
    work_mem = 64MB
    maintenance_work_mem = 512MB

    # WAL Settings
    wal_buffers = 64MB
    checkpoint_completion_target = 0.9
    max_wal_size = 4GB
    min_wal_size = 1GB

    # Query Tuning
    random_page_cost = 1.1
    effective_io_concurrency = 200

    # Logging
    log_destination = 'stderr'
    logging_collector = on
    log_directory = 'log'
    log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
    log_min_messages = warning
    log_min_error_statement = error

    # Encryption
    ssl = on
    ssl_cert_file = '/etc/ssl/certs/server.crt'
    ssl_key_file = '/etc/ssl/private/server.key'
```

### Redis Cache Configuration
```yaml
# redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: culture-score
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7.0-alpine
        command:
        - redis-server
        - /etc/redis/redis.conf
        ports:
        - containerPort: 6379
          name: redis
        volumeMounts:
        - name: redis-config
          mountPath: /etc/redis/redis.conf
          subPath: redis.conf
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 2Gi
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: redis-config
        configMap:
          name: redis-config
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc

---
# Redis Configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-config
  namespace: culture-score
data:
  redis.conf: |
    # Network
    bind 0.0.0.0
    port 6379
    timeout 0
    tcp-keepalive 300

    # General
    daemonize no
    supervised no
    pidfile /var/run/redis_6379.pid
    loglevel notice
    logfile ""

    # Snapshotting
    save 900 1
    save 300 10
    save 60 10000
    stop-writes-on-bgsave-error yes
    rdbcompression yes
    rdbchecksum yes
    dbfilename dump.rdb
    dir /data

    # Replication
    replica-serve-stale-data yes
    replica-read-only yes

    # Security
    requirepass ${REDIS_PASSWORD}

    # Memory Management
    maxmemory 1gb
    maxmemory-policy allkeys-lru

    # Append Only File
    appendonly yes
    appendfilename "appendonly.aof"
    appendfsync everysec
    no-appendfsync-on-rewrite no
    auto-aof-rewrite-percentage 100
    auto-aof-rewrite-min-size 64mb
```

### Ingress Configuration
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: culture-score-ingress
  namespace: culture-score
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - api.culturescore.com
    - app.culturescore.com
    secretName: culture-score-tls
  rules:
  - host: api.culturescore.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: culture-score-api-service
            port:
              number: 8000
  - host: app.culturescore.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: culture-score-frontend-service
            port:
              number: 80
```

## Docker Compose Deployment

### Production Docker Compose
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  # Reverse Proxy
  nginx:
    image: nginx:1.24-alpine
    container_name: culture-score-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - api
      - frontend
    restart: unless-stopped
    networks:
      - culture-score-network

  # API Application
  api:
    image: culture-score/api:${VERSION:-latest}
    container_name: culture-score-api
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:pass@postgres:5432/culture_score
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - SENTRY_DSN=${SENTRY_DSN}
    volumes:
      - ./app/models:/app/models:ro
      - ./logs/api:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    networks:
      - culture-score-network

  # Frontend Application
  frontend:
    image: culture-score/frontend:${VERSION:-latest}
    container_name: culture-score-frontend
    environment:
      - REACT_APP_API_URL=https://api.culturescore.com
      - REACT_APP_ENVIRONMENT=production
    volumes:
      - ./logs/frontend:/var/log/nginx
    restart: unless-stopped
    networks:
      - culture-score-network

  # PostgreSQL Database
  postgres:
    image: postgres:14.8
    container_name: culture-score-postgres
    environment:
      - POSTGRES_DB=culture_score
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_INITDB_ARGS=--auth-host=md5
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/postgresql.conf:/etc/postgresql/postgresql.conf:ro
      - ./postgres/init:/docker-entrypoint-initdb.d:ro
      - ./logs/postgres:/var/log/postgresql
    ports:
      - "5432:5432"
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d culture_score"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - culture-score-network

  # Redis Cache
  redis:
    image: redis:7.0-alpine
    container_name: culture-score-redis
    command: redis-server /etc/redis/redis.conf
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/etc/redis/redis.conf:ro
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - culture-score-network

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:v2.40.0
    container_name: culture-score-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped
    networks:
      - culture-score-network

  grafana:
    image: grafana/grafana:9.2.0
    container_name: culture-score-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    ports:
      - "3001:3000"
    restart: unless-stopped
    networks:
      - culture-score-network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

networks:
  culture-score-network:
    driver: bridge
```

## Security Configuration

### SSL/TLS Configuration
```nginx
# nginx/ssl.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
ssl_prefer_server_ciphers off;
ssl_dhparam /etc/nginx/ssl/dhparam.pem;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# Security Headers
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';";
```

### Network Security
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: culture-score-network-policy
  namespace: culture-score
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: nginx-ingress
    ports:
    - protocol: TCP
      port: 8000
  - from:
    - podSelector:
        matchLabels:
          app: culture-score-api
    - podSelector:
        matchLabels:
          app: postgresql
    - podSelector:
        matchLabels:
          app: redis
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
  - to:
    - podSelector:
        matchLabels:
          app: postgresql
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### Secret Management
```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: culture-score-secrets
  namespace: culture-score
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  redis-url: <base64-encoded-redis-url>
  jwt-secret: <base64-encoded-jwt-secret>
  api-key: <base64-encoded-api-key>

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: culture-score-vault-secret
  namespace: culture-score
spec:
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: culture-score-secrets
    creationPolicy: Owner
  data:
  - secretKey: database-url
    remoteRef:
      key: secret/culture-score
      property: database_url
  - secretKey: redis-url
    remoteRef:
      key: secret/culture-score
      property: redis_url
  - secretKey: jwt-secret
    remoteRef:
      key: secret/culture-score
      property: jwt_secret
```

## Monitoring and Observability

### Prometheus Configuration
```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'culture-score-api'
    static_configs:
      - targets: ['culture-score-api:8000']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
```

### Alerting Rules
```yaml
# monitoring/prometheus/rules/culture-score.yml
groups:
- name: culture-score.rules
  rules:
  # API Health
  - alert: APIDown
    expr: up{job="culture-score-api"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Blucentia API is down"
      description: "API has been down for more than 1 minute."

  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second."

  # Database
  - alert: DatabaseDown
    expr: up{job="postgres"} == 0
    for: 30s
    labels:
      severity: critical
    annotations:
      summary: "PostgreSQL database is down"

  - alert: HighDatabaseConnections
    expr: pg_stat_database_numbackends > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High database connection usage"

  # Memory and CPU
  - alert: HighMemoryUsage
    expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"

  - alert: HighCPUUsage
    expr: rate(container_cpu_usage_seconds_total[5m]) > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage"

  # ML Model Performance
  - alert: ModelPredictionLatency
    expr: histogram_quantile(0.95, rate(prediction_duration_seconds_bucket[5m])) > 1.0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High model prediction latency"
      description: "95th percentile latency is {{ $value }} seconds."

  - alert: ModelAccuracyDrop
    expr: model_accuracy < 0.85
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "Model accuracy has dropped"
      description: "Current accuracy is {{ $value }}."
```

## Deployment Scripts

### Automated Deployment Script
```bash
#!/bin/bash
# deploy.sh - Automated deployment script

set -e

# Configuration
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
NAMESPACE="culture-score"

echo "🚀 Starting Blucentia deployment..."
echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"

# Pre-deployment checks
check_prerequisites() {
    echo "📋 Checking prerequisites..."

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl not found. Please install kubectl."
        exit 1
    fi

    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        echo "❌ Cannot connect to Kubernetes cluster."
        exit 1
    fi

    # Check namespace
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        echo "📝 Creating namespace $NAMESPACE..."
        kubectl create namespace $NAMESPACE
    fi

    echo "✅ Prerequisites check passed"
}

# Database migration
run_migrations() {
    echo "🗄️ Running database migrations..."

    kubectl run migration-job \
        --image=culture-score/api:$VERSION \
        --rm -it --restart=Never \
        --namespace=$NAMESPACE \
        -- python -m alembic upgrade head

    echo "✅ Database migrations completed"
}

# Deploy infrastructure
deploy_infrastructure() {
    echo "🏗️ Deploying infrastructure components..."

    # Deploy secrets (from Vault)
    kubectl apply -f k8s/secrets/ -n $NAMESPACE

    # Deploy ConfigMaps
    kubectl apply -f k8s/configmaps/ -n $NAMESPACE

    # Deploy PersistentVolumes
    kubectl apply -f k8s/storage/ -n $NAMESPACE

    # Deploy Database
    kubectl apply -f k8s/database/ -n $NAMESPACE

    # Deploy Redis
    kubectl apply -f k8s/redis/ -n $NAMESPACE

    echo "✅ Infrastructure deployment completed"
}

# Deploy application
deploy_application() {
    echo "🚢 Deploying application components..."

    # Update image version
    sed -i "s|culture-score/api:.*|culture-score/api:$VERSION|g" k8s/api/deployment.yaml
    sed -i "s|culture-score/frontend:.*|culture-score/frontend:$VERSION|g" k8s/frontend/deployment.yaml

    # Deploy API
    kubectl apply -f k8s/api/ -n $NAMESPACE

    # Deploy Frontend
    kubectl apply -f k8s/frontend/ -n $NAMESPACE

    # Deploy Ingress
    kubectl apply -f k8s/ingress/ -n $NAMESPACE

    echo "✅ Application deployment completed"
}

# Health checks
verify_deployment() {
    echo "🔍 Verifying deployment..."

    # Wait for pods to be ready
    echo "Waiting for pods to be ready..."
    kubectl wait --for=condition=Ready pods -l app=culture-score-api -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=Ready pods -l app=postgresql -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=Ready pods -l app=redis -n $NAMESPACE --timeout=300s

    # Check API health
    API_URL=$(kubectl get ingress culture-score-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}')

    for i in {1..30}; do
        if curl -f "https://$API_URL/health" &> /dev/null; then
            echo "✅ API health check passed"
            break
        fi

        if [ $i -eq 30 ]; then
            echo "❌ API health check failed after 30 attempts"
            exit 1
        fi

        echo "Waiting for API to be ready... ($i/30)"
        sleep 10
    done

    # Run smoke tests
    echo "🧪 Running smoke tests..."
    kubectl run smoke-tests \
        --image=culture-score/tests:$VERSION \
        --rm -it --restart=Never \
        --namespace=$NAMESPACE \
        --env="API_URL=https://$API_URL" \
        -- python -m pytest tests/smoke/

    echo "✅ Deployment verification completed"
}

# Monitoring setup
setup_monitoring() {
    echo "📊 Setting up monitoring..."

    # Deploy Prometheus
    kubectl apply -f k8s/monitoring/prometheus/ -n $NAMESPACE

    # Deploy Grafana
    kubectl apply -f k8s/monitoring/grafana/ -n $NAMESPACE

    # Deploy ServiceMonitors
    kubectl apply -f k8s/monitoring/servicemonitors/ -n $NAMESPACE

    echo "✅ Monitoring setup completed"
}

# Cleanup old resources
cleanup_old_versions() {
    echo "🧹 Cleaning up old versions..."

    # Remove old ReplicaSets
    kubectl delete replicasets -l app=culture-score-api --all -n $NAMESPACE

    # Remove old ConfigMaps (except current)
    kubectl get configmaps -n $NAMESPACE --sort-by=.metadata.creationTimestamp -o name | head -n -3 | xargs -r kubectl delete -n $NAMESPACE

    echo "✅ Cleanup completed"
}

# Main deployment flow
main() {
    check_prerequisites
    deploy_infrastructure

    # Wait for infrastructure to be ready
    sleep 30

    run_migrations
    deploy_application
    verify_deployment
    setup_monitoring
    cleanup_old_versions

    echo "🎉 Deployment completed successfully!"
    echo "API URL: https://$(kubectl get ingress culture-score-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}')"
    echo "Dashboard: https://$(kubectl get ingress culture-score-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[1].host}')"
}

# Run deployment
main "$@"
```

### Rollback Script
```bash
#!/bin/bash
# rollback.sh - Rollback to previous version

set -e

NAMESPACE="culture-score"
PREVIOUS_VERSION=${1}

if [ -z "$PREVIOUS_VERSION" ]; then
    echo "Usage: ./rollback.sh <previous_version>"
    echo "Available versions:"
    kubectl rollout history deployment/culture-score-api -n $NAMESPACE
    exit 1
fi

echo "🔄 Rolling back to version $PREVIOUS_VERSION..."

# Rollback API
kubectl rollout undo deployment/culture-score-api --to-revision=$PREVIOUS_VERSION -n $NAMESPACE

# Rollback Frontend
kubectl rollout undo deployment/culture-score-frontend --to-revision=$PREVIOUS_VERSION -n $NAMESPACE

# Wait for rollback to complete
kubectl rollout status deployment/culture-score-api -n $NAMESPACE
kubectl rollout status deployment/culture-score-frontend -n $NAMESPACE

echo "✅ Rollback completed successfully!"
```

## Performance Tuning

### Application Performance
```python
# performance_config.py
PERFORMANCE_SETTINGS = {
    # API Settings
    'uvicorn': {
        'workers': 4,
        'worker_class': 'uvicorn.workers.UvicornWorker',
        'worker_connections': 1000,
        'max_requests': 10000,
        'max_requests_jitter': 1000,
        'timeout': 30,
        'keepalive': 5
    },

    # Database Connection Pool
    'database': {
        'pool_size': 20,
        'max_overflow': 30,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    },

    # Redis Settings
    'redis': {
        'connection_pool_size': 50,
        'retry_on_timeout': True,
        'socket_keepalive': True,
        'socket_keepalive_options': {
            'TCP_KEEPIDLE': 1,
            'TCP_KEEPINTVL': 3,
            'TCP_KEEPCNT': 5
        }
    },

    # ML Model Settings
    'ml_models': {
        'batch_size': 100,
        'cache_predictions': True,
        'cache_ttl': 3600,
        'parallel_processing': True,
        'max_workers': 4
    }
}
```

### Database Performance
```sql
-- performance_indexes.sql
-- Indexes for optimal query performance

-- Survey responses indexes
CREATE INDEX CONCURRENTLY idx_survey_responses_org_id ON survey_responses(organization_id);
CREATE INDEX CONCURRENTLY idx_survey_responses_campaign_id ON survey_responses(campaign_id);
CREATE INDEX CONCURRENTLY idx_survey_responses_submitted_at ON survey_responses(submitted_at);
CREATE INDEX CONCURRENTLY idx_survey_responses_risk_tier ON survey_responses(risk_tier);

-- Organization indexes
CREATE INDEX CONCURRENTLY idx_organizations_domain ON organizations(domain);
CREATE INDEX CONCURRENTLY idx_organizations_employee_count ON organizations(employee_count);

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY idx_responses_org_date ON survey_responses(organization_id, submitted_at);
CREATE INDEX CONCURRENTLY idx_responses_risk_date ON survey_responses(risk_tier, submitted_at);

-- Partial indexes for active records
CREATE INDEX CONCURRENTLY idx_active_campaigns ON survey_campaigns(organization_id, status)
WHERE status = 'Active';

-- Text search indexes
CREATE INDEX CONCURRENTLY idx_text_responses_gin ON survey_responses
USING gin(to_tsvector('english', text_responses::text));
```

## Disaster Recovery

### Backup Strategy
```bash
#!/bin/bash
# backup.sh - Automated backup script

BACKUP_DIR="/backups/culture-score"
DATE=$(date +%Y%m%d_%H%M%S)
NAMESPACE="culture-score"

# Database backup
backup_database() {
    echo "🗄️ Backing up database..."

    kubectl exec -n $NAMESPACE deployment/postgresql -- \
        pg_dump -U culture_score_user culture_score \
        | gzip > "$BACKUP_DIR/database_$DATE.sql.gz"

    echo "✅ Database backup completed"
}

# Redis backup
backup_redis() {
    echo "📦 Backing up Redis..."

    kubectl exec -n $NAMESPACE deployment/redis -- \
        redis-cli BGSAVE

    sleep 10

    kubectl cp $NAMESPACE/redis:/data/dump.rdb \
        "$BACKUP_DIR/redis_$DATE.rdb"

    echo "✅ Redis backup completed"
}

# Model artifacts backup
backup_models() {
    echo "🤖 Backing up ML models..."

    kubectl cp $NAMESPACE/culture-score-api:/app/models/trained \
        "$BACKUP_DIR/models_$DATE/"

    echo "✅ Model backup completed"
}

# Configuration backup
backup_config() {
    echo "⚙️ Backing up configurations..."

    kubectl get all,secrets,configmaps,pvc -n $NAMESPACE -o yaml > \
        "$BACKUP_DIR/k8s_config_$DATE.yaml"

    echo "✅ Configuration backup completed"
}

# Retention policy (keep 30 days)
cleanup_old_backups() {
    find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
    find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
    find $BACKUP_DIR -name "*.yaml" -mtime +30 -delete
    find $BACKUP_DIR -type d -name "models_*" -mtime +30 -exec rm -rf {} \;
}

# Main backup routine
mkdir -p $BACKUP_DIR
backup_database
backup_redis
backup_models
backup_config
cleanup_old_backups

echo "🎉 Backup completed successfully!"
echo "Backup location: $BACKUP_DIR"
```

This comprehensive enterprise deployment guide provides all necessary components for securely and reliably deploying the Blucentia Culture Intelligence Platform in production environments, with proper scalability, monitoring, and disaster recovery capabilities.