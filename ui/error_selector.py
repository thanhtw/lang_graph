"""
Error Selector UI module for Java Peer Review Training System.

This module provides the ErrorSelectorUI class for selecting Java error categories
to include in the generated code problems.
"""

import streamlit as st
import logging
import random
from typing import List, Dict, Any, Optional, Tuple, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorSelectorUI:
    """
    UI Component for selecting Java error categories.
    
    This class handles displaying and selecting Java error categories
    from both build errors and checkstyle errors.
    """
    
    def __init__(self):
        """Initialize the ErrorSelectorUI component with empty selections."""
        # Track selected categories - initialize with empty collections if not in session state
        if "selected_error_categories" not in st.session_state:
            st.session_state.selected_error_categories = {
                "build": [],
                "checkstyle": []
            }
        elif not isinstance(st.session_state.selected_error_categories, dict):
            # Fix if it's not a proper dictionary
            st.session_state.selected_error_categories = {
                "build": [],
                "checkstyle": []
            }
        elif "build" not in st.session_state.selected_error_categories or "checkstyle" not in st.session_state.selected_error_categories:
            # Make sure both build and checkstyle keys exist
            if "build" not in st.session_state.selected_error_categories:
                st.session_state.selected_error_categories["build"] = []
            if "checkstyle" not in st.session_state.selected_error_categories:
                st.session_state.selected_error_categories["checkstyle"] = []
        
        # Track error selection mode
        if "error_selection_mode" not in st.session_state:
            st.session_state.error_selection_mode = "standard"
        
        # Track expanded categories
        if "expanded_categories" not in st.session_state:
            st.session_state.expanded_categories = {}
            
        # Track selected specific errors - initialize as empty list
        if "selected_specific_errors" not in st.session_state:
            st.session_state.selected_specific_errors = []
        
        # Track problem areas - initialize as empty list
        if "problem_areas" not in st.session_state:
            st.session_state.problem_areas = []
        
        # Print initial state for debugging
        print("\n========== ERROR SELECTOR INITIALIZATION ==========")
        print(f"Error Selection Mode: {st.session_state.error_selection_mode}")
        print(f"Problem Areas: {st.session_state.problem_areas}")
        print(f"Selected Error Categories: {st.session_state.selected_error_categories}")
        print(f"Selected Specific Errors: {len(st.session_state.selected_specific_errors)}")
        print("====================================================")
    
    def render_category_selection(self, all_categories: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Render the error category selection UI for advanced mode with enhanced debugging.
        
        Args:
            all_categories: Dictionary with 'build' and 'checkstyle' categories
            
        Returns:
            Dictionary with selected categories
        """
        st.subheader("Select Specific Error Categories")
        
        # Add help text explaining how this mode works
        st.info("""
        **Advanced Mode**: Select specific error categories to include in the generated code. 
        When you select a category, the system will randomly choose errors from that category 
        to include in the generated code.
        """)
        
        build_categories = all_categories.get("build", [])
        checkstyle_categories = all_categories.get("checkstyle", [])
        
        # Ensure the session state structure is correct
        if "selected_error_categories" not in st.session_state:
            st.session_state.selected_error_categories = {"build": [], "checkstyle": []}
        if "build" not in st.session_state.selected_error_categories:
            st.session_state.selected_error_categories["build"] = []
        if "checkstyle" not in st.session_state.selected_error_categories:
            st.session_state.selected_error_categories["checkstyle"] = []
        
        # Build errors section
        st.markdown("<div class='error-type-header'>Build Errors</div>", unsafe_allow_html=True)
        
        # Create a multi-column layout for build errors
        build_cols = st.columns(2)
        
        # Get the current selection state from session
        current_build_selections = st.session_state.selected_error_categories.get("build", [])
        
        # Split the build categories into two columns
        half_length = len(build_categories) // 2
        for i, col in enumerate(build_cols):
            start_idx = i * half_length
            end_idx = start_idx + half_length if i == 0 else len(build_categories)
            
            with col:
                for category in build_categories[start_idx:end_idx]:
                    # Create a unique key for this category
                    category_key = f"build_{category}"
                    
                    # Check if category is already selected from session state
                    is_selected = category in current_build_selections
                    
                    # Create the checkbox
                    selected = st.checkbox(
                        category,
                        key=category_key,
                        value=is_selected
                    )
                    
                    # Update selection state based on checkbox
                    if selected:
                        if category not in current_build_selections:
                            current_build_selections.append(category)
                    else:
                        if category in current_build_selections:
                            current_build_selections.remove(category)
        
        # Update build selections in session state
        st.session_state.selected_error_categories["build"] = current_build_selections
        
        # Checkstyle errors section
        st.markdown("<div class='error-type-header'>Checkstyle Errors</div>", unsafe_allow_html=True)
        
        # Create a multi-column layout for checkstyle errors
        checkstyle_cols = st.columns(2)
        
        # Get the current selection state from session
        current_checkstyle_selections = st.session_state.selected_error_categories.get("checkstyle", [])
        
        # Split the checkstyle categories into two columns
        half_length = len(checkstyle_categories) // 2
        for i, col in enumerate(checkstyle_cols):
            start_idx = i * half_length
            end_idx = start_idx + half_length if i == 0 else len(checkstyle_categories)
            
            with col:
                for category in checkstyle_categories[start_idx:end_idx]:
                    # Create a unique key for this category
                    category_key = f"checkstyle_{category}"
                    
                    # Check if category is already selected from session state
                    is_selected = category in current_checkstyle_selections
                    
                    # Create the checkbox
                    selected = st.checkbox(
                        category,
                        key=category_key,
                        value=is_selected
                    )
                    
                    # Update selection state based on checkbox
                    if selected:
                        if category not in current_checkstyle_selections:
                            current_checkstyle_selections.append(category)
                    else:
                        if category in current_checkstyle_selections:
                            current_checkstyle_selections.remove(category)
        
        # Update checkstyle selections in session state
        st.session_state.selected_error_categories["checkstyle"] = current_checkstyle_selections
        
        # Selection summary
        build_selected = st.session_state.selected_error_categories.get("build", [])
        checkstyle_selected = st.session_state.selected_error_categories.get("checkstyle", [])
        
        st.write("### Selected Categories")
        if not build_selected and not checkstyle_selected:
            st.warning("No categories selected. You must select at least one category to generate code.")
        
        if build_selected:
            st.write("Build Error Categories:")
            for category in build_selected:
                st.markdown(f"<div class='error-category'>{category}</div>", unsafe_allow_html=True)
        
        if checkstyle_selected:
            st.write("Checkstyle Error Categories:")
            for category in checkstyle_selected:
                st.markdown(f"<div class='error-category'>{category}</div>", unsafe_allow_html=True)
        
        # Enhanced debug output for advanced mode
        print("\n========== ADVANCED MODE SELECTION ==========")
        print(f"Build Categories: {build_selected}")
        print(f"Checkstyle Categories: {checkstyle_selected}")
        
        # If any categories are selected, show potential errors in each category
        if build_selected or checkstyle_selected:
            print("\n--- POTENTIAL ERRORS BY CATEGORY ---")
            
            # For build categories
            for category in build_selected:
                print(f"Build Category: {category}")
                # Get sample errors from this category if available
                try:
                    from data.json_error_repository import JsonErrorRepository
                    repo = JsonErrorRepository()
                    errors = repo.get_category_errors("build", category)
                    if errors:
                        print(f"  Sample errors (max 3):")
                        for i, error in enumerate(errors[:3]):
                            print(f"    {i+1}. {error.get('error_name', 'Unknown')}: {error.get('description', '')[:50]}..." 
                                if len(error.get('description', '')) > 50 else error.get('description', ''))
                except Exception as e:
                    print(f"  Error retrieving category info: {str(e)}")
            
            # For checkstyle categories
            for category in checkstyle_selected:
                print(f"Checkstyle Category: {category}")
                # Get sample errors from this category if available
                try:
                    from data.json_error_repository import JsonErrorRepository
                    repo = JsonErrorRepository()
                    errors = repo.get_category_errors("checkstyle", category)
                    if errors:
                        print(f"  Sample errors (max 3):")
                        for i, error in enumerate(errors[:3]):
                            print(f"    {i+1}. {error.get('check_name', 'Unknown')}: {error.get('description', '')[:50]}..." 
                                if len(error.get('description', '')) > 50 else error.get('description', ''))
                except Exception as e:
                    print(f"  Error retrieving category info: {str(e)}")
        
        print("=============================================")
        
        return st.session_state.selected_error_categories
    
    def render_specific_error_selection(self, error_repository) -> List[Dict[str, Any]]:
        """
        Render UI for selecting specific errors to include in generated code.
        
        Args:
            error_repository: Repository for accessing Java error data
            
        Returns:
            List of selected specific errors
        """
        st.subheader("Select Specific Errors")
        
        # Get all categories
        all_categories = error_repository.get_all_categories()
        build_categories = all_categories.get("build", [])
        checkstyle_categories = all_categories.get("checkstyle", [])
        
        # Selection of category type
        error_type = st.radio(
            "Error Type",
            ["Build Errors", "Checkstyle Errors"],
            horizontal=True
        )

        # Filter for searching errors
        search_term = st.text_input("Search Errors", "")
        
        # Container for selected errors
        if "selected_specific_errors" not in st.session_state:
            st.session_state.selected_specific_errors = []
            
        # Display errors based on type
        if error_type == "Build Errors":
            self._display_build_errors(error_repository, build_categories, search_term)
        else:
            self._display_checkstyle_errors(error_repository, checkstyle_categories, search_term)
            
        # Show selected errors
        st.subheader("Selected Errors")
        
        if not st.session_state.selected_specific_errors:
            st.info("No specific errors selected. Random errors will be used based on categories.")
        else:
            for idx, error in enumerate(st.session_state.selected_specific_errors):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{error['type']} - {error['name']}**")
                    st.markdown(f"*{error['description']}*")
                with col2:
                    if st.button("Remove", key=f"remove_{idx}"):
                        st.session_state.selected_specific_errors.pop(idx)
                        st.rerun()
        
        return st.session_state.selected_specific_errors
        
    def _display_build_errors(self, error_repository, categories, search_term=""):
        """Display build errors with filtering"""
        for category in categories:
            # Get errors for this category
            errors = error_repository.get_category_errors("build", category)
            
            # Filter errors if search term is provided
            if search_term:
                errors = [e for e in errors if search_term.lower() in e.get("error_name", "").lower() 
                          or search_term.lower() in e.get("description", "").lower()]
                
            if not errors:
                continue
                
            # Display category with expander
            with st.expander(f"{category} ({len(errors)} errors)"):
                for error in errors:
                    error_name = error.get("error_name", "Unknown")
                    description = error.get("description", "")
                    
                    # Check if already selected
                    is_selected = any(
                        e["type"] == "build" and e["name"] == error_name 
                        for e in st.session_state.selected_specific_errors
                    )
                    
                    # Add select button
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"**{error_name}**")
                        st.markdown(f"*{description}*")
                    with col2:
                        if not is_selected:
                            if st.button("Select", key=f"build_{category}_{error_name}"):
                                st.session_state.selected_specific_errors.append({
                                    "type": "build",
                                    "category": category,
                                    "name": error_name,
                                    "description": description
                                })
                                st.rerun()
                        else:
                            st.success("Selected")
                    
                    st.markdown("---")
    
    def _display_checkstyle_errors(self, error_repository, categories, search_term=""):
        """Display checkstyle errors with filtering"""
        for category in categories:
            # Get errors for this category
            errors = error_repository.get_category_errors("checkstyle", category)
            
            # Filter errors if search term is provided
            if search_term:
                errors = [e for e in errors if search_term.lower() in e.get("check_name", "").lower() 
                          or search_term.lower() in e.get("description", "").lower()]
                
            if not errors:
                continue
                
            # Display category with expander
            with st.expander(f"{category} ({len(errors)} errors)"):
                for error in errors:
                    error_name = error.get("check_name", "Unknown")
                    description = error.get("description", "")
                    
                    # Check if already selected
                    is_selected = any(
                        e["type"] == "checkstyle" and e["name"] == error_name 
                        for e in st.session_state.selected_specific_errors
                    )
                    
                    # Add select button
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"**{error_name}**")
                        st.markdown(f"*{description}*")
                    with col2:
                        if not is_selected:
                            if st.button("Select", key=f"checkstyle_{category}_{error_name}"):
                                st.session_state.selected_specific_errors.append({
                                    "type": "checkstyle",
                                    "category": category,
                                    "name": error_name,
                                    "description": description
                                })
                                st.rerun()
                        else:
                            st.success("Selected")
                    
                    st.markdown("---")
        
    def render_mode_selector(self) -> str:
        """
        Render the mode selector UI with improved mode switching behavior.
        
        Returns:
            Selected mode ("standard", "advanced", or "specific")
        """
        st.markdown("#### Error Selection Mode")
        
        # Create a more descriptive selection with radio buttons
        mode_options = [
            "Standard: Select by problem areas (recommended)",
            "Advanced: Select by error categories",
            "Specific: Choose exact errors to include"
        ]
        
        # Convert session state to index
        current_mode = st.session_state.error_selection_mode
        current_index = 0
        if current_mode == "advanced":
            current_index = 1
        elif current_mode == "specific":
            current_index = 2
        
        # Error selection mode radio buttons
        selected_option = st.radio(
            "How would you like to select errors?",
            options=mode_options,
            index=current_index,
            key="error_mode_radio",
            label_visibility="collapsed",
            horizontal=True
        )
        
        # Print previous and new selection for debugging
        print(f"\n========== MODE SELECTION CHANGE ==========")
        print(f"Previous mode: {st.session_state.error_selection_mode}")
        
        # Update error selection mode based on selection
        new_mode = st.session_state.error_selection_mode
        if "Standard" in selected_option and st.session_state.error_selection_mode != "standard":
            new_mode = "standard"
        elif "Advanced" in selected_option and st.session_state.error_selection_mode != "advanced":
            new_mode = "advanced"
        elif "Specific" in selected_option and st.session_state.error_selection_mode != "specific":
            new_mode = "specific"
        
        # Only update if the mode has changed
        if new_mode != st.session_state.error_selection_mode:
            print(f"Mode changing from {st.session_state.error_selection_mode} to {new_mode}")
            
            # Store previous mode for reference
            previous_mode = st.session_state.error_selection_mode
            
            # Update the mode
            st.session_state.error_selection_mode = new_mode
            
            # Importantly: Clear selections when switching TO Advanced mode
            # This prevents auto-selected categories when changing modes
            if new_mode == "advanced":
                # Reset categories to empty when switching to advanced mode
                st.session_state.selected_error_categories = {
                    "build": [],
                    "checkstyle": []
                }
                print("Cleared error categories when switching to Advanced mode")
                
            # Initialize or reset appropriate selections when mode changes
            if new_mode == "standard":
                # Ensure problem areas are set for Standard mode
                if not hasattr(st.session_state, "problem_areas") or not st.session_state.problem_areas:
                    st.session_state.problem_areas = []
            elif new_mode == "specific":
                # Make sure selected_specific_errors exists
                if "selected_specific_errors" not in st.session_state:
                    st.session_state.selected_specific_errors = []
        
        print(f"Current mode: {st.session_state.error_selection_mode}")
        print(f"Selected categories: {st.session_state.selected_error_categories}")
        print("=============================================")
        
        # Show help text for the selected mode
        if st.session_state.error_selection_mode == "standard":
            st.info("Standard mode: Select general problem areas like Style, Logic, or Performance. The system will map these to specific error categories.")
        elif st.session_state.error_selection_mode == "advanced":
            st.info("Advanced mode: Select specific error categories like LogicalErrors or NamingConventionChecks. The system will randomly select errors from these categories.")
        else:
            st.info("Specific mode: Choose exactly which errors will appear in the generated code.")
        
        return st.session_state.error_selection_mode
    
    def render_simple_mode(self) -> List[str]:
        """
        Render a more professional problem area selection UI with improved styling.
        Includes enhanced debugging output for problem areas and mapped error categories.
        
        Returns:
            List of selected problem areas
        """
        st.markdown("#### Focus Areas for Code Review")
        st.markdown("Select the categories of issues you want to find in the generated code:")
        
        # Problem area definitions with icons and descriptions
        problem_areas_config = {
            "Style": {
                "icon": "",
                "description": "Naming conventions, whitespace, formatting, and documentation issues",
                "mapping": {
                    "build": [],
                    "checkstyle": ["NamingConventionChecks", "WhitespaceAndFormattingChecks", "JavadocChecks"]
                }
            },
            "Logical": {
                "icon": ">�",
                "description": "Logic flaws, incorrect conditionals, off-by-one errors, and algorithm issues",
                "mapping": {
                    "build": ["LogicalErrors"],
                    "checkstyle": []
                }
            },
            "Performance": {
                "icon": "�",
                "description": "Inefficient code, unnecessary operations, resource leaks, and optimization issues",
                "mapping": {
                    "build": ["RuntimeErrors"],
                    "checkstyle": ["MetricsChecks"]
                }
            },
            "Security": {
                "icon": "=",
                "description": "Potential vulnerabilities, input validation issues, and unsafe operations",
                "mapping": {
                    "build": ["RuntimeErrors", "LogicalErrors"],
                    "checkstyle": ["CodeQualityChecks"]
                }
            },
            "Design": {
                "icon": "<�",
                "description": "Poor class design, code organization, and maintainability problems",
                "mapping": {
                    "build": ["LogicalErrors"],
                    "checkstyle": ["MiscellaneousChecks", "FileStructureChecks", "BlockChecks"]
                }
            }
        }
        
        # Start of grid container
        st.markdown('<div class="problem-area-grid">', unsafe_allow_html=True)
        
        # Initialize empty list for selected areas
        problem_areas = []
        
        # Add cards for each problem area
        for area, config in problem_areas_config.items():
            is_selected = area in st.session_state.problem_areas
            selected_class = "selected" if is_selected else ""
            
            st.markdown(f"""
            <div class="problem-area-card {selected_class}" id="card-{area.lower()}" 
                onclick="this.classList.toggle('selected'); 
                        document.getElementById('checkbox-{area.lower()}').click();">
                <div class="problem-area-title">
                    {area} <span class="icon">{config['icon']}</span>
                </div>
                <p class="problem-area-description">{config['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Hidden checkbox to track selection state
            if st.checkbox(area, value=is_selected, key=f"checkbox-{area.lower()}", label_visibility="collapsed"):
                problem_areas.append(area)
        
        # End of grid container
        st.markdown('</div>', unsafe_allow_html=True)
        
        # JavaScript to make the cards clickable and sync with checkboxes
        st.markdown("""
        <script>
        // Add event listeners for card selection
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.problem-area-card');
            cards.forEach(card => {
                card.addEventListener('click', function() {
                    const id = this.id.replace('card-', '');
                    const checkbox = document.getElementById(`checkbox-${id}`);
                    if (checkbox) checkbox.click();
                });
            });
        });
        </script>
        """, unsafe_allow_html=True)
        
        # Update session state
        st.session_state.problem_areas = problem_areas
        
        # Important change: No longer defaulting to Style if nothing selected
        if not problem_areas:
            st.warning("Please select at least one problem area. No errors will be included until you make a selection.")
        
        # Display selected areas with professional badges
        if problem_areas:
            st.markdown("#### Selected Focus Areas:")
            badges_html = ""
            for area in problem_areas:
                config = problem_areas_config.get(area, {"icon": ""})
                badges_html += f'<span style="color: #4c68d7; padding: 6px 12px; border-radius: 16px; margin-right: 10px; font-size: 0.9em; display: inline-flex; align-items: center; border: 1px solid rgba(76, 104, 215, 0.3);"><span style="margin-right: 5px;">{config["icon"]}</span> {area}</span>'
            
            st.markdown(f"<div style='margin-top: 10px;'>{badges_html}</div>", unsafe_allow_html=True)
            
            # Add explanation of mapping
            with st.expander("How problem areas map to error categories"):
                st.markdown("When you select problem areas, they map to specific error categories:")
                for area in problem_areas:
                    config = problem_areas_config.get(area, {"mapping": {"build": [], "checkstyle": []}})
                    mapping = config["mapping"]
                    
                    st.markdown(f"**{area}** maps to:")
                    
                    if mapping["build"]:
                        st.markdown("Build error categories:")
                        for category in mapping["build"]:
                            st.markdown(f"- {category}")
                    
                    if mapping["checkstyle"]:
                        st.markdown("Checkstyle categories:")
                        for category in mapping["checkstyle"]:
                            st.markdown(f"- {category}")
                    
                    if not mapping["build"] and not mapping["checkstyle"]:
                        st.markdown("No specific error categories")
        
        # Map problem areas to error categories - this is used by the application
        selected_categories = {
            "build": [],
            "checkstyle": []
        }
        
        # Build selected categories from problem areas
        for area in problem_areas:
            if area in problem_areas_config:
                mapping = problem_areas_config[area]["mapping"]
                for category in mapping["build"]:
                    if category not in selected_categories["build"]:
                        selected_categories["build"].append(category)
                for category in mapping["checkstyle"]:
                    if category not in selected_categories["checkstyle"]:
                        selected_categories["checkstyle"].append(category)
        
        # Update session state with the mapping result
        st.session_state.selected_error_categories = selected_categories
        
        # Enhanced debug print of selected categories with potential errors
        print("\n========== STANDARD MODE SELECTION ==========")
        print(f"Problem Areas: {problem_areas}")
        print(f"Build Categories: {selected_categories.get('build', [])}")
        print(f"Checkstyle Categories: {selected_categories.get('checkstyle', [])}")
        
        # If any categories are selected, show potential errors
        if selected_categories["build"] or selected_categories["checkstyle"]:
            print("\n--- POTENTIAL ERRORS BY CATEGORY ---")
            
            # For build categories
            for category in selected_categories["build"]:
                print(f"Build Category: {category}")
                # Get sample errors from this category if available
                try:
                    from data.json_error_repository import JsonErrorRepository
                    repo = JsonErrorRepository()
                    errors = repo.get_category_errors("build", category)
                    if errors:
                        print(f"  Sample errors (max 3):")
                        for i, error in enumerate(errors[:3]):
                            print(f"    {i+1}. {error.get('error_name', 'Unknown')}: {error.get('description', '')[:50]}..." 
                                if len(error.get('description', '')) > 50 else error.get('description', ''))
                except Exception as e:
                    print(f"  Error retrieving category info: {str(e)}")
            
            # For checkstyle categories
            for category in selected_categories["checkstyle"]:
                print(f"Checkstyle Category: {category}")
                # Get sample errors from this category if available
                try:
                    from data.json_error_repository import JsonErrorRepository
                    repo = JsonErrorRepository()
                    errors = repo.get_category_errors("checkstyle", category)
                    if errors:
                        print(f"  Sample errors (max 3):")
                        for i, error in enumerate(errors[:3]):
                            print(f"    {i+1}. {error.get('check_name', 'Unknown')}: {error.get('description', '')[:50]}..." 
                                if len(error.get('description', '')) > 50 else error.get('description', ''))
                except Exception as e:
                    print(f"  Error retrieving category info: {str(e)}")
        
        print("=============================================")
        
        return problem_areas

    def render_code_params(self) -> Dict[str, str]:
        """
        Render code generation parameters UI with improved professional appearance.
        
        Returns:
            Dictionary with code generation parameters
        """
        # Initialize parameters if not in session state
        if "difficulty_level" not in st.session_state:
            st.session_state.difficulty_level = "Medium"
        if "code_length" not in st.session_state:
            st.session_state.code_length = "Medium"
        
        st.markdown('<div class="param-container">', unsafe_allow_html=True)
        
        # Create columns for a more compact layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="param-title">Difficulty Level</div>', unsafe_allow_html=True)
            st.markdown('<div class="param-description">Determines the complexity and subtlety of errors in the code</div>', unsafe_allow_html=True)
            difficulty_level = st.select_slider(
                "Select difficulty",
                options=["Easy", "Medium", "Hard"],
                value=st.session_state.difficulty_level,
                key="difficulty_level_select",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown('<div class="param-title">Code Length</div>', unsafe_allow_html=True)
            st.markdown('<div class="param-description">Controls the size and complexity of the generated code</div>', unsafe_allow_html=True)
            code_length = st.select_slider(
                "Select code length",
                options=["Short", "Medium", "Long"],
                value=st.session_state.code_length,
                key="code_length_select",
                label_visibility="collapsed"
            )
        
        # Update session state
        st.session_state.difficulty_level = difficulty_level
        st.session_state.code_length = code_length
        
        # Show explanation of selected options with improved styling
        difficulty_explanation = {
            "Easy": "Basic errors that are relatively obvious, suitable for beginners",
            "Medium": "More subtle errors requiring careful code reading, good for practice",
            "Hard": "Complex, hard-to-spot errors that might require deeper Java knowledge"
        }
        
        length_explanation = {
            "Short": "~50 lines of code, typically 1 class with a few methods",
            "Medium": "~100-150 lines, 1-2 classes with multiple methods",
            "Long": "~200+ lines, multiple classes with complex relationships"
        }
        
        st.markdown('<div class="param-value">', unsafe_allow_html=True)
        st.markdown(f"**Difficulty:** {difficulty_level} - {difficulty_explanation[difficulty_level]}", unsafe_allow_html=True)
        st.markdown(f"**Length:** {code_length} - {length_explanation[code_length]}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return {
            "difficulty_level": difficulty_level.lower(),
            "code_length": code_length.lower()
        }