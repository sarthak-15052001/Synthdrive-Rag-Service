#!/bin/bash

# Script to run the complete tenant files testing process
# This script:
# 1. Ingests sample tenant files
# 2. Waits for processing
# 3. Runs the curl tests
# 4. Runs the Python tests

echo "====================================================================="
echo "SynthDrive RAG Query API Testing with Tenant Files"
echo "====================================================================="

# Step 1: Ingest sample tenant files
echo "Step 1: Ingesting sample tenant files..."
python ingest_tenant_files_for_testing.py

# Step 2: Wait for processing to complete
echo "Step 2: Waiting for additional processing time (15 seconds)..."
sleep 15

# Step 3: Run curl tests
echo "Step 3: Running curl tests with tenant file filters..."
chmod +x test_rag_query_tenant_files_curl.sh
./test_rag_query_tenant_files_curl.sh

# Step 4: Run Python tests
echo "Step 4: Running Python tests with tenant file filters..."
python test_rag_query_tenant_files.py

echo "====================================================================="
echo "Testing completed at $(date)"
echo "See the test results above and check the generated sample payloads"
echo "in the tenant_file_payloads directory."
echo "====================================================================="