from setuptools import setup, find_packages

setup(
    name="synthdrive-rag-service",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic-settings",
        "weaviate-client",
        "neo4j",
        "langchain",
        "langchain-community",
        "langgraph",
        "langchain-openai",
    ],
)