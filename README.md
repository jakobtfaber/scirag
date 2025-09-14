# Enhanced SciRAG

Enhanced SciRAG is a scientific document processing system that combines the original SciRAG capabilities with advanced RAGBook integration for superior mathematical content handling.

### Local Development
```bash
# Run the enhanced processing
./scirag_notebook_env/bin/python test_final_verification.py

# Or use the local server
./scripts/run_local.sh
```

### Docker Deployment
```bash
# Deploy with Docker
./scripts/deploy.sh
```

## Directory Structure

- `scirag/` - Main SciRAG package with enhanced processing
- `scripts/` - Deployment and utility scripts
- `development/` - Development files organized by phase
- `deployment/` - Production deployment configurations
- `archive/` - Archived development files

## Core Features

- **Mathematical Content Processing** - Full LaTeX equation support
- **Intelligent Content Classification** - Automatic content type detection
- **Enhanced Chunking** - Smart chunking that preserves structure
- **Asset Processing** - Figure and table handling
- **Glossary Extraction** - Definition and term extraction

## Documentation

- [Production Guide](deployment/PRODUCTION_GUIDE.md)
- [Development History](development/)
- [API Documentation](scirag/api/)
