# HSEG AI System - Docker Deployment Guide

## 🚀 Quick Start with Docker

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose
- 8GB+ RAM recommended
- 10GB+ free disk space

### 1. Clone and Setup
```bash
# Navigate to project directory
cd ai-modeling

# Ensure models are trained (if not already done)
python train_individual_model.py
python train_organizational_model.py
python train_text_classifier.py
```

### 2. Build and Run with Docker Compose
```bash
# Build all services
docker-compose build

# Start all services in background
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Grafana Dashboard**: http://localhost:3001 (admin/admin123)
- **Prometheus Metrics**: http://localhost:9090

### 4. Test the System
```bash
# Health check
curl http://localhost:8000/health

# Test individual prediction
curl -X POST "http://localhost:8000/predict/individual" \
     -H "Content-Type: application/json" \
     -d '{
       "domain": "Business",
       "survey_responses": {
         "q1": 2.5, "q2": 3.0, "q3": 2.0, "q4": 3.5,
         "q5": 2.0, "q6": 3.0, "q7": 2.5, "q8": 3.0,
         "q9": 2.0, "q10": 2.5, "q11": 3.0, "q12": 2.0,
         "q13": 2.5, "q14": 3.0, "q15": 2.0, "q16": 2.5,
         "q17": 3.0, "q18": 2.0, "q19": 2.5, "q20": 3.0,
         "q21": 2.0, "q22": 2.5
       }
     }'
```

### 5. Stop the System
```bash
# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## 🏢 Enterprise Deployment Options

### Option 1: Cloud Deployment (AWS/Azure/GCP)
```bash
# 1. Push to container registry
docker tag ai-modeling_api:latest your-registry/hseg-api:latest
docker push your-registry/hseg-api:latest

# 2. Deploy using cloud-specific tools
# AWS: ECS/EKS
# Azure: Container Instances/AKS
# GCP: Cloud Run/GKE
```

### Option 2: Kubernetes Deployment
```bash
# Create namespace
kubectl create namespace hseg

# Deploy
kubectl apply -f k8s/ -n hseg

# Check status
kubectl get pods -n hseg
```

### Option 3: Traditional VPS/Server
```bash
# Copy docker-compose.yml to server
scp docker-compose.yml user@server:/opt/hseg/

# SSH and deploy
ssh user@server
cd /opt/hseg
docker-compose up -d
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:
```bash
ENV=production
DATABASE_URL=postgresql://hseg:hseg_password@db:5432/hseg_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-super-secret-key-change-this
API_HOST=0.0.0.0
API_PORT=8000
```

### SSL/HTTPS Setup
1. Add SSL certificates to `docker/ssl/`
2. Update nginx configuration
3. Use Let's Encrypt for automatic certificates

### Scaling Configuration
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  api:
    deploy:
      replicas: 3
    environment:
      - WORKERS=4
```

## 📊 Monitoring

### Available Metrics
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090
- **Application Logs**: `docker-compose logs -f api`

### Key Metrics to Monitor
- API response times
- Model prediction accuracy
- Database performance
- Memory usage
- Request rates

## 🚨 Troubleshooting

### Common Issues

#### 1. Models Not Loading
```bash
# Check if model files exist
docker-compose exec api ls -la /app/app/models/trained/

# Retrain if missing
docker-compose exec api python train_individual_model.py
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose exec db pg_isready -U hseg

# Reset database
docker-compose down
docker volume rm ai-modeling_postgres_data
docker-compose up -d
```

#### 3. Memory Issues
```bash
# Increase memory limits in docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 4G
```

#### 4. Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Debug Commands
```bash
# Access container shell
docker-compose exec api bash

# View application logs
docker-compose logs -f api

# Check resource usage
docker stats

# Test database connection
docker-compose exec db psql -U hseg -d hseg_db -c "SELECT version();"
```

## 🔐 Security Considerations

### Production Security Checklist
- [ ] Change default passwords
- [ ] Use environment variables for secrets
- [ ] Enable SSL/HTTPS
- [ ] Configure firewall rules
- [ ] Set up log monitoring
- [ ] Regular security updates
- [ ] API rate limiting
- [ ] Authentication tokens

### Recommended Security Settings
```bash
# Strong passwords
POSTGRES_PASSWORD=complex-password-here
SECRET_KEY=long-random-string-for-jwt

# Limit access
API_ALLOWED_HOSTS=your-domain.com
CORS_ORIGINS=https://your-frontend.com
```

## 📈 Performance Optimization

### For High Traffic
1. **Load Balancing**: Use multiple API containers
2. **Database**: Set up read replicas
3. **Caching**: Configure Redis for API responses
4. **CDN**: Use CloudFlare for static assets

### Model Performance
1. **Model Optimization**: Quantize models for faster inference
2. **Batch Processing**: Process multiple requests together
3. **Async Processing**: Use background tasks for heavy operations

## 📋 Production Checklist

Before going live:
- [ ] All models trained and tested
- [ ] Database migrations completed
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Documentation updated

## 🆘 Support and Maintenance

### Regular Maintenance Tasks
- Monitor system performance
- Update dependencies
- Retrain models with new data
- Database cleanup
- Log rotation
- Security updates

### Getting Help
- Check application logs: `docker-compose logs`
- Health endpoint: `/health`
- API documentation: `/docs`
- Monitoring dashboards: Grafana/Prometheus

---

## ✅ Success! Your HSEG AI System is Production-Ready

The containerized system includes:
- ✅ Complete AI pipeline with 3 trained models
- ✅ Professional React frontend
- ✅ Scalable FastAPI backend
- ✅ PostgreSQL database
- ✅ Redis caching
- ✅ Nginx load balancer
- ✅ Monitoring with Prometheus & Grafana
- ✅ Health checks and logging
- ✅ Enterprise-grade configuration

You can now share this with your frontend team or deploy to any cloud platform!