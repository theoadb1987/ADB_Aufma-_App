"""
Service container for dependency injection.
"""
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Dict, Any, Type, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class ServiceContainer:
    """Container for service dependency injection."""
    
    def __init__(self):
        """Initialize an empty service container."""
        self._services = {}
        logger.info("ServiceContainer initialized")
    
    def register(self, service_type: Type, instance: Any) -> None:
        """
        Register a service instance.
        
        Args:
            service_type: The type/class of the service
            instance: The service instance
        """
        service_name = service_type.__name__
        self._services[service_name] = instance
        logger.info(f"Registered service: {service_name}")
    
    def get(self, service_type: Type) -> Any:
        """
        Get a service instance by type.
        
        Args:
            service_type: The type/class of the service
            
        Returns:
            The service instance
            
        Raises:
            KeyError: If the service is not registered
        """
        service_name = service_type.__name__
        if service_name not in self._services:
            raise KeyError(f"Service not registered: {service_name}")
        
        return self._services[service_name]
    
    def has(self, service_type: Type) -> bool:
        """
        Check if a service is registered.
        
        Args:
            service_type: The type/class of the service
            
        Returns:
            True if the service is registered, False otherwise
        """
        service_name = service_type.__name__
        return service_name in self._services

# Create a singleton instance
container = ServiceContainer()
