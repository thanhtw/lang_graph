"""
Model Manager UI module for Java Peer Review Training System.

This module provides the ModelManagerUI class for managing Ollama models
through the web interface.
"""

import streamlit as st
import logging
import os
import time
from typing import List, Dict, Any, Optional, Tuple, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelManagerUI:
    """
    UI Component for managing Ollama models.
    
    This class handles displaying available models, pulling new models,
    and selecting models for different roles in the application.
    """
    
    def __init__(self, llm_manager):
        """
        Initialize the ModelManagerUI component.
        
        Args:
            llm_manager: LLMManager instance for interacting with Ollama
        """
        self.llm_manager = llm_manager
        
        # Initialize session state for model selections
        if "model_selections" not in st.session_state:
            # Initialize with environment variables if available
            st.session_state.model_selections = {
                "generative": os.getenv("GENERATIVE_MODEL", llm_manager.default_model),
                "review": os.getenv("REVIEW_MODEL", llm_manager.default_model),
                "summary": os.getenv("SUMMARY_MODEL", llm_manager.default_model),
                "compare": os.getenv("COMPARE_MODEL", llm_manager.default_model)
            }
            
        # Initialize session state for model operations
        if "model_operations" not in st.session_state:
            st.session_state.model_operations = {
                "pulling": False,
                "current_pull": None,
                "pull_progress": 0,
                "last_pulled": None,
                "error": None
            }
    
    def render_model_manager(self) -> Dict[str, str]:
        """
        Render the Ollama model management UI.
        
        Returns:
            Dictionary with selected models for each role
        """
        st.header("Ollama Model Management")
        
        # Check connection to Ollama
        connection_status, message = self.llm_manager.check_ollama_connection()
        
        if not connection_status:
            st.error(f"Cannot connect to Ollama: {message}")
            
            with st.expander("Troubleshooting"):
                st.markdown("""
                1. **Check if Ollama is running:**
                   ```bash
                   curl http://localhost:11434/api/tags
                   ```
                   
                2. **Make sure the Ollama service is started:**
                   - On Linux/Mac: `ollama serve`
                   - On Windows: Start the Ollama application
                   
                3. **Check the Ollama URL in .env file:**
                   - Default is http://localhost:11434
                """)
            return st.session_state.model_selections
        
        # Get available models
        available_models = self.llm_manager.get_available_models()
        
        # Display available models and allow pulling new ones
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Available Models")
            
            if not available_models:
                st.info("No models found. Pull a model to get started.")
            else:
                # Create a filtered list of models to display
                display_models = []
                for model in available_models:
                    display_models.append({
                        "name": model["name"],
                        "id": model["id"],
                        "pulled": model["pulled"],
                        "description": model["description"]
                    })
                
                # Generate a table of available models
                self._render_model_table(display_models)
        
        with col2:
            st.subheader("Pull New Model")
            
            # When a model is being pulled, show progress
            if st.session_state.model_operations["pulling"]:
                model_name = st.session_state.model_operations["current_pull"]
                st.info(f"Pulling model: {model_name}")
                progress_bar = st.progress(st.session_state.model_operations["pull_progress"])
                
                if st.button("Cancel"):
                    st.session_state.model_operations["pulling"] = False
                    st.session_state.model_operations["current_pull"] = None
                    st.session_state.model_operations["pull_progress"] = 0
                    st.rerun()
            else:
                # Model pull form
                with st.form("pull_model_form"):
                    model_id = st.text_input(
                        "Model ID", 
                        placeholder="e.g., llama3:8b, phi3:mini, gemma:2b",
                        help="Enter the ID of the model you want to pull from Ollama"
                    )
                    
                    submitted = st.form_submit_button("Pull Model")
                    
                    if submitted and model_id:
                        st.session_state.model_operations["pulling"] = True
                        st.session_state.model_operations["current_pull"] = model_id
                        st.session_state.model_operations["pull_progress"] = 0
                        
                        # Start a background job to pull the model
                        def pull_model():
                            try:
                                success = self.llm_manager.download_ollama_model(model_id)
                                
                                if success:
                                    st.session_state.model_operations["last_pulled"] = model_id
                                else:
                                    st.session_state.model_operations["error"] = f"Failed to pull model: {model_id}"
                            except Exception as e:
                                st.session_state.model_operations["error"] = f"Error: {str(e)}"
                            finally:
                                st.session_state.model_operations["pulling"] = False
                                st.session_state.model_operations["current_pull"] = None
                                st.session_state.model_operations["pull_progress"] = 0
                        
                        # We can't actually run a background job in Streamlit, so we'll fake it with progress
                        # In a real app, you'd want to use something like BackgroundProcess from streamlit-extras
                        st.rerun()
            
            # Show last pulled model
            if st.session_state.model_operations["last_pulled"]:
                st.success(f"Successfully pulled model: {st.session_state.model_operations['last_pulled']}")
            
            # Show error if any
            if st.session_state.model_operations["error"]:
                st.error(st.session_state.model_operations["error"])
                if st.button("Clear Error"):
                    st.session_state.model_operations["error"] = None
                    st.rerun()
        
        # Model selection for different roles
        st.subheader("Model Selection")
        
        # Get model options (only pulled models)
        model_options = [model["id"] for model in available_models if model["pulled"]]
        
        if not model_options:
            st.warning("No models are available. Please pull at least one model.")
        else:
            # Create columns for model selection
            col1, col2 = st.columns(2)
            
            with col1:
                # For code generation
                st.markdown("**Code Generation Model**")
                generative_model = st.selectbox(
                    "Model for generating code problems",
                    options=model_options,
                    index=model_options.index(st.session_state.model_selections["generative"]) 
                    if st.session_state.model_selections["generative"] in model_options else 0,
                    key="generative_model_select"
                )
                
                st.session_state.model_selections["generative"] = generative_model
                
                # For review analysis
                st.markdown("**Review Analysis Model**")
                review_model = st.selectbox(
                    "Model for analyzing student reviews",
                    options=model_options,
                    index=model_options.index(st.session_state.model_selections["review"]) 
                    if st.session_state.model_selections["review"] in model_options else 0,
                    key="review_model_select"
                )
                
                st.session_state.model_selections["review"] = review_model
            
            with col2:
                # For summary generation
                st.markdown("**Summary Generation Model**")
                summary_model = st.selectbox(
                    "Model for generating feedback summaries",
                    options=model_options,
                    index=model_options.index(st.session_state.model_selections["summary"]) 
                    if st.session_state.model_selections["summary"] in model_options else 0,
                    key="summary_model_select"
                )
                
                st.session_state.model_selections["summary"] = summary_model
                
                # For comparison
                st.markdown("**Comparison Model**")
                compare_model = st.selectbox(
                    "Model for comparing student reviews with actual issues",
                    options=model_options,
                    index=model_options.index(st.session_state.model_selections["compare"]) 
                    if st.session_state.model_selections["compare"] in model_options else 0,
                    key="compare_model_select"
                )
                
                st.session_state.model_selections["compare"] = compare_model
            
            # Advanced settings
            with st.expander("Advanced Settings", expanded=False):
                # Enable/disable reasoning mode
                reasoning_mode = st.checkbox(
                    "Enable Reasoning Mode",
                    value=os.getenv("REASONING_MODE", "false").lower() == "true",
                    help="When enabled, models will use step-by-step reasoning (may use more tokens)"
                )
                
                # Temperature settings
                st.subheader("Temperature Settings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    generative_temp = st.slider(
                        "Generation Temperature",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(os.getenv("GENERATIVE_TEMPERATURE", "0.7")),
                        step=0.1,
                        help="Higher temperature = more creative but less predictable"
                    )
                    
                    review_temp = st.slider(
                        "Review Temperature",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(os.getenv("REVIEW_TEMPERATURE", "0.7")),
                        step=0.1
                    )
                
                with col2:
                    summary_temp = st.slider(
                        "Summary Temperature",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(os.getenv("SUMMARY_TEMPERATURE", "0.7")),
                        step=0.1
                    )
                    
                    compare_temp = st.slider(
                        "Compare Temperature",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(os.getenv("COMPARE_TEMPERATURE", "0.7")),
                        step=0.1
                    )
                
                # Reasoning temperature
                reasoning_temp = st.slider(
                    "Reasoning Temperature",
                    min_value=0.0,
                    max_value=1.0,
                    value=float(os.getenv("REASONING_TEMPERATURE", "0.1")),
                    step=0.1,
                    help="Lower values give more predictable responses in reasoning mode"
                )
                
                # Save settings button
                if st.button("Save Settings to .env"):
                    # Update environment variables in memory
                    os.environ["GENERATIVE_MODEL"] = st.session_state.model_selections["generative"]
                    os.environ["REVIEW_MODEL"] = st.session_state.model_selections["review"]
                    os.environ["SUMMARY_MODEL"] = st.session_state.model_selections["summary"]
                    os.environ["COMPARE_MODEL"] = st.session_state.model_selections["compare"]
                    
                    os.environ["GENERATIVE_TEMPERATURE"] = str(generative_temp)
                    os.environ["REVIEW_TEMPERATURE"] = str(review_temp)
                    os.environ["SUMMARY_TEMPERATURE"] = str(summary_temp)
                    os.environ["COMPARE_TEMPERATURE"] = str(compare_temp)
                    
                    os.environ["REASONING_MODE"] = str(reasoning_mode).lower()
                    os.environ["REASONING_TEMPERATURE"] = str(reasoning_temp)
                    
                    # Update .env file (this is a simple implementation; a real app would use a more robust approach)
                    try:
                        env_path = ".env"
                        if os.path.exists(env_path):
                            # Read existing .env content
                            with open(env_path, "r") as f:
                                lines = f.readlines()
                            
                            # Update existing values or add new ones
                            env_vars = {
                                "GENERATIVE_MODEL": st.session_state.model_selections["generative"],
                                "REVIEW_MODEL": st.session_state.model_selections["review"],
                                "SUMMARY_MODEL": st.session_state.model_selections["summary"],
                                "COMPARE_MODEL": st.session_state.model_selections["compare"],
                                "GENERATIVE_TEMPERATURE": str(generative_temp),
                                "REVIEW_TEMPERATURE": str(review_temp),
                                "SUMMARY_TEMPERATURE": str(summary_temp),
                                "COMPARE_TEMPERATURE": str(compare_temp),
                                "REASONING_MODE": str(reasoning_mode).lower(),
                                "REASONING_TEMPERATURE": str(reasoning_temp)
                            }
                            
                            # Update existing variables
                            updated_lines = []
                            updated_vars = set()
                            
                            for line in lines:
                                updated = False
                                for var_name, var_value in env_vars.items():
                                    if line.startswith(f"{var_name}="):
                                        updated_lines.append(f"{var_name}={var_value}\n")
                                        updated_vars.add(var_name)
                                        updated = True
                                        break
                                
                                if not updated:
                                    updated_lines.append(line)
                            
                            # Add new variables that weren't updated
                            for var_name, var_value in env_vars.items():
                                if var_name not in updated_vars:
                                    updated_lines.append(f"{var_name}={var_value}\n")
                            
                            # Write the updated content back
                            with open(env_path, "w") as f:
                                f.writelines(updated_lines)
                            
                            st.success("Settings saved to .env file!")
                        else:
                            # Create a new .env file
                            with open(env_path, "w") as f:
                                f.write(f"OLLAMA_BASE_URL={self.llm_manager.ollama_base_url}\n")
                                f.write(f"DEFAULT_MODEL={self.llm_manager.default_model}\n")
                                f.write(f"GENERATIVE_MODEL={st.session_state.model_selections['generative']}\n")
                                f.write(f"REVIEW_MODEL={st.session_state.model_selections['review']}\n")
                                f.write(f"SUMMARY_MODEL={st.session_state.model_selections['summary']}\n")
                                f.write(f"COMPARE_MODEL={st.session_state.model_selections['compare']}\n")
                                f.write(f"GENERATIVE_TEMPERATURE={generative_temp}\n")
                                f.write(f"REVIEW_TEMPERATURE={review_temp}\n")
                                f.write(f"SUMMARY_TEMPERATURE={summary_temp}\n")
                                f.write(f"COMPARE_TEMPERATURE={compare_temp}\n")
                                f.write(f"REASONING_MODE={str(reasoning_mode).lower()}\n")
                                f.write(f"REASONING_TEMPERATURE={reasoning_temp}\n")
                            
                            st.success("Created new .env file with settings!")
                    except Exception as e:
                        st.error(f"Error saving settings: {str(e)}")
        
        # Return the current model selections
        return st.session_state.model_selections
    
    def _render_model_table(self, models: List[Dict[str, Any]]):
        """
        Render a table of available models with improved styling.
        
        Args:
            models: List of model dictionaries
        """
        # Add custom CSS for model cards
        st.markdown("""
            <style>
                .model-card {
                    background-color: white;
                    border-radius: 8px;
                    padding: 12px 15px;
                    margin-bottom: 12px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                    border-left: 4px solid #ccc;
                }
                .model-card:hover {
                    transform: translateY(-2px);
                }
                .model-card.available {
                    border-left-color: #4CAF50;
                }
                .model-card.not-available {
                    border-left-color: #9e9e9e;
                }
                .model-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                }
                .model-name {
                    font-size: 16px;
                    font-weight: 600;
                }
                .model-id {
                    color: #666;
                    font-size: 13px;
                    font-weight: normal;
                    margin-left: 5px;
                }
                .model-status {
                    font-size: 12px;
                    padding: 3px 10px;
                    border-radius: 12px;
                    font-weight: 500;
                }
                .status-available {
                    background-color: #e8f5e9;
                    color: #2e7d32;
                }
                .status-not-available {
                    background-color: #f5f5f5;
                    color: #616161;
                }
                .model-description {
                    font-size: 14px;
                    color: #333;
                    margin-bottom: 10px;
                    line-height: 1.4;
                }
                .model-button {
                    text-align: right;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Render each model as a card
        for model in models:
            # Determine status and styling
            if model["pulled"]:
                status_class = "available"
                status_badge_class = "status-available"
                status_text = "Available"
            else:
                status_class = "not-available"
                status_badge_class = "status-not-available"
                status_text = "Not pulled"
            
            # Create model card with better styling
            st.markdown(f"""
                <div class="model-card {status_class}">
                    <div class="model-header">
                        <div class="model-name">
                            {model["name"]} <span class="model-id">({model["id"]})</span>
                        </div>
                        <div class="model-status {status_badge_class}">
                            {status_text}
                        </div>
                    </div>
                    <div class="model-description">
                        {model["description"]}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Add pull button for models that aren't pulled
            # Using a separate button outside the HTML for better interaction
            if not model["pulled"]:
                col1, col2, col3 = st.columns([2, 2, 1])
                with col3:
                    if st.button(f"Pull Model", key=f"pull_{model['id']}"):
                        st.session_state.model_operations["pulling"] = True
                        st.session_state.model_operations["current_pull"] = model["id"]
                        st.session_state.model_operations["pull_progress"] = 0
                        st.rerun()