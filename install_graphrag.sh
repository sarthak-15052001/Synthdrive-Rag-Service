#!/bin/bash

# Installation script for Neo4j GraphRAG integration
# This script installs packages in phases to avoid dependency resolution issues

set -e  # Exit on error

echo "======================================================================"
echo "Neo4j GraphRAG Installation Script"
echo "======================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${YELLOW}Step 1: Checking Python version...${NC}"
python --version

echo ""
echo -e "${YELLOW}Step 2: Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

echo ""
echo -e "${YELLOW}Step 3: Installing core dependencies (numpy 2.x first)...${NC}"
pip install "numpy>=2.0.0,<3.0.0"

echo ""
echo -e "${YELLOW}Step 4: Installing Neo4j and GraphRAG...${NC}"
pip install "neo4j>=5.17.0,<6.0.0"
pip install "neo4j-graphrag==1.10.0"

echo ""
echo -e "${YELLOW}Step 5: Installing updated LangChain ecosystem...${NC}"
pip install "langchain-core>=0.3.0,<0.4.0"
pip install "langchain>=0.3.0,<0.4.0"
pip install "langchain-community>=0.3.0,<0.4.0"
pip install "langchain-text-splitters>=0.3.0,<0.4.0"
pip install "langchain-openai>=0.2.0,<0.3.0"
pip install "langgraph>=0.2.0,<0.3.0"

echo ""
echo -e "${YELLOW}Step 6: Installing web framework...${NC}"
pip install "fastapi==0.104.1"
pip install "uvicorn==0.24.0"
pip install "pydantic>=2.0.0,<3.0.0"
pip install "pydantic-settings>=2.10.1,<3.0.0"
pip install "python-multipart==0.0.6"

echo ""
echo -e "${YELLOW}Step 7: Installing authentication packages...${NC}"
pip install "python-jose[cryptography]==3.3.0"
pip install "passlib[bcrypt]>=1.7.4"

echo ""
echo -e "${YELLOW}Step 8: Installing database clients...${NC}"
pip install "sqlalchemy>=2.0.0,<3.0.0"
pip install "psycopg2-binary>=2.9.6"
pip install "weaviate-client==4.5.2"

echo ""
echo -e "${YELLOW}Step 9: Installing utilities...${NC}"
pip install "python-dotenv>=1.0.0"
pip install "tenacity>=8.2.2"
pip install "httpx>=0.24.1"

echo ""
echo -e "${YELLOW}Step 10: Installing async task manager...${NC}"
pip install "celery==5.3.4"

echo ""
echo -e "${YELLOW}Step 11: Installing testing packages...${NC}"
pip install "pytest>=7.3.1"
pip install "pytest-asyncio>=0.21.0"
pip install "pytest-mock>=3.10.0"

echo ""
echo -e "${GREEN}======================================================================"
echo "Installation Complete!"
echo "======================================================================${NC}"

echo ""
echo "Verifying installation..."
python -c "import neo4j_graphrag; print('✓ neo4j-graphrag version:', neo4j_graphrag.__version__)"
python -c "import langchain; print('✓ langchain version:', langchain.__version__)"
python -c "import numpy; print('✓ numpy version:', numpy.__version__)"
python -c "import neo4j; print('✓ neo4j driver version:', neo4j.__version__)"

echo ""
echo -e "${GREEN}All packages installed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Configure .env file with Neo4j and OpenAI credentials"
echo "2. Start Neo4j 5.17+: docker run -d -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.17.0"
echo "3. Test: python examples/neo4j_graphrag_example.py"
echo "4. Run service: uvicorn src.main:app --reload"