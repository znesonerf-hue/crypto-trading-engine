"""Model Versioning & Registry"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import pickle
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ModelRegistry:
    """Manage model versions and registry"""
    
    def __init__(self, registry_dir: str = "models/registry"):
        """
        Initialize model registry.
        
        Args:
            registry_dir: Directory for model registry
        """
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, List[Dict]] = {}
    
    def register_model(self, name: str, model: object, 
                      metadata: Dict = None) -> str:
        """
        Register a model version.
        
        Args:
            name: Model name
            model: Model object
            metadata: Model metadata
        
        Returns:
            Model version ID
        """
        if name not in self.models:
            self.models[name] = []
        
        version = len(self.models[name]) + 1
        version_id = f"{name}_v{version}"
        
        # Save model
        model_path = self.registry_dir / f"{version_id}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Save metadata
        if metadata is None:
            metadata = {}
        
        metadata['version_id'] = version_id
        metadata['timestamp'] = datetime.now().isoformat()
        metadata['model_path'] = str(model_path)
        
        metadata_path = self.registry_dir / f"{version_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.models[name].append(metadata)
        logger.info(f"Registered model: {version_id}")
        
        return version_id
    
    def load_model(self, version_id: str) -> object:
        """
        Load a model by version ID.
        
        Args:
            version_id: Model version ID
        
        Returns:
            Loaded model
        """
        model_path = self.registry_dir / f"{version_id}.pkl"
        
        if not model_path.exists():
            logger.error(f"Model not found: {version_id}")
            return None
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        logger.info(f"Loaded model: {version_id}")
        return model
    
    def get_latest_model(self, name: str) -> Optional[Dict]:
        """
        Get latest model version.
        
        Args:
            name: Model name
        
        Returns:
            Latest model metadata
        """
        if name in self.models and self.models[name]:
            return self.models[name][-1]
        return None
    
    def list_models(self, name: Optional[str] = None) -> List[Dict]:
        """
        List all registered models.
        
        Args:
            name: Filter by model name
        
        Returns:
            List of model metadata
        """
        if name:
            return self.models.get(name, [])
        
        all_models = []
        for models_list in self.models.values():
            all_models.extend(models_list)
        
        return all_models
