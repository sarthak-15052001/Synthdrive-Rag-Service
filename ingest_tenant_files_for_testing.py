import requests
import json
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ingest_tenant_files():
    """
    Ingest sample tenant files into the SynthDrive RAG Service for testing purposes.
    This function ingests multiple files with different content, metadata, and tags
    to ensure comprehensive testing of the tenant files search functionality.
    """
    base_url = "http://localhost:8000/api/v1/rag"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"
    }
    
    # Organization ID for testing
    organization_id = "test_org_123"
    
    # Sample tenant files to ingest
    sample_files = [
        {
            "content": """
            # Business Strategy 2023
            
            ## Executive Summary
            
            Our key business objectives for 2023 focus on sustainable growth, market expansion, and digital transformation.
            
            ## Key Business Objectives
            
            1. Increase market share by 15% in core segments
            2. Launch 3 new product lines in emerging markets
            3. Achieve 25% revenue growth year-over-year
            4. Implement company-wide digital transformation initiative
            5. Reduce operational costs by 10% through process optimization
            
            ## Strategic Initiatives
            
            ### Market Expansion
            - Enter 2 new geographic markets in Asia-Pacific
            - Establish strategic partnerships with 5 key industry players
            - Increase digital marketing budget by 30%
            
            ### Product Innovation
            - Allocate 20% of R&D budget to disruptive technologies
            - Accelerate product development lifecycle by 30%
            - Implement customer-centric design processes
            
            ### Operational Excellence
            - Deploy AI-driven analytics across all business units
            - Streamline supply chain operations
            - Enhance customer service capabilities
            
            ## Success Metrics
            
            We will track progress using the following KPIs:
            - Revenue growth: 25% YoY
            - Customer acquisition cost: Reduce by 15%
            - Customer satisfaction: Increase NPS to 60+
            - Employee engagement: Improve by 20%
            - Operational efficiency: 10% cost reduction
            """,
            "metadata": {
                "file_name": "Business Strategy 2023.docx",
                "file_path": "/strategy/business/2023.docx",
                "file_type": "docx",
                "organization_id": organization_id,
                "upload_date": "2023-01-15",
                "tags": ["business", "strategy", "2023", "objectives"]
            }
        },
        {
            "content": """
            # Financial Performance Report 2023
            
            ## Executive Summary
            
            The company has demonstrated strong financial growth in 2023, with revenue increasing by 22% compared to the previous year. This report provides a detailed analysis of our financial performance and key trends.
            
            ## Revenue Trends
            
            Our total revenue for 2023 reached $125 million, representing a 22% increase from $102.5 million in 2022. Key revenue drivers include:
            
            - Core product lines: $78 million (up 15%)
            - New product launches: $22 million
            - Service contracts: $25 million (up 30%)
            
            Quarterly revenue growth showed consistent improvement throughout the year:
            - Q1: $28 million (18% YoY growth)
            - Q2: $30 million (20% YoY growth)
            - Q3: $32 million (24% YoY growth)
            - Q4: $35 million (26% YoY growth)
            
            ## Profitability Analysis
            
            Gross profit margin improved to 62% from 58% in the previous year, driven by:
            - Improved production efficiency
            - Strategic pricing adjustments
            - Favorable raw material costs
            
            EBITDA increased by 28% to $37.5 million, with EBITDA margin expanding to 30% from 28.5% in 2022.
            
            Net income grew by 32% to $22.5 million, resulting in an EPS of $2.25 (up from $1.70 in 2022).
            
            ## Cash Flow and Balance Sheet
            
            Operating cash flow increased by 25% to $33 million, providing strong support for our strategic investments.
            
            Key balance sheet metrics as of December 31, 2023:
            - Cash and equivalents: $45 million
            - Total assets: $180 million (up 15%)
            - Total debt: $40 million (debt-to-equity ratio: 0.35)
            
            ## 2024 Financial Outlook
            
            Based on our strong performance and market conditions, we project:
            - Revenue growth: 18-20%
            - Gross margin: 62-64%
            - EBITDA margin: 30-32%
            - Capital expenditure: $15-18 million
            """,
            "metadata": {
                "file_name": "Financial Performance 2023.pdf",
                "file_path": "/finance/reports/2023_performance.pdf",
                "file_type": "pdf",
                "organization_id": organization_id,
                "upload_date": "2024-01-20",
                "tags": ["financial", "2023", "revenue", "performance"]
            }
        },
        {
            "content": """
            # Digital Marketing Strategy 2023
            
            ## Executive Summary
            
            Our 2023 digital marketing strategy focuses on enhancing customer engagement, leveraging data-driven insights, and expanding our digital presence across multiple channels. This document outlines our key focus areas, tactics, and success metrics.
            
            ## Digital Marketing Focus Areas for 2023
            
            ### 1. Content Marketing Enhancement
            
            - Develop industry-specific thought leadership content
            - Increase video content production by 50%
            - Implement content personalization based on user behavior
            - Establish a regular publishing schedule across all platforms
            
            ### 2. Social Media Expansion
            
            - Increase presence on LinkedIn and Twitter for B2B engagement
            - Explore emerging platforms (TikTok, Instagram Reels) for brand awareness
            - Implement social listening tools for real-time market insights
            - Develop platform-specific content strategies
            
            ### 3. Search Engine Optimization
            
            - Conduct comprehensive keyword research for all product lines
            - Optimize website structure and technical SEO elements
            - Develop a backlink acquisition strategy
            - Focus on local SEO for regional markets
            
            ### 4. Paid Digital Advertising
            
            - Implement account-based marketing campaigns for key prospects
            - Optimize Google Ads campaigns with enhanced audience targeting
            - Explore programmatic advertising opportunities
            - Increase retargeting efforts for website visitors
            
            ### 5. Marketing Automation
            
            - Implement advanced lead scoring and nurturing workflows
            - Develop personalized email marketing campaigns
            - Integrate CRM data for improved targeting
            - Implement chatbots for initial customer engagement
            
            ## Budget Allocation
            
            Total digital marketing budget: $3.5 million
            
            - Content marketing: 30% ($1,050,000)
            - Paid advertising: 35% ($1,225,000)
            - Technology and tools: 15% ($525,000)
            - Agency and creative services: 20% ($700,000)
            
            ## Success Metrics
            
            We will measure success using the following KPIs:
            
            - Website traffic: Increase by 40%
            - Conversion rate: Improve by 15%
            - Marketing qualified leads: Increase by 30%
            - Customer acquisition cost: Reduce by 10%
            - Social media engagement: Increase by 50%
            - Content engagement metrics: Improve by 25%
            """,
            "metadata": {
                "file_name": "Digital Marketing Strategy 2023.docx",
                "file_path": "/marketing/strategy/2023.docx",
                "file_type": "docx",
                "organization_id": organization_id,
                "upload_date": "2023-01-10",
                "tags": ["marketing", "strategy", "digital", "2023"]
            }
        },
        {
            "content": """
            # Product Roadmap 2023-2024
            
            ## Executive Summary
            
            This product roadmap outlines our planned product launches and enhancements for 2023-2024. It reflects our commitment to innovation, customer-centricity, and market leadership.
            
            ## Upcoming Product Launches
            
            ### Q2 2023
            
            1. **ProductX Pro 5.0**
               - Release date: May 15, 2023
               - Key features:
                 - AI-powered analytics dashboard
                 - Enhanced integration capabilities
                 - Improved user interface
                 - Mobile application support
               - Target market: Enterprise customers
            
            2. **CloudConnect Service**
               - Release date: June 30, 2023
               - Key features:
                 - Seamless cloud migration tools
                 - Multi-cloud management
                 - Automated backup and recovery
                 - Security compliance monitoring
               - Target market: Mid-market and enterprise
            
            ### Q3 2023
            
            1. **DataInsight Platform**
               - Release date: August 20, 2023
               - Key features:
                 - Real-time data processing
                 - Custom visualization tools
                 - Predictive analytics
                 - Industry-specific templates
               - Target market: Data-intensive industries
            
            2. **MobileWorkspace App**
               - Release date: September 15, 2023
               - Key features:
                 - Cross-platform compatibility
                 - Offline functionality
                 - Secure document sharing
                 - Team collaboration tools
               - Target market: Remote and hybrid workforces
            
            ### Q4 2023
            
            1. **SecurityShield 2.0**
               - Release date: November 10, 2023
               - Key features:
                 - Advanced threat detection
                 - Zero-trust architecture
                 - Compliance automation
                 - Incident response workflows
               - Target market: All segments with enhanced focus on regulated industries
            
            ### Q1 2024
            
            1. **ProductX Lite**
               - Release date: February 2024
               - Key features:
                 - Streamlined functionality
                 - Simplified user interface
                 - Essential integrations
                 - Competitive pricing
               - Target market: Small businesses and startups
            
            2. **IndustrySpecific Solutions**
               - Release date: March 2024
               - Vertical solutions for:
                 - Healthcare
                 - Financial services
                 - Manufacturing
                 - Retail
               - Target market: Industry-specific enterprise customers
            
            ### Q2 2024
            
            1. **ProductX Enterprise 6.0**
               - Release date: May 2024
               - Key features:
                 - Advanced AI capabilities
                 - Enhanced security features
                 - Expanded integration ecosystem
                 - Custom workflow builder
               - Target market: Large enterprise customers
            
            ## Product Enhancement Timeline
            
            In addition to new product launches, we will deliver regular enhancements to existing products:
            
            - Monthly security updates
            - Quarterly feature releases
            - Bi-annual major version updates
            
            ## Market Strategy
            
            Each product launch will be supported by:
            - Pre-launch beta programs with key customers
            - Comprehensive marketing campaigns
            - Sales enablement training
            - Customer success programs
            """,
            "metadata": {
                "file_name": "Product Roadmap 2023-2024.pdf",
                "file_path": "/product/roadmap/2023_2024.pdf",
                "file_type": "pdf",
                "organization_id": organization_id,
                "upload_date": "2023-02-05",
                "tags": ["product", "roadmap", "2023", "2024", "launches"]
            }
        },
        {
            "content": """
            # Annual Report 2023
            
            ## Letter from the CEO
            
            Dear Shareholders,
            
            I am pleased to present our Annual Report for the fiscal year 2023. This has been a transformative year for our company, marked by strong financial performance, strategic acquisitions, and significant product innovations.
            
            ## 2023 Annual Report Highlights
            
            ### Financial Performance
            
            - Revenue: $125 million (22% YoY growth)
            - Gross margin: 62% (up from 58% in 2022)
            - EBITDA: $37.5 million (28% YoY growth)
            - Net income: $22.5 million (32% YoY growth)
            - Earnings per share: $2.25 (up from $1.70 in 2022)
            - Operating cash flow: $33 million (25% YoY growth)
            
            ### Strategic Achievements
            
            1. **Market Expansion**
               - Successfully entered two new geographic markets in Asia-Pacific
               - Established strategic partnerships with 4 industry leaders
               - Increased market share in core segments by 17%
            
            2. **Product Innovation**
               - Launched 4 new product lines, exceeding our target of 3
               - Reduced product development cycle by 35%
               - Received 2 industry innovation awards
            
            3. **Operational Excellence**
               - Implemented AI-driven analytics across all business units
               - Reduced operational costs by 12%, exceeding our 10% target
               - Improved supply chain efficiency by 20%
            
            4. **Digital Transformation**
               - Completed phase 1 of our company-wide digital transformation initiative
               - Migrated 80% of our infrastructure to cloud platforms
               - Implemented advanced data analytics capabilities
            
            ### Customer Success
            
            - Increased customer satisfaction (NPS score of 65, up from 52)
            - Reduced customer acquisition cost by 18%
            - Improved customer retention rate to 92% (up from 85%)
            
            ### Employee Engagement
            
            - Improved employee engagement score by 22%
            - Reduced voluntary turnover by 15%
            - Expanded workforce by 18% to support growth
            
            ## Corporate Social Responsibility
            
            - Reduced carbon footprint by 25%
            - Implemented sustainable sourcing for 70% of materials
            - Launched community education initiatives in 5 regions
            
            ## Looking Ahead to 2024
            
            As we look to 2024, we are well-positioned for continued growth and innovation. Our strategic priorities include:
            
            1. Accelerating product development in emerging technologies
            2. Expanding our global footprint with focus on European markets
            3. Enhancing our digital capabilities and customer experience
            4. Continuing our commitment to sustainability and social responsibility
            
            We remain committed to delivering value to our shareholders, customers, employees, and communities.
            
            Sincerely,
            
            [CEO Name]
            Chief Executive Officer
            """,
            "metadata": {
                "file_name": "Annual Report 2023.pdf",
                "file_path": "/corporate/annual_reports/2023.pdf",
                "file_type": "pdf",
                "organization_id": organization_id,
                "upload_date": "2024-02-15",
                "tags": ["annual", "report", "2023", "corporate"]
            }
        }
    ]
    
    logger.info(f"Ingesting {len(sample_files)} sample tenant files for testing")
    
    # Create directory for tenant files
    os.makedirs("tenant_files", exist_ok=True)
    
    # Ingest each file
    for i, file_data in enumerate(sample_files):
        file_name = file_data["metadata"]["file_name"]
        logger.info(f"Ingesting file {i+1}/{len(sample_files)}: {file_name}")
        
        # Save the content to a local file for reference
        file_path = os.path.join("tenant_files", file_name.replace(" ", "_"))
        with open(file_path, "w") as f:
            f.write(file_data["content"])
        
        # Prepare the payload for the API
        payload = {
            "content": file_data["content"],
            "metadata": {
                "source": file_data["metadata"]["file_path"],
                "author": "Test User",
                "document_type": file_data["metadata"]["file_type"],
                "tags": file_data["metadata"]["tags"],
                "additional_metadata": {
                    "file_name": file_data["metadata"]["file_name"],
                    "file_path": file_data["metadata"]["file_path"],
                    "organization_id": file_data["metadata"]["organization_id"],
                    "upload_date": file_data["metadata"]["upload_date"]
                }
            },
            "tenant_id": "default"
        }
        
        try:
            # Make the request to ingest the document
            response = requests.post(
                f"{base_url}/ingest/document", 
                json=payload, 
                headers=headers
            )
            
            # Check if the request was successful
            if response.status_code in [200, 202]:
                logger.info(f"Successfully ingested file {i+1}: {response.json()}")
            else:
                logger.error(f"Failed to ingest file {i+1}: {response.text}")
                
        except Exception as e:
            logger.error(f"Error ingesting file {i+1}: {str(e)}")
    
    # Wait for processing to complete
    logger.info("Waiting for document processing to complete (30 seconds)")
    time.sleep(30)
    
    logger.info("Sample tenant files ingestion completed")
    logger.info(f"Files saved locally in the 'tenant_files' directory for reference")

if __name__ == "__main__":
    ingest_tenant_files()