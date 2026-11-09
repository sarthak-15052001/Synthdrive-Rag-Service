import asyncio
from test_tenant_files_custom import test_tenant_file_upload, test_tenant_file_search

async def run_test_with_longer_wait():
    print("Starting test with longer wait time...")
    
    # Upload the file
    job_id = await test_tenant_file_upload()
    
    if job_id:
        print(f"File uploaded with job ID: {job_id}")
        print("Waiting 60 seconds for ingestion to complete...")
        await asyncio.sleep(60)
        
        # Search for the file
        files = await test_tenant_file_search(job_id)
        return files
    else:
        print("File upload failed, cannot proceed with search")
        return []

if __name__ == "__main__":
    asyncio.run(run_test_with_longer_wait())