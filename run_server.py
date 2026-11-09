import uvicorn
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Run the FastAPI server for testing the GCS file ingestion API.
    """
    logger.info("Starting the FastAPI server for testing")
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Get host from environment or use default
    host = os.environ.get("HOST", "127.0.0.1")
    
    logger.info(f"Server will run at http://{host}:{port}")
    logger.info("Press Ctrl+C to stop the server")
    
    # Run the server
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=True  # Enable auto-reload for development
    )

if __name__ == "__main__":
    main()