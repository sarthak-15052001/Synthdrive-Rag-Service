from typing import List, Optional, Dict, Union
from datetime import datetime, UTC
from pydantic import BaseModel, HttpUrl, field_serializer
import logging
import json
import httpx
import os
from src.core.config import settings

class Feature(BaseModel):
    name: str
    description: str
    use_case: str

class Subscription(BaseModel):
    plan_name: str
    price_monthly: Optional[float]
    price_annual: Optional[float]
    pricing_model: str
    features_included: List[str]

class Categories(BaseModel):
    primary: str
    secondary: List[str]

class Compliance(BaseModel):
    gdpr_compliant: bool
    us_cloud_act_safe: bool
    data_sovereignty_options: List[str]
    certifications: List[str]
 
class GlobalTool(BaseModel):
    name: str
    homepage_url: HttpUrl
    last_scraped_at: datetime
    source_urls: List[HttpUrl]
    categories: Categories
    short_description: str
    detailed_description: str
    features: List[Feature]
    differentiators: List[str]
    subscriptions: List[Subscription]
    compliance: Compliance
    documentation_links: List[HttpUrl]
    rating: float
    logo_url: Optional[HttpUrl] = None
    tags: List[str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Sample AI Tool",
                "homepage_url": "https://tool-website.com",
                "last_scraped_at": "2025-11-19T06:08:19.972Z",
                "source_urls": ["https://source1.com", "https://source2.com"],
                "categories": {
                    "primary": "AI Writing",
                    "secondary": ["Content Generation", "Marketing"]
                },
                "short_description": "A brief description of the tool (max 500 chars)",
                "detailed_description": "A more detailed explanation of what the tool does and how it works...",
                "features": [
                    {
                        "name": "Feature 1",
                        "description": "Description of feature 1",
                        "use_case": "Example use case for feature 1"
                    }
                ],
                "differentiators": [
                    "What makes this tool unique compared to competitors",
                    "Another unique selling point"
                ],
                "subscriptions": [
                    {
                        "plan_name": "Free",
                        "price_monthly": None,
                        "price_annual": None,
                        "pricing_model": "freemium",
                        "features_included": ["Basic feature 1", "Basic feature 2"]
                    }
                ],
                "compliance": {
                    "gdpr_compliant": True,
                    "us_cloud_act_safe": False,
                    "data_sovereignty_options": ["EU", "US"],
                    "certifications": ["SOC2", "ISO 27001"]
                },
                "documentation_links": [
                    "https://docs.tool-website.com/getting-started",
                    "https://docs.tool-website.com/api-reference"
                ],
                "rating": 4.5,
                "logo_url": "https://tool-website.com/logo.png",
                "tags": ["AI", "Productivity", "Content Creation"]
            }
        }
    }

    @field_serializer('last_scraped_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

    @field_serializer('logo_url')
    def serialize_logo_url(self, logo_url: Optional[HttpUrl]) -> Optional[str]:
        return str(logo_url) if logo_url else None


class GlobalToolsClient:
    def __init__(self, base_url: str = settings.BACKEND_SERVICE_URL, api_key: Optional[str] = None):
        self.base_url = base_url
        self.endpoint = f"{self.base_url}/api/global-tools"
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Add console handler if not already added
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    async def add_global_tool(self, tool: GlobalTool) -> dict:
        """
        Add a new global tool to the external service.
        
        Args:
            tool: GlobalTool object containing tool information
            
        Returns:
            dict: Response from the API
        """

        self.logger.info("="*50)
        self.logger.info("GLOBAL TOOLS CONNECTOR - Starting Tool Ingestion")
        self.logger.info("="*50)
        self.logger.info(f"Tool Name: {tool.name}")
        self.logger.info(f"Endpoint: {self.endpoint}")
        
        async with httpx.AsyncClient() as client:
            # Convert model to dict and serialize special types
            data = tool.model_dump(exclude_none=True)
            self.logger.debug("Tool Data Details:")
            self.logger.debug(f"- Categories: Primary={data['categories']['primary']}, Secondary={data['categories']['secondary']}")
            self.logger.debug(f"- Features Count: {len(data['features'])}")
            self.logger.debug(f"- Subscription Plans: {len(data['subscriptions'])}")
            
            def serialize_types(obj):
                if obj is None:
                    return None
                if isinstance(obj, dict):
                    return {k: serialize_types(v) for k, v in obj.items() if v is not None}
                elif isinstance(obj, list):
                    return [serialize_types(i) for i in obj if i is not None]
                elif isinstance(obj, HttpUrl):
                    return str(obj) if obj else None
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                elif hasattr(obj, '__str__') and not isinstance(obj, (str, int, float, bool, type(None))):
                    # Convert any object with __str__ method to string
                    return str(obj)
                return obj
            
            serialized_data = serialize_types(data)
            
            try:
                self.logger.info(f"Sending request to global tools service...")
                response = await client.post(
                    self.endpoint,
                    json=serialized_data
                )
                response.raise_for_status()
                response_data = response.json()
                
                self.logger.info("="*50)
                self.logger.info("GLOBAL TOOLS CONNECTOR - Tool Successfully Added")
                self.logger.info("="*50)
                self.logger.info(f"Tool '{tool.name}' successfully stored in global service")
                self.logger.debug("Storage Details:")
                self.logger.debug(f"- Response: {json.dumps(response_data, indent=2)}")
                self.logger.debug(f"- Status Code: {response.status_code}")
                self.logger.debug(f"- Headers: {dict(response.headers)}")
                
                return response_data
            except httpx.HTTPStatusError as e:
                # Check if this is a duplicate tool error (400 with specific message)
                if e.response.status_code == 400:
                    try:
                        error_data = e.response.json()
                        if "message" in error_data and "already exists" in error_data["message"].lower():
                            self.logger.info("="*50)
                            self.logger.info("GLOBAL TOOLS CONNECTOR - Tool Already Exists")
                            self.logger.info("="*50)
                            self.logger.info(f"Tool '{tool.name}' already exists in global service - skipping creation")
                            self.logger.debug("Duplicate Details:")
                            self.logger.debug(f"- Status Code: {e.response.status_code}")
                            self.logger.debug(f"- Message: {error_data['message']}")
                            # Return a success-like response for duplicate tools
                            return {"success": True, "message": "Tool already exists", "duplicate": True}
                    except (json.JSONDecodeError, KeyError):
                        pass  # Fall through to normal error handling

                # Handle other HTTP errors normally
                self.logger.error("="*50)
                self.logger.error("GLOBAL TOOLS CONNECTOR - Tool Ingestion Failed - HTTP Error")
                self.logger.error("="*50)
                self.logger.error(f"Status Code: {e.response.status_code}")
                self.logger.error(f"Response Text: {e.response.text}")
                self.logger.error(f"Request URL: {e.request.url}")
                self.logger.error(f"Request Headers: {dict(e.request.headers)}")
                raise
            except httpx.RequestError as e:
                self.logger.error("="*50)
                self.logger.error("GLOBAL TOOLS CONNECTOR - Tool Ingestion Failed - Network Error")
                self.logger.error("="*50)
                self.logger.error(f"Error Type: {type(e).__name__}")
                self.logger.error(f"Error Message: {str(e)}")
                self.logger.error(f"Request URL: {self.endpoint}")
                raise
            except Exception as e:
                self.logger.error("="*50)
                self.logger.error("GLOBAL TOOLS CONNECTOR - Tool Ingestion Failed - Unexpected Error")
                self.logger.error("="*50)
                self.logger.error(f"Error Type: {type(e).__name__}")
                self.logger.error(f"Error Message: {str(e)}")
                self.logger.error(f"Tool Name: {tool.name}")
                self.logger.error(f"Endpoint: {self.endpoint}")
                raise

class Content(BaseModel):
    summary: str
    learning_objectives: List[str] = []
    full_text_markdown: str
    video_transcript: Optional[str] = None
    video_url: Optional[HttpUrl] = None

    @field_serializer('video_url')
    def serialize_video_url(self, video_url: Optional[HttpUrl]) -> Optional[str]:
        return str(video_url) if video_url else None

class TargetAudience(BaseModel):
    expertise_level: str
    job_roles: List[str]

class Taxonomy(BaseModel):
    department: str
    team_task_category: str
    type_category: str

class KPIBenefits(BaseModel):
    estimated_time_saving: Optional[str] = None
    efficiency_gain_percentage: Optional[int] = None
    cost_reduction: Optional[str] = None
    quality_improvement_metric: Optional[str] = None

class Subscriptions(BaseModel):
    plan_name: str
    price_monthly: Optional[float] = None
    price_annual: Optional[float] = None
    pricing_model: str
    features_included: List[str] = []

class GlobalLearningResource(BaseModel):
    title: str
    description: str
    source_url: HttpUrl
    resource_type: str
    categories: Categories
    topics_discussed: List[str]
    target_audience: TargetAudience
    useful_context: List[str]
    content: Content
    tags: List[str]
    estimatedTime: str
    platform_name: Optional[str] = None
    platform_logo_url: Optional[HttpUrl] = None
    associated_tool: Optional[str] = None
    taxonomy: Optional[Taxonomy] = None
    kpi_benefits: Optional[KPIBenefits] = None
    is_paid: Optional[bool] = None
    subscriptions: Optional[Subscriptions] = None


    @field_serializer('source_url')
    def serialize_source_url(self, source_url: HttpUrl) -> str:
        return str(source_url)

    @field_serializer('platform_logo_url')
    def serialize_platform_logo_url(self, platform_logo_url: Optional[HttpUrl]) -> Optional[str]:
        return str(platform_logo_url) if platform_logo_url else None

class GlobalLearningResourcesClient:
    def __init__(self, base_url: str = settings.BACKEND_SERVICE_URL, api_key: Optional[str] = None):
        self.base_url = base_url
        self.endpoint = f"{self.base_url}/api/global-learning-resources"
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Add console handler if not already added
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    async def post_learning_resource(self, resource: GlobalLearningResource) -> dict:
        """
        Add a new global learning resource to the external service.
        
        Args:
            resource: GlobalLearningResource object containing resource information
            
        Returns:
            dict: Response from the API
            
        Raises:
            httpx.HTTPStatusError: If the API request fails with an HTTP error
            httpx.RequestError: If the request fails due to network issues
            ValueError: If the resource validation fails
            Exception: For other unexpected errors
        """

        self.logger.info("="*50)
        self.logger.info("GLOBAL LEARNING RESOURCES CONNECTOR - Starting Resource Ingestion")
        self.logger.info("="*50)
        self.logger.info(f"Resource Title: {resource.title}")
        self.logger.info(f"Endpoint: {self.endpoint}")
        
        try:
            # Validate resource before making request
            resource_dict = resource.model_dump(exclude_none=True)
            self.logger.debug("Resource Data Details:")
            self.logger.debug(f"- Categories: Primary={resource_dict['categories']['primary']}, Secondary={resource_dict['categories']['secondary']}")
            self.logger.debug(f"- Topics: {', '.join(resource_dict['topics_discussed'])}")
            self.logger.debug(f"- Target Audience: {resource_dict['target_audience']}")
            
            def serialize_types(obj):
                if isinstance(obj, dict):
                    return {k: serialize_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [serialize_types(i) for i in obj]
                elif isinstance(obj, HttpUrl):
                    return str(obj)
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                elif hasattr(obj, '__str__') and not isinstance(obj, (str, int, float, bool, type(None))):
                    # Convert any object with __str__ method to string
                    return str(obj)
                return obj

            serialized_data = serialize_types(resource_dict)
            
            async with httpx.AsyncClient() as client:
                try:
                    self.logger.info(f"Sending request to global learning resources service...")
                    response = await client.post(
                        self.endpoint,
                        json=serialized_data,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    response_data = response.json()
                    
                    self.logger.info("="*50)
                    self.logger.info("GLOBAL LEARNING RESOURCES CONNECTOR - Resource Successfully Added")
                    self.logger.info("="*50)
                    self.logger.info(f"Resource '{resource.title}' successfully stored in global service")
                    self.logger.debug("Storage Details:")
                    self.logger.debug(f"- Response: {json.dumps(response_data, indent=2)}")
                    self.logger.debug(f"- Status Code: {response.status_code}")
                    self.logger.debug(f"- Headers: {dict(response.headers)}")
                    
                    return response_data
                    
                except httpx.HTTPStatusError as e:
                    # Check if this is a duplicate resource error (400 with specific message)
                    if e.response.status_code == 400:
                        try:
                            error_data = e.response.json()
                            if "message" in error_data and "already exists" in error_data["message"].lower():
                                self.logger.info("="*50)
                                self.logger.info("GLOBAL LEARNING RESOURCES CONNECTOR - Resource Already Exists")
                                self.logger.info("="*50)
                                self.logger.info(f"Resource '{resource.title}' already exists in global service - skipping creation")
                                self.logger.debug("Duplicate Details:")
                                self.logger.debug(f"- Status Code: {e.response.status_code}")
                                self.logger.debug(f"- Message: {error_data['message']}")
                                # Return a success-like response for duplicate resources
                                return {"success": True, "message": "Resource already exists", "duplicate": True}
                        except (json.JSONDecodeError, KeyError):
                            pass  # Fall through to normal error handling

                    # Handle other HTTP errors normally
                    self.logger.error("="*50)
                    self.logger.error("GLOBAL LEARNING RESOURCES CONNECTOR - Resource Ingestion Failed - HTTP Error")
                    self.logger.error("="*50)
                    self.logger.error(f"Status Code: {e.response.status_code}")
                    self.logger.error(f"Response Text: {e.response.text}")
                    self.logger.error(f"Request URL: {e.request.url}")
                    self.logger.error(f"Request Headers: {dict(e.request.headers)}")
                    raise
                except httpx.RequestError as e:
                    self.logger.error("="*50)
                    self.logger.error("GLOBAL LEARNING RESOURCES CONNECTOR - Resource Ingestion Failed - Network Error")
                    self.logger.error("="*50)
                    self.logger.error(f"Error Type: {type(e).__name__}")
                    self.logger.error(f"Error Message: {str(e)}")
                    self.logger.error(f"Request URL: {self.endpoint}")
                    raise
                    
        except ValueError as e:
            self.logger.error("="*50)
            self.logger.error("GLOBAL LEARNING RESOURCES CONNECTOR - Resource Ingestion Failed - Validation Error")
            self.logger.error("="*50)
            self.logger.error(f"Error Message: {str(e)}")
            raise ValueError(f"Resource validation failed: {str(e)}")
        except Exception as e:
            self.logger.error("="*50)
            self.logger.error("GLOBAL LEARNING RESOURCES CONNECTOR - Resource Ingestion Failed - Unexpected Error")
            self.logger.error("="*50)
            self.logger.error(f"Error Type: {type(e).__name__}")
            self.logger.error(f"Error Message: {str(e)}")
            self.logger.error(f"Resource Title: {resource.title}")
            self.logger.error(f"Endpoint: {self.endpoint}")
            raise Exception(f"Unexpected error occurred: {str(e)}")


class NoCodeTemplateCategory(BaseModel):
    primary: str
    secondary: List[str] = []


class TaxonomyTemplate(BaseModel):
    department: str
    team_task_category: str
    type_category: str


class TargetAudienceTemplateModel(BaseModel):
    expertise_level: str
    job_roles: List[str] = []


class KPIBenefitsTemplate(BaseModel):
    estimated_time_saving: Optional[str] = None
    efficiency_gain_percentage: Optional[int] = None
    cost_reduction: Optional[str] = None
    quality_improvement_metric: Optional[str] = None


class NoCodeTemplate(BaseModel):
    name: str
    source_url: HttpUrl
    platform: str
    platform_logo_url: Optional[HttpUrl] = None
    use_cases: List[str] = []
    short_description: str
    complexity: str
    categories: NoCodeTemplateCategory
    concrete_tasks: List[str] = []
    required_connections: List[str] = []
    taxonomy: TaxonomyTemplate
    target_audience: TargetAudienceTemplateModel
    kpi_benefits: Optional[KPIBenefitsTemplate] = None
    blueprint_json_url: Optional[HttpUrl] = None

    @field_serializer('source_url')
    def serialize_source_url(self, source_url: HttpUrl) -> str:
        return str(source_url)
    
    @field_serializer('platform_logo_url')
    def serialize_platform_logo_url(self, platform_logo_url: Optional[HttpUrl]) -> Optional[str]:
        return str(platform_logo_url) if platform_logo_url else None
    
    @field_serializer('blueprint_json_url')
    def serialize_blueprint_json_url(self, blueprint_json_url: Optional[HttpUrl]) -> Optional[str]:
        return str(blueprint_json_url) if blueprint_json_url else None


class NoCodeTemplatesClient:
    def __init__(self, base_url: str = settings.BACKEND_SERVICE_URL, api_key: Optional[str] = None):
        self.base_url = base_url
        self.endpoint = f"{self.base_url}/api/no-code-templates"
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Add console handler if not already added
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    async def post_no_code_template(self, template: NoCodeTemplate) -> dict:
        """
        Add a new no-code template to the external service.
        
        Args:
            template: NoCodeTemplate object containing template information
            
        Returns:
            dict: Response from the API
            
        Raises:
            httpx.HTTPStatusError: If the API request fails with an HTTP error
            httpx.RequestError: If the request fails due to network issues
            ValueError: If the template validation fails
            Exception: For other unexpected errors
        """

        self.logger.info("="*50)
        self.logger.info("NO-CODE TEMPLATES CONNECTOR - Starting Template Ingestion")
        self.logger.info("="*50)
        self.logger.info(f"Template Name: {template.name}")
        self.logger.info(f"Endpoint: {self.endpoint}")
        
        try:
            # Convert to JSON string first, then back to dict to ensure all serializers are applied
            import json
            template_json = template.model_dump_json(exclude_none=True)
            template_dict = json.loads(template_json)
            
            self.logger.debug("Template Data Details:")
            self.logger.debug(f"- Platform: {template_dict.get('platform')}")
            self.logger.debug(f"- Complexity: {template_dict.get('complexity')}")
            self.logger.debug(f"- Categories: Primary={template_dict.get('categories', {}).get('primary')}, Secondary={template_dict.get('categories', {}).get('secondary')}")
            self.logger.debug(f"- Use Cases: {', '.join(template_dict.get('use_cases', []))}")
            
            # Double-check: Ensure all HttpUrl objects are converted to strings
            def serialize_types(obj):
                if obj is None:
                    return None
                if isinstance(obj, dict):
                    return {k: serialize_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [serialize_types(i) for i in obj]
                elif isinstance(obj, HttpUrl):
                    return str(obj)
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                elif hasattr(obj, '__str__') and not isinstance(obj, (str, int, float, bool, type(None))):
                    # Convert any object with __str__ method to string
                    return str(obj)
                return obj
            
            serialized_data = serialize_types(template_dict)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    self.logger.info(f"Sending request to no-code templates service...")
                
                    
                    response = await client.post(
                        self.endpoint,
                        json=serialized_data
                    )
                    response.raise_for_status()
                    response_data = response.json()
                    
                    self.logger.info("="*50)
                    self.logger.info("NO-CODE TEMPLATES CONNECTOR - Template Successfully Added")
                    self.logger.info("="*50)
                    self.logger.info(f"Template '{template.name}' successfully stored in global service")
                    self.logger.debug("Storage Details:")
                    self.logger.debug(f"- Response: {json.dumps(response_data, indent=2)}")
                    self.logger.debug(f"- Status Code: {response.status_code}")
                    self.logger.debug(f"- Headers: {dict(response.headers)}")
                    
                    return response_data
                    
                except httpx.HTTPStatusError as e:
                    self.logger.error("="*50)
                    self.logger.error("NO-CODE TEMPLATES CONNECTOR - Template Ingestion Failed - HTTP Error")
                    self.logger.error("="*50)
                    self.logger.error(f"Status Code: {e.response.status_code}")
                    self.logger.error(f"Response Text: {e.response.text}")
                    self.logger.error(f"Request URL: {e.request.url}")
                    self.logger.error(f"Request Headers: {dict(e.request.headers)}")
                    raise
                except httpx.TimeoutException as e:
                    self.logger.error("="*50)
                    self.logger.error("NO-CODE TEMPLATES CONNECTOR - Template Ingestion Failed - Timeout")
                    self.logger.error("="*50)
                    self.logger.error(f"Error Type: {type(e).__name__}")
                    self.logger.error(f"Error Message: Request to external service timed out after 60 seconds")
                    self.logger.error(f"Request URL: {self.endpoint}")
                    self.logger.error("Possible causes:")
                    self.logger.error("  1. External service is processing the request slowly")
                    self.logger.error("  2. External service is experiencing high load")
                    self.logger.error("  3. Network connectivity issues")
                    self.logger.error("  4. External service database operations are slow")
                    raise
                except httpx.RequestError as e:
                    self.logger.error("="*50)
                    self.logger.error("NO-CODE TEMPLATES CONNECTOR - Template Ingestion Failed - Network Error")
                    self.logger.error("="*50)
                    self.logger.error(f"Error Type: {type(e).__name__}")
                    self.logger.error(f"Error Message: {str(e)}")
                    self.logger.error(f"Request URL: {self.endpoint}")
                    raise
                    
        except ValueError as e:
            self.logger.error("="*50)
            self.logger.error("NO-CODE TEMPLATES CONNECTOR - Template Ingestion Failed - Validation Error")
            self.logger.error("="*50)
            self.logger.error(f"Error Message: {str(e)}")
            raise ValueError(f"Template validation failed: {str(e)}")
        except Exception as e:
            self.logger.error("="*50)
            self.logger.error("NO-CODE TEMPLATES CONNECTOR - Template Ingestion Failed - Unexpected Error")
            self.logger.error("="*50)
            self.logger.error(f"Error Type: {type(e).__name__}")
            self.logger.error(f"Error Message: {str(e)}")
            self.logger.error(f"Template Name: {template.name}")
            self.logger.error(f"Endpoint: {self.endpoint}")
            raise Exception(f"Unexpected error occurred: {str(e)}")


class TaxonomyModel(BaseModel):
    department: str
    team_task_category: str
    type_category: str


class TargetAudiencePromptModel(BaseModel):
    expertise_level: str
    job_roles: List[str]


class KPIBenefitsModel(BaseModel):
    estimated_time_saving: Optional[str] = None
    efficiency_gain_percentage: Optional[int] = None
    cost_reduction: Optional[str] = None
    quality_improvement_metric: Optional[str] = None


class PreMadePrompt(BaseModel):
    name: str
    prompt_body: str
    placeholders: List[str]
    associated_tool: str
    concrete_tasks: List[str]
    taxonomy: TaxonomyModel
    target_audience: TargetAudiencePromptModel
    kpi_benefits: KPIBenefitsModel
    model_compatibility: List[str]
    prompting_technique: str
    tags: List[str]


class PreMadePromptsClient:
    def __init__(self, base_url: str = settings.BACKEND_SERVICE_URL, api_key: Optional[str] = None):
        self.base_url = base_url
        self.endpoint = f"{self.base_url}/api/pre-made-prompts"
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Add console handler if not already added
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    async def post_pre_made_prompt(self, prompt: PreMadePrompt) -> dict:
        """
        Add a new pre-made prompt to the external service.
        
        Args:
            prompt: PreMadePrompt object containing prompt information
            
        Returns:
            dict: Response from the API
            
        Raises:
            httpx.HTTPStatusError: If the API request fails with an HTTP error
            httpx.RequestError: If the request fails due to network issues
            ValueError: If the prompt validation fails
            Exception: For other unexpected errors
        """


        self.logger.info("="*50)
        self.logger.info("PRE-MADE PROMPTS CONNECTOR - Starting Prompt Ingestion")
        self.logger.info("="*50)
        self.logger.info(f"Prompt Name: {prompt.name}")
        self.logger.info(f"Endpoint: {self.endpoint}")
        
        try:
            # Validate prompt before making request
            prompt_dict = prompt.model_dump(exclude_none=True)
            self.logger.debug("Prompt Data Details:")
            self.logger.debug(f"- Associated Tool: {prompt_dict.get('associated_tool')}")
            self.logger.debug(f"- Prompting Technique: {prompt_dict.get('prompting_technique')}")
            self.logger.debug(f"- Taxonomy: Department={prompt_dict.get('taxonomy', {}).get('department')}, Team Task Category={prompt_dict.get('taxonomy', {}).get('team_task_category')}, Type Category={prompt_dict.get('taxonomy', {}).get('type_category')}")
            self.logger.debug(f"- Concrete Tasks: {', '.join(prompt_dict.get('concrete_tasks', []))}")
            
            def serialize_types(obj):
                if isinstance(obj, dict):
                    return {k: serialize_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [serialize_types(i) for i in obj]
                elif isinstance(obj, HttpUrl):
                    return str(obj)
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                elif hasattr(obj, '__str__') and not isinstance(obj, (str, int, float, bool, type(None))):
                    # Convert any object with __str__ method to string
                    return str(obj)
                return obj
            
            serialized_data = serialize_types(prompt_dict)
            
            async with httpx.AsyncClient() as client:
                try:
                    self.logger.info(f"Sending request to pre-made prompts service...")
                    
                    response = await client.post(
                        self.endpoint,
                        json=serialized_data,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    response_data = response.json()
                    
                    self.logger.info("="*50)
                    self.logger.info("PRE-MADE PROMPTS CONNECTOR - Prompt Successfully Added")
                    self.logger.info("="*50)
                    self.logger.info(f"Prompt '{prompt.name}' successfully stored in global service")
                    self.logger.debug("Storage Details:")
                    self.logger.debug(f"- Response: {json.dumps(response_data, indent=2)}")
                    self.logger.debug(f"- Status Code: {response.status_code}")
                    self.logger.debug(f"- Headers: {dict(response.headers)}")
                    
                    return response_data
                    
                except httpx.HTTPStatusError as e:
                    self.logger.error("="*50)
                    self.logger.error("PRE-MADE PROMPTS CONNECTOR - Prompt Ingestion Failed - HTTP Error")
                    self.logger.error("="*50)
                    self.logger.error(f"Status Code: {e.response.status_code}")
                    self.logger.error(f"Response Text: {e.response.text}")
                    self.logger.error(f"Request URL: {e.request.url}")
                    self.logger.error(f"Request Headers: {dict(e.request.headers)}")
                    raise
                except httpx.RequestError as e:
                    self.logger.error("="*50)
                    self.logger.error("PRE-MADE PROMPTS CONNECTOR - Prompt Ingestion Failed - Network Error")
                    self.logger.error("="*50)
                    self.logger.error(f"Error Type: {type(e).__name__}")
                    self.logger.error(f"Error Message: {str(e)}")
                    self.logger.error(f"Request URL: {self.endpoint}")
                    raise
                    
        except ValueError as e:
            self.logger.error("="*50)
            self.logger.error("PRE-MADE PROMPTS CONNECTOR - Prompt Ingestion Failed - Validation Error")
            self.logger.error("="*50)
            self.logger.error(f"Error Message: {str(e)}")
            raise ValueError(f"Prompt validation failed: {str(e)}")
        except Exception as e:
            self.logger.error("="*50)
            self.logger.error("PRE-MADE PROMPTS CONNECTOR - Prompt Ingestion Failed - Unexpected Error")
            self.logger.error("="*50)
            self.logger.error(f"Error Type: {type(e).__name__}")
            self.logger.error(f"Error Message: {str(e)}")
            self.logger.error(f"Prompt Name: {prompt.name}")
            self.logger.error(f"Endpoint: {self.endpoint}")
            raise Exception(f"Unexpected error occurred: {str(e)}")