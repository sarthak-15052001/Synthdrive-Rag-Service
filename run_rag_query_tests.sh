#!/bin/bash

# Script to run the complete RAG query testing process
# This script:
# 1. Ingests sample data
# 2. Waits for processing
# 3. Runs the curl tests
# 4. Runs the Python tests

echo "====================================================================="
echo "SynthDrive RAG Query API Testing"
echo "====================================================================="

# Step 1: Ingest sample data
echo "Step 1: Ingesting sample data..."
python ingest_sample_data_for_testing.py

# Step 2: Wait for processing to complete
echo "Step 2: Waiting for additional processing time (15 seconds)..."
sleep 15

# Step 3: Run curl tests
echo "Step 3: Running curl tests..."
chmod +x test_rag_query_graphrag_curl.sh
./test_rag_query_graphrag_curl.sh

# Step 4: Run Python tests
echo "Step 4: Running Python tests..."
python test_rag_query_graphrag.py

# Step 5: Run GraphRAG contextualizer tests
echo "Step 5: Running GraphRAG contextualizer tests..."
python test_graph_rag_contextualizer.py

echo "====================================================================="
echo "Testing completed at $(date)"
echo "See the test results above and check the generated sample payloads"
echo "in the sample_payloads and graph_rag_payloads directories."
echo "====================================================================="