# Quantum UI with Gradio

```
                                  .-o@@@@@@o-.
                               .o@@@@@@@@@@@@@o.
                             .@@@@@@@@@@@@@@@@@@.
                            o@@@@@@@@@@@@@@@@@@@o
                           @@@@@@@@@@@@@@@@@@@@@@@
                          @@@@@@@@@@@@@@@@@@@@@@@@@
                         @@@@@@@@@@@@@@@@@@@@@@@@@@@
                         @@@@@@@@@@@@@@@@@@@@@@@@@@@
                         @@@@@@@@@@@@@@@@@@@@@@@@@@@
              .oooooooo. @@@@@@@@@@@@@@@@@@@@@@@@@@ .oooooooo.
           .o@@@@@@@@@@@o@@@@@@@@@@@@@@@@@@@@@@@@@o@@@@@@@@@@@o.
         .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.
        o@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@o
       o@@@@@@@@@Q   u   A   n   t   u   m   U   I@@@@@@@@@@@o
       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
       o@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@o
        `o@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@o'
          `o@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@o'
            `o@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@o'
```

A professional-grade quantum computing UI framework built with Gradio, providing interactive visualization and manipulation of quantum algorithms and simulations.

## Features

- Interactive quantum circuit design and visualization
- Real-time quantum state visualization
- Multiple quantum algorithm implementations
- Integration with quantum computing backends
- User-friendly interface for quantum computing experiments
- Modular architecture for easy extension
- Solid genesis states for reliable quantum initialization
- Entanglement preservation throughout transformations
- Kubernetes deployment support for cloud environments

## Architecture Highlights

This project implements a micro-module architecture that prioritizes:

- **Solid Genesis States**: Reliable initialization protocols for quantum states with verification
- **Entanglement Preservation**: Careful tracking and preservation of quantum entanglement
- **Backend Agnostic Design**: Support for multiple quantum computing providers
- **Quantum-Classical Hybrid Workflows**: Seamless integration between classical and quantum processing

See [ARCHITECTURE.md](/docs/ARCHITECTURE.md) for comprehensive details.

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)
- Docker and Kubernetes (for containerized deployment)
- IBM Quantum account for accessing real quantum hardware (optional)

### Installation

#### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/nego-drama.git
cd nego-drama

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Docker Deployment

```bash
# Build the Docker image
docker build -t quantum-ui:latest -f infrastructure/containers/Dockerfile .

# Run the container locally
docker run -p 7860:7860 -e IBMQ_TOKEN=your_token_here quantum-ui:latest
```

### Running the Application

#### Local Execution

```bash
python src/main.py
```

#### Kubernetes Deployment

The project includes Kubernetes configuration for cloud deployment:

```bash
# Create the secret for IBM Quantum credentials
kubectl create secret generic quantum-credentials \
  --from-literal=ibmq-token=your_ibmq_token_here

# Apply the Kubernetes configuration
kubectl apply -f infrastructure/orchestration/kubernetes.yaml

# Get the service URL
kubectl get service quantum-ui-service
```

## Environment Variables

The application supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| IBMQ_TOKEN | IBM Quantum Experience API token | None |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

## Quantum Backends

The system supports the following quantum backends:

- Local simulator (built-in)
- IBM Quantum Experience (requires API token)
- AWS Braket (coming soon)
- Azure Quantum (coming soon)

## Documentation

For detailed documentation, please refer to the [docs](/docs) directory:

- [Architecture Overview](/docs/ARCHITECTURE.md)
- [Contributing Guidelines](/docs/CONTRIBUTING.md)
- [API Reference](/docs/API.md)
- [Deployment Guide](/docs/DEPLOYMENT.md)

## Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## Contributing

Please read [CONTRIBUTING.md](/docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details.

## Acknowledgments

- IBM Quantum for quantum computing resources
- Gradio team for the interactive UI framework
- Quantum computing community for algorithms and inspiration
