from typing import Dict, Any, Optional
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


def validate_tenant_access(tenant_id: str, current_user: Dict[str, Any]) -> None:
    """
    Validate that the current user has access to the specified tenant.
    
    Args:
        tenant_id: The tenant ID to validate access for
        current_user: The current authenticated user
        
    Raises:
        HTTPException: If the user doesn't have access to the tenant
    """
    user_tenant_id = current_user.get("tenant_id", "default_tenant")
    
    # Check if the user is accessing their own tenant
    if tenant_id != user_tenant_id:
        logger.warning(
            f"User {current_user.get('username')} attempted to access tenant {tenant_id} "
            f"but belongs to tenant {user_tenant_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to access this tenant's data"
        )
    
    logger.debug(f"Tenant access validated for user {current_user.get('username')} and tenant {tenant_id}")


def ensure_tenant_isolation(data: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
    """
    Ensure tenant isolation by adding or validating tenant_id in data.
    
    Args:
        data: The data to ensure tenant isolation for
        tenant_id: The tenant ID to ensure in the data
        
    Returns:
        The data with tenant_id ensured
    """
    # If data already has a tenant_id, validate it matches
    if "tenant_id" in data and data["tenant_id"] != tenant_id:
        logger.warning(
            f"Data contains tenant_id {data['tenant_id']} but expected {tenant_id}. "
            "Overriding with expected tenant_id for security."
        )
    
    # Ensure the correct tenant_id is set
    data["tenant_id"] = tenant_id
    
    return data


def validate_metadata(metadata: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
    """
    Validate and ensure tenant isolation in metadata.
    
    Args:
        metadata: The metadata to validate
        tenant_id: The tenant ID to ensure in the metadata
        
    Returns:
        The validated metadata with tenant_id ensured
    """
    # Ensure tenant_id is in metadata
    metadata = ensure_tenant_isolation(metadata, tenant_id)
    
    # Add validation timestamp if not present
    if "validated_at" not in metadata:
        from datetime import datetime, timezone
        metadata["validated_at"] = datetime.now(timezone.utc).isoformat()
    
    return metadata