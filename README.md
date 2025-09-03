# 🧬 IONLACE Protein Structure Prediction Service

A production-ready web service for autonomous protein structure prediction using ESMFold and advanced AI agents.

## 🚀 Features

- **🧠 Autonomous AI Agent**: Implements a sophisticated "think/plan/act/observe" cycle
- **🔬 ESMFold Integration**: Local protein structure prediction using HuggingFace Transformers
- **🌐 RESTful API**: FastAPI-based web service with comprehensive endpoints
- **📊 Smart Fallbacks**: Graceful degradation with sequence-aware mock predictions
- **📈 Real-time Monitoring**: Structured logging and execution tracking
- **🐳 Docker Ready**: Containerized deployment with docker-compose

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│  Protein Agent   │───▶│  ESMFold Model  │
│                 │    │  (Think/Plan/    │    │  (Local/API)    │
│  - /predict     │    │   Act/Observe)   │    │                 │
│  - /health      │    │                  │    └─────────────────┘
│  - /docs        │    └──────────────────┘
└─────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: FastAPI + Python 3.10+
- **ML Framework**: PyTorch 2.2+ + Transformers
- **Protein Prediction**: ESMFold (Facebook/Meta)
- **Async HTTP**: aiohttp + httpx
- **Data Processing**: BioPython + NumPy + Pandas
- **Logging**: structlog
- **Containerization**: Docker + Docker Compose

## 📋 Prerequisites

- Python 3.10 or higher
- Conda or Miniconda
- 8GB+ RAM (for ESMFold model)
- Internet connection (for model download)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Ionlace-Task
```

### 2. Create Conda Environment
```bash
conda create -n ionlace-env python=3.10 -y
conda activate ionlace-env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Service
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access the Service
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Prediction Endpoint**: http://localhost:8000/predict

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
docker-compose up --build
```

### Manual Docker Build
```bash
docker build -t ionlace-service .
docker run -p 8000:8000 ionlace-service
```

## 📚 API Endpoints

### POST /predict
Predict protein structure from amino acid sequence.

**Request:**
```json
{
  "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
  "num_recycles": 3
}
```

**Response:**
```json
{
  "status": "completed",
  "prediction_id": "uuid",
  "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
  "result": {
    "execution_summary": {...},
    "step_results": {...},
    "final_report": {...}
  }
}
```

### GET /health
Service health check.

### GET /docs
Interactive API documentation (Swagger UI).

## 🧠 Autonomous Agent Workflow

The system implements a sophisticated AI agent with the following execution cycle:

1. **🤔 THINK**: Analyze input sequence and determine optimal approach
2. **📋 PLAN**: Create execution plan with 5 core steps
3. **⚡ ACT**: Execute each step sequentially
4. **👁️ OBSERVE**: Monitor results and adjust strategy

### Execution Steps:
1. **Sequence Validation**: Verify amino acid format and content
2. **Structure Prediction**: Use ESMFold for 3D structure prediction
3. **Structure Parsing**: Parse PDB format and extract metadata
4. **Metrics Calculation**: Compute structural and quality metrics
5. **Report Generation**: Create comprehensive analysis report

## 🔧 Configuration

### Environment Variables
```bash
# ESMFold Configuration
ESMFOLD_MODEL_NAME=facebook/esmfold_v1
ESMFOLD_NUM_RECYCLES=3
ESMFOLD_API_TIMEOUT=300

# Service Configuration
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### Model Configuration
The service automatically handles:
- **Local Model Loading**: HuggingFace Transformers integration
- **API Fallback**: ESM Atlas API when local model unavailable
- **Smart Mock**: Sequence-aware fallback for testing

## 📊 Performance & Monitoring

- **Execution Time Tracking**: Per-step timing and total duration
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Error Handling**: Graceful degradation with detailed error reporting
- **Resource Monitoring**: Memory and CPU usage tracking

## 🧪 Testing

### Run Tests
```bash
python -m pytest tests/
```

### Test Service Endpoints
```bash
python test_service.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# Protein prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"}'
```

## 🔍 Troubleshooting

### Common Issues

1. **Model Loading Failures**
   - Ensure PyTorch 2.2+ is installed
   - Check available memory (8GB+ recommended)
   - Verify internet connection for model download

2. **API 422 Errors**
   - Check sequence format (valid amino acids only)
   - Verify request payload structure
   - Check ESM Atlas API status

3. **Environment Issues**
   - Ensure correct Python version (3.10+)
   - Activate conda environment: `conda activate ionlace-env`
   - Reinstall dependencies: `pip install -r requirements.txt`

### Logs and Debugging
- Check service logs for detailed error information
- Use `LOG_LEVEL=DEBUG` for verbose logging
- Monitor `/health` endpoint for service status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is part of the IONLACE Technical Interview Assignment.

## 🙏 Acknowledgments

- **ESMFold**: Facebook/Meta for protein structure prediction
- **HuggingFace**: Transformers library and model hosting
- **FastAPI**: Modern web framework for building APIs
- **BioPython**: Biological data processing tools

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review service logs
3. Open an issue on GitHub
4. Contact the development team

---

**Built with ❤️ for protein structure prediction and AI research**
