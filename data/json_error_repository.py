"""
JSON Error Repository module for Java Peer Review Training System.

This module provides direct access to error data from JSON files,
eliminating the need for intermediate data transformation.
"""

import os
import json
import logging
import random
from typing import Dict, List, Any, Optional, Set, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JsonErrorRepository:
    """
    Repository for accessing Java error data directly from JSON files.
    
    This class handles loading, categorizing, and providing access to
    error data from build_errors.json and checkstyle_error.json files.
    """
    
    def __init__(self, build_errors_path: str = "build_errors.json",
                checkstyle_errors_path: str = "checkstyle_error.json"):
        """
        Initialize the JSON Error Repository.
        
        Args:
            build_errors_path: Path to the build errors JSON file
            checkstyle_errors_path: Path to the checkstyle errors JSON file
        """
        self.build_errors_path = build_errors_path
        self.checkstyle_errors_path = checkstyle_errors_path
        
        # Initialize data
        self.build_errors = {}
        self.checkstyle_errors = {}
        self.build_categories = []
        self.checkstyle_categories = []
        
        # Load error data from JSON files
        self.load_error_data()
    
    def load_error_data(self) -> bool:
        """
        Load error data from JSON files.
        
        Returns:
            True if both files are loaded successfully, False otherwise
        """
        build_loaded = self._load_build_errors()
        checkstyle_loaded = self._load_checkstyle_errors()
        
        return build_loaded and checkstyle_loaded
    
    def _load_build_errors(self) -> bool:
        """
        Load build errors from JSON file.
        
        Returns:
            True if file is loaded successfully, False otherwise
        """
        try:
            # Try different paths to find the build errors file
            file_paths = self._get_potential_file_paths(self.build_errors_path)
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        self.build_errors = json.load(file)
                        self.build_categories = list(self.build_errors.keys())
                        logger.info(f"Loaded build errors from {file_path} with {len(self.build_categories)} categories")
                        return True
            
            logger.warning(f"Could not find build errors file: {self.build_errors_path}")
            return False
            
        except Exception as e:
            logger.error(f"Error loading build errors: {str(e)}")
            return False
    
    def _load_checkstyle_errors(self) -> bool:
        """
        Load checkstyle errors from JSON file.
        
        Returns:
            True if file is loaded successfully, False otherwise
        """
        try:
            # Try different paths to find the checkstyle errors file
            file_paths = self._get_potential_file_paths(self.checkstyle_errors_path)
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        self.checkstyle_errors = json.load(file)
                        self.checkstyle_categories = list(self.checkstyle_errors.keys())
                        logger.info(f"Loaded checkstyle errors from {file_path} with {len(self.checkstyle_categories)} categories")
                        return True
            
            logger.warning(f"Could not find checkstyle errors file: {self.checkstyle_errors_path}")
            return False
            
        except Exception as e:
            logger.error(f"Error loading checkstyle errors: {str(e)}")
            return False
    
    def _get_potential_file_paths(self, file_name: str) -> List[str]:
        """
        Get potential file paths to look for the error files.
        
        Args:
            file_name: Base file name to search for
            
        Returns:
            List of potential file paths
        """
        # Get the current directory
        current_dir = os.path.dirname(os.path.realpath(__file__))
        
        # Get the parent directory (project root)
        parent_dir = os.path.dirname(current_dir)
        
        # Try various potential locations
        return [
            file_name,  # Direct file name (if it's in the working directory)
            os.path.join(current_dir, file_name),  # In the same directory as this file
            os.path.join(parent_dir, file_name),  # In the parent directory (project root)
            os.path.join(parent_dir, "data", file_name),  # In a data subdirectory
            os.path.join(parent_dir, "resources", file_name),  # In a resources subdirectory
            os.path.join(parent_dir, "assets", file_name)  # In an assets subdirectory
        ]
    
    def get_all_categories(self) -> Dict[str, List[str]]:
        """
        Get all error categories.
        
        Returns:
            Dictionary with 'build' and 'checkstyle' categories
        """
        return {
            "build": self.build_categories,
            "checkstyle": self.checkstyle_categories
        }
    
    def get_category_errors(self, category_type: str, category_name: str) -> List[Dict[str, str]]:
        """
        Get errors for a specific category.
        
        Args:
            category_type: Type of category ('build' or 'checkstyle')
            category_name: Name of the category
            
        Returns:
            List of error dictionaries for the category
        """
        if category_type == "build" and category_name in self.build_errors:
            return self.build_errors[category_name]
        elif category_type == "checkstyle" and category_name in self.checkstyle_errors:
            return self.checkstyle_errors[category_name]
        return []
    
    def get_errors_by_categories(self, selected_categories: Dict[str, List[str]]) -> Dict[str, List[Dict[str, str]]]:
        """
        Get errors for selected categories.
        
        Args:
            selected_categories: Dictionary with 'build' and 'checkstyle' keys,
                               each containing a list of selected categories
            
        Returns:
            Dictionary with selected errors by category type
        """
        selected_errors = {
            "build": [],
            "checkstyle": []
        }
        
        # Get build errors
        if "build" in selected_categories:
            for category in selected_categories["build"]:
                if category in self.build_errors:
                    selected_errors["build"].extend(self.build_errors[category])
        
        # Get checkstyle errors
        if "checkstyle" in selected_categories:
            for category in selected_categories["checkstyle"]:
                if category in self.checkstyle_errors:
                    selected_errors["checkstyle"].extend(self.checkstyle_errors[category])
        
        return selected_errors
    
    def get_error_details(self, error_type: str, error_name: str) -> Optional[Dict[str, str]]:
        """
        Get details for a specific error.
        
        Args:
            error_type: Type of error ('build' or 'checkstyle')
            error_name: Name of the error
            
        Returns:
            Error details dictionary or None if not found
        """
        if error_type == "build":
            for category in self.build_errors:
                for error in self.build_errors[category]:
                    if error.get("error_name") == error_name:
                        return error
        elif error_type == "checkstyle":
            for category in self.checkstyle_errors:
                for error in self.checkstyle_errors[category]:
                    if error.get("check_name") == error_name:
                        return error
        return None
    
    def get_random_errors_by_categories(self, selected_categories: Dict[str, List[str]], 
                                  count: int = 4) -> List[Dict[str, Any]]:
        """
        Get random errors from selected categories.
        
        Args:
            selected_categories: Dictionary with 'build' and 'checkstyle' keys,
                            each containing a list of selected categories
            count: Number of errors to select
            
        Returns:
            List of selected errors with type and category information
        """
        all_errors = []
        build_categories = selected_categories.get("build", [])
        checkstyle_categories = selected_categories.get("checkstyle", [])
        
        # Build errors
        for category in build_categories:
            if category in self.build_errors:
                for error in self.build_errors[category]:
                    all_errors.append({
                        "type": "build",
                        "category": category,
                        "name": error["error_name"],
                        "description": error["description"],
                        "implementation_guide": error.get("implementation_guide", "")
                    })
        
        # Checkstyle errors
        for category in checkstyle_categories:
            if category in self.checkstyle_errors:
                for error in self.checkstyle_errors[category]:
                    all_errors.append({
                        "type": "checkstyle",
                        "category": category,
                        "name": error["check_name"],
                        "description": error["description"],
                        "implementation_guide": error.get("implementation_guide", "")
                    })
        
        # Select random errors
        if all_errors:
            # If we have fewer errors than requested, return all
            if len(all_errors) <= count:
                return all_errors
            
            # Otherwise select random errors
            return random.sample(all_errors, count)
        
        return []
    
    def get_errors_for_llm(self, 
                     selected_categories: Dict[str, List[str]] = None, 
                     specific_errors: List[Dict[str, Any]] = None,
                     count: int = 4, 
                     difficulty: str = "medium") -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Get errors suitable for sending to the LLM for code generation.
        Can use either category-based selection or specific errors.
        
        Args:
            selected_categories: Dictionary with selected error categories
            specific_errors: List of specific errors to include
            count: Number of errors to select if using categories
            difficulty: Difficulty level to adjust error count
            
        Returns:
            Tuple of (list of error objects, list of problem descriptions)
        """
        # Adjust count based on difficulty
        error_counts = {
            "easy": max(2, count - 2),
            "medium": count,
            "hard": count + 2
        }
        adjusted_count = error_counts.get(difficulty.lower(), count)
        
        # If specific errors are provided, use those
        if specific_errors and len(specific_errors) > 0:
            selected_errors = specific_errors
            
            # Format problem descriptions
            problem_descriptions = []
            for error in selected_errors:
                error_type = error.get("type", "Unknown")
                name = error.get("name", "Unknown")
                description = error.get("description", "")
                category = error.get("category", "")
                
                # Add implementation guide if available
                implementation_guide = self._get_implementation_guide(error_type, name, category)
                if implementation_guide:
                    error["implementation_guide"] = implementation_guide
                
                if error_type == "build":
                    problem_descriptions.append(f"Build Error - {name}: {description} (Category: {category})")
                else:  # checkstyle
                    problem_descriptions.append(f"Checkstyle Error - {name}: {description} (Category: {category})")
            
            return selected_errors, problem_descriptions
        
        # Otherwise use category-based selection
        elif selected_categories:
            # Check if any categories are actually selected
            build_categories = selected_categories.get("build", [])
            checkstyle_categories = selected_categories.get("checkstyle", [])
            
            if not build_categories and not checkstyle_categories:
                # Use default categories if none specified
                selected_categories = {
                    "build": ["CompileTimeErrors", "RuntimeErrors", "LogicalErrors"],
                    "checkstyle": ["NamingConventionChecks", "WhitespaceAndFormattingChecks"]
                }
            
            # Collect errors from each selected category
            all_errors = []
            
            # Build errors - randomly select from each category
            for category in selected_categories.get("build", []):
                if category in self.build_errors:
                    category_errors = self.build_errors[category]
                    # For each selected category, randomly select 1-2 errors
                    num_to_select = min(len(category_errors), random.randint(1, 2))
                    if num_to_select > 0:
                        selected_from_category = random.sample(category_errors, num_to_select)
                        for error in selected_from_category:
                            all_errors.append({
                                "type": "build",
                                "category": category,
                                "name": error["error_name"],
                                "description": error["description"],
                                "implementation_guide": error.get("implementation_guide", "")
                            })
            
            # Checkstyle errors - randomly select from each category
            for category in selected_categories.get("checkstyle", []):
                if category in self.checkstyle_errors:
                    category_errors = self.checkstyle_errors[category]
                    # For each selected category, randomly select 1-2 errors
                    num_to_select = min(len(category_errors), random.randint(1, 2))
                    if num_to_select > 0:
                        selected_from_category = random.sample(category_errors, num_to_select)
                        for error in selected_from_category:
                            all_errors.append({
                                "type": "checkstyle",
                                "category": category,
                                "name": error["check_name"],
                                "description": error["description"],
                                "implementation_guide": error.get("implementation_guide", "")
                            })
            
            # If we have more errors than needed, randomly select the required number
            if len(all_errors) > adjusted_count:
                selected_errors = random.sample(all_errors, adjusted_count)
            else:
                selected_errors = all_errors
            
            # Format problem descriptions
            problem_descriptions = []
            for error in selected_errors:
                error_type = error.get("type", "Unknown")
                name = error.get("name", "Unknown")
                description = error.get("description", "")
                category = error.get("category", "")
                
                if error_type == "build":
                    problem_descriptions.append(f"Build Error - {name}: {description} (Category: {category})")
                else:  # checkstyle
                    problem_descriptions.append(f"Checkstyle Error - {name}: {description} (Category: {category})")
            
            return selected_errors, problem_descriptions
        
        # If no selection method was provided, return empty lists
        return [], []
    
    def _get_implementation_guide(self, error_type: str, error_name: str, category: str) -> Optional[str]:
        """
        Get implementation guide for a specific error.
        
        Args:
            error_type: Type of error ('build' or 'checkstyle')
            error_name: Name of the error
            category: Category of the error
            
        Returns:
            Implementation guide string or None if not found
        """
        if error_type == "build":
            if category in self.build_errors:
                for error in self.build_errors[category]:
                    if error.get("error_name") == error_name:
                        return error.get("implementation_guide")
        elif error_type == "checkstyle":
            if category in self.checkstyle_errors:
                for error in self.checkstyle_errors[category]:
                    if error.get("check_name") == error_name:
                        return error.get("implementation_guide")
        return None

    def search_errors(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for errors containing the search term.
        
        Args:
            search_term: Term to search for in error names and descriptions
            
        Returns:
            List of matching errors with type and category information
        """
        results = []
        search_term = search_term.lower()
        
        # Search build errors
        for category in self.build_errors:
            for error in self.build_errors[category]:
                name = error.get("error_name", "").lower()
                description = error.get("description", "").lower()
                
                if search_term in name or search_term in description:
                    results.append({
                        "type": "build",
                        "category": category,
                        "name": error["error_name"],
                        "description": error["description"]
                    })
        
        # Search checkstyle errors
        for category in self.checkstyle_errors:
            for error in self.checkstyle_errors[category]:
                name = error.get("check_name", "").lower()
                description = error.get("description", "").lower()
                
                if search_term in name or search_term in description:
                    results.append({
                        "type": "checkstyle",
                        "category": category,
                        "name": error["check_name"],
                        "description": error["description"]
                    })
        
        return results
    
    def get_error_by_name(self, error_type: str, error_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific error by name.
        
        Args:
            error_type: Type of error ('build' or 'checkstyle')
            error_name: Name of the error
            
        Returns:
            Error dictionary with added type and category, or None if not found
        """
        if error_type == "build":
            for category, errors in self.build_errors.items():
                for error in errors:
                    if error.get("error_name") == error_name:
                        return {
                            "type": "build",
                            "category": category,
                            "name": error["error_name"],
                            "description": error["description"]
                        }
        elif error_type == "checkstyle":
            for category, errors in self.checkstyle_errors.items():
                for error in errors:
                    if error.get("check_name") == error_name:
                        return {
                            "type": "checkstyle",
                            "category": category,
                            "name": error["check_name"],
                            "description": error["description"]
                        }
        return None