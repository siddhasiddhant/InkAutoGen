#!/usr/bin/env python3
"""
SVG template processing utilities for InkAutoGen extension.

This module provides core functionality for parsing and processing SVG template files.
It supports variable replacement in SVG documents based on data from CSV files, enabling
mass customization of SVG designs.

Key Components:
    - CSVReader: Parses and validates CSV header patterns using new CSV_HEADER_PATTERN
    - SVGElementProcessor: Handles element-specific operations (text, layers, images, properties)
    - SVGTemplateProcessor: Coordinates overall template application process

Key Patterns (CSV Headers):
    Element headers: <element label name>
        - MyTitle: Replace text content
        - Background: Control layer visibility
        - Logo: Replace image reference

    Property headers: <element label name>##<property name>
        - MyBox##fill: Change fill color of MyBox
        - MyCircle##stroke: Change stroke of MyCircle
        - Title##font-size: Change font size of Title

Usage:
    >>> logger = logging.getLogger(__name__)
    >>> processor = SVGTemplateProcessor(logger, csv_dir="./")
    >>> svg_root = etree.parse("template.svg").getroot()
    >>> data_row = {"Text_name": "John Doe", "Layer_background": "visible"}
    >>> stats = processor.apply_data_to_template(svg_root, data_row)
    >>> print(f"Replaced {stats['text_replaced']} text elements")

Dependencies:
    - lxml: For XML/SVG parsing and XPath queries
    - re: For regex pattern matching in key parsing
    - config: Configuration constants and patterns
    - exceptions: Custom exception classes
    - security: File validation utilities
"""

import os
import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from lxml import etree

import config
import utilities
from exceptions import SVGTemplateError
from security import FileValidator

class SVGElementProcessor:
    """
    Handles processing of individual SVG elements.
    
    This class provides methods to modify various SVG element types
    based on template keys and data values.
    """
    #def __init__(self, csv_dir: str, output_dir: str, logger: Optional[logging.Logger] = None):
    def __init__(self, csv_dir: Optional[str] = None, output_dir: Optional[str] = None
                 , is_use_relative_path: bool = False, logger: Optional[logging.Logger] = None):
        self.csv_dir = csv_dir
        self.output_dir = output_dir
        self.use_relative_path = is_use_relative_path
        self.logger = logger
        # Caching for performance
        self._color_cache = {}  # Color conversion cache
        self._element_cache = {}  # Element lookup cache    
    
    @staticmethod
    def get_display_attribute(element):
        """
        Get the display attribute value from an SVG element.
        
        Args:
            element: lxml element object
            
        Returns:
            str: Display value ('inline', 'none', 'block', etc.) or None if not found
        """
        # Method 1: Check style attribute
        style = element.get('style', '')
        if style:
            # Look for display: value in style string
            display_match = re.search(r'display\s*:\s*([^;]+)', style)
            if display_match:
                return display_match.group(1).strip()
        
        # Method 2: Check direct display attribute
        display = element.get('display')
        if display:
            return display.strip()
        
        # Method 3: Check for default display (element is visible)
        return 'inline'  # Default for SVG elements
    

    @staticmethod
    def set_display_value(element, display_value):
        """Set display value for element."""
        style = element.get('style', '')
        
        # Remove existing display declaration
        style = re.sub(r'display\s*:\s*[^;]*;?', '', style).strip(';')
        
        # Add new display value
        if style:
            style += f'; display:{display_value}'
        else:
            style = f'display:{display_value}'
        
        element.set('style', style)


    def process_text_element(self, element, variable_name: str, value: Optional[str]) -> bool:
        """
        Process text element by replacing text content.
        
        Args:
            element: SVG text element
            variable_name: Variable name from template
            value: Value to set
        
        Returns:
            True if element was modified, False otherwise
        """
        if value is None:
            if self.logger:
                self.logger.debug(f"      ❌ No value provided for text element '{variable_name}'")
            return False
        
        original_text = element.text or ''.join(el.text or '' for el in element if el.text)
        
        if self.logger:
            elem_id = element.get('id', 'no-id')
            elem_label = element.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}label", 'no-label')
            self.logger.debug(f"      Text element: id={elem_id}, label={elem_label}")
            self.logger.debug(f"      Current text: '{original_text}'")
            self.logger.debug(f"      New text: '{value}'")
        
        if original_text != value:
            if element.text == original_text:
                element.text = value
            else:
                for el in element :
                    if el.text == original_text:
                        el.text = value

            if self.logger:
                self.logger.debug(f"      ✅ Text updated: '{original_text}' -> '{value}'")
            return True
        else:
            if self.logger:
                self.logger.debug(f"      ⚠️ No change needed - texts are identical")
            return False
    
    def process_layer_element(self, element, variable_name: str, value: Optional[str]) -> bool:
        """
        Process layer element by controlling visibility.
        
        Args:
            element: SVG group element (layer)
            variable_name: Variable name from template
            value: Visibility value
        
        Returns:
            True if element was modified, False otherwise
        """
        if value is None:
            if self.logger:
                self.logger.debug(f"      ❌ No value provided for layer element '{variable_name}'")
            return False
        
        # Normalize visibility value
        normalized_value = value.lower().strip()
        display_value = config.LAYER_VISIBILITY_MAP.get(normalized_value, 'inline')
        
        elem_id = element.get('id', 'no-id')
        elem_label = element.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}label", 'no-label')
        #current_display = element.get('display', 'inline')
        #current_display = self.get_display_attribute(element)
        current_display = utilities.parse_style(element.get('style')).get('display')
        
        if self.logger:
            self.logger.debug(f"      Layer element: id={elem_id}, label={elem_label}")
            self.logger.debug(f"      Current visibility: '{current_display}'")
            self.logger.debug(f"      Input value: '{value}' -> normalized: '{normalized_value}' -> display: '{display_value}'")
        
        
        if current_display != display_value:
            self.set_display_value(element=element,display_value=display_value)
            if self.logger:
                self.logger.debug(f"      ✅ Layer visibility updated: '{current_display}' -> '{display_value}'")
            return True
        else:
            if self.logger:
                self.logger.debug(f"      ⚠️ No change needed - visibility already set to '{display_value}'")
            return False
    
    def process_image_element(self, element, variable_name: str, value: Optional[str]) -> bool:
        """
        Process image element by replacing href.
        
        Args:
            element: SVG image element
            variable_name: Variable name from template
            value: Image filename or path
        
        Returns:
            True if element was modified, False otherwise
        """
        if value is None:
            if self.logger:
                self.logger.debug(f"      ❌ No value provided for image element '{variable_name}'")
            return False
        
        value_str = str(value).strip()
        if not value_str:
            if self.logger:
                self.logger.debug(f"      ❌ Empty value provided for image element '{variable_name}'")
            return False
        
        elem_id = element.get('id', 'no-id')
        elem_label = element.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}label", 'no-label')
        original_href = element.get(f"{{{config.SVG_NAMESPACES['xlink']}}}href", '') or element.get('href', '')
        #original_href = element.get('href', '') or element.get('xlink:href', '')
        
        if self.logger:
            self.logger.debug(f"      Image element: id={elem_id}, label={elem_label}")
            self.logger.debug(f"      Current href: '{original_href}'")
            self.logger.debug(f"      New href: '{value_str}'")
        
        if not original_href:
            if self.logger:
                self.logger.warning(f"      ⚠️ No original href found in template for image '{variable_name}'")
            #return False
        
        # Check if value is meant to be filename only (not full path)
        is_filename_only = not os.path.isabs(value_str) and '://' not in value_str
        final_href = value_str
        
        if is_filename_only:
            if self.logger:
                self.logger.debug(f"    Value '{value_str}' is a filename only, searching in absolute path.")
            
            # Search for file
            found_path = utilities.find_file(
                filename=value_str,
                search_dir=self.csv_dir or "",
                output_dir=self.output_dir or "",
                logger=self.logger)
            
            if found_path:
                # Use absolute path for validation
                final_href = found_path['absolute']
                if self.logger:
                    self.logger.info(f"    Found image file '{value_str}' a1 '{final_href}'")
            else:
                if self.logger:
                    self.logger.warning(f"    Image file '{value_str}' not found in search directories")
                
        # Validate image file security
        try:
            FileValidator.validate_image_file(final_href)
        except Exception as validation_error:
            # Check if this is a security issue
            is_security_issue = False
            if hasattr(validation_error, 'args') and len(validation_error.args) > 0:
                error_msg = str(validation_error.args[0])
                is_security_issue = any(ind in error_msg.lower() for ind in config.SECURITY_INDICATORS)
            
            if is_security_issue:
                if self.logger:
                    self.logger.warning(f"    Security validation failed for '{value_str}': {validation_error}")
                    self.logger.info(f"    Preserving template's original href instead of updating")
                return False
        
        # Update href
        if self.use_relative_path is True:
            if self.logger:
                self.logger.debug('Using relative path for image file.')

            final_href = found_path['relative'] if found_path and 'relative' in found_path else value_str
        
        if original_href != final_href:
            element.set(f"{{{config.SVG_NAMESPACES['xlink']}}}href", final_href)
            if self.logger:
                self.logger.debug(f"    Updated '{original_href}' -> '{final_href}'")
            return True
        
        return False
    

    def process_property(self, element, property_name: str, value: Optional[str], 
                      element_type: str) -> bool:
        """
        Process property change for an element.
        
        This method handles both direct SVG attributes and CSS style properties.
        If the property belongs to the style attribute, it will:
        - Add style attribute if not present
        - Modify existing style attribute with the required property
        
        Args:
            element: SVG element
            property_name: Property name to change
            value: New value for property
            element_type: Type of element (rect, circle, text, etc.)
        
        Returns:
            True if element was modified, False otherwise
        """
        if value is None:
            if self.logger:
                self.logger.debug(f"        ❌ No value provided for property '{property_name}'")
            return False
        
        elem_id = element.get('id', 'no-id')
        elem_label = element.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}label", 'no-label')
        
        if self.logger:
            self.logger.debug(f"        Property processing on {element_type}: id={elem_id}, label={elem_label}")
            self.logger.debug(f"        Property: {property_name} = '{value}'")
        
        # First verify property is supported for this element type
        if element_type.lower() not in config.SUPPORTED_PROPERTY_ELEMENTS:
            if self.logger:
                self.logger.warning(f"        ⚠️ Element type '{element_type}' does not support properties")
            return False
        
        # Map property names to SVG attributes using comprehensive mapping from config
        svg_attr = config.PROPERTY_ATTRIBUTE_MAP.get(property_name.lower())
        if not svg_attr:
            if self.logger:
                self.logger.warning(f"        ⚠️ Unknown property: {property_name}")
            return False
        
        converted_value = value
        # Validate color values
        if svg_attr in ['fill', 'stroke']:
            # Convert color aliases to hex values when reading from CSV
            converted_value = utilities.convert_color_to_hex(value)
            if not utilities.is_valid_color(value=converted_value, logger=self.logger):
                if self.logger:
                    self.logger.warning(f"        ⚠️ Invalid color value: {converted_value}")
                return False
            elif self.logger:
                self.logger.debug(f"        Color conversion: '{value}' -> '{converted_value}'")
        
        # Determine if this property should go in style attribute or be a direct attribute
        is_style_property = svg_attr in config.STYLE_PROPERTIES
        
        if is_style_property:
            # Handle property as CSS style
            return self._process_style_property(element, svg_attr, converted_value)
        else:
            # Handle property as direct attribute
            return self._process_direct_attribute(element, svg_attr, converted_value)
            
    def _process_style_property(self, element, property_name: str, value: str) -> bool:
        """
        Process property that belongs to the style attribute.
        
        Args:
            element: SVG element
            property_name: CSS property name
            value: New property value
            
        Returns:
            True if element was modified, False otherwise
        """
        attrs = utilities.get_element_attributes(element)
        
        if self.logger:
            self.logger.debug(f"        Style property: {property_name}")
            self.logger.debug(f"        Processing element: {attrs['label']}")
        
        return utilities.update_svg_style_property(element, property_name, value, self.logger)
    
    def _process_direct_attribute(self, element, attribute_name: str, value: str) -> bool:
        """
        Process property that is a direct SVG attribute.
        
        Args:
            element: SVG element
            attribute_name: SVG attribute name
            value: New attribute value
            
        Returns:
            True if element was modified, False otherwise
        """
        # Get current attribute value
        current_value = element.get(attribute_name, '')
        
        if self.logger:
            self.logger.debug(f"        Direct attribute: {attribute_name}")
            self.logger.debug(f"        Current {attribute_name}: '{current_value}'")
            self.logger.debug(f"        New {attribute_name}: '{value}'")
        
        # Check if value needs to be changed
        if str(current_value) != str(value):
            # Set the attribute
            element.set(attribute_name, str(value))
            
            if self.logger:
                self.logger.debug(f"        ✅ Attribute updated: {attribute_name} '{current_value}' -> '{value}'")
            
            return True
        else:
            if self.logger:
                self.logger.debug(f"        ⚠️ No attribute change needed - already set to '{value}'")
            return False
    

    def validate_svg(self, svg_root) -> Tuple[bool, List[str]]:
        """
        Validate SVG buffer for potential issues.
        
        Args:
            svg_root: SVG document root element
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for required attributes
        if not svg_root.get('width') and not svg_root.get('viewBox'):
            issues.append("SVG missing width or viewBox attribute")
        
        if not svg_root.get('height') and not svg_root.get('viewBox'):
            issues.append("SVG missing height or viewBox attribute")
        
        # Check for elements with IDs that might conflict
        id_counts = {}
        for element in svg_root.iter():
            element_id = element.get('id')
            if element_id:
                id_counts[element_id] = id_counts.get(element_id, 0) + 1
        
        duplicate_ids = [id for id, count in id_counts.items() if count > 1]
        if duplicate_ids:
            issues.append(f"Duplicate IDs found: {duplicate_ids}")
        
        return (len(issues) == 0, issues)
    

    def apply_data_to_template(self, svg_root, data_row: Dict[str, str], 
                             apply_layer_visibility: bool = False, 
                             csv_classification: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
        """
        Apply data from CSV row to SVG template.
        
        Args:
            svg_root: SVG document root element
            data_row: Dictionary of variable names to values
            apply_layer_visibility: Whether to apply layer visibility filtering
            csv_classification: Pre-classified CSV data (optimization - pass to avoid redundant parsing)
        
        Returns:
            Dictionary with statistics about processing
        """

        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("SVG TEMPLATE PROCESSING STARTED")
            self.logger.info("=" * 60)
            self.logger.debug(f"SVG root tag: {svg_root.tag if svg_root else 'None'}")
            self.logger.debug(f"Data row keys: {list(data_row.keys())}")
            self.logger.debug(f"Apply layer visibility: {apply_layer_visibility}")
            self.logger.debug(f"CSV classification provided: {csv_classification is not None}")

        #validate input parameters
        if not svg_root:
            raise SVGTemplateError("SVG root element is None")
        
        if not data_row:
            raise SVGTemplateError("Data row is empty")
        
        if self.logger:
            self.logger.debug(f"Processing Data row: {data_row}")
            self.logger.debug(f"Data row values count: {len(data_row)}")

        # Initialize statistics tracking
        stats = {
            'text_replaced': 0,
            'layers_modified': 0,
            'images_replaced': 0,
            'properties_modified': 0,
            'errors': 0
        }
        
        if self.logger:
            self.logger.debug(f"Initial statistics: {stats}")
        
        try:
            # Use pre-classified data if provided (optimization), otherwise classify on the fly
            if csv_classification:
                if self.logger:
                    self.logger.info("Using pre-classified CSV data")
                    self.logger.debug(f"Elements: {csv_classification['elements']}")
                    self.logger.debug(f"Properties: {csv_classification['properties']}")
                    if csv_classification.get('missing_elements'):
                        self.logger.debug(f"Missing elements: {csv_classification['missing_elements']}")
                classification = csv_classification
            else:
                if self.logger:
                    self.logger.info("Classifying CSV data on-the-fly")
                # Fallback: classify on the fly (redundant but for compatibility)
                from csv_reader import CSVReader
                csv_reader = CSVReader(self.logger)
                classification = csv_reader.classify_csv_data([data_row], svg_root)
                
                if self.logger:
                    self.logger.debug(f"Data classification: {len(classification['elements'])} elements, {len(classification['properties'])} properties")
            
            if self.logger:
                self.logger.info("=" * 40)
                self.logger.info("GROUPING OPERATIONS BY ELEMENT")
                self.logger.info("=" * 40)
            
            # Optimized processing: Group operations by element name to reduce lookups
            element_operations = {}
            layer_data = {}
            
            operation_count = 0
            
            # Group element mapping operations
            if self.logger:
                self.logger.debug("Processing element mappings...")
            
            for header, parsed_header in classification['element_mapping'].items():
                if header in data_row:
                    element_name = parsed_header['element_name']
                    element_type = parsed_header['element_type']
                    value = data_row[header]
                    
                    if self.logger:
                        self.logger.debug(f"  Element mapping: {header} -> {element_name} ({element_type}) = '{value}'")
                    
                    if element_name not in element_operations:
                        element_operations[element_name] = {
                            'elements': None,  # Will be loaded when needed
                            'element_type': element_type,
                            'operations': []
                        }
                    
                    if element_type == 'layer':
                        layer_data[element_name] = value
                        if self.logger:
                            self.logger.debug(f"    Added layer operation: {element_name} -> '{value}'")
                    else:
                        element_operations[element_name]['operations'].append({
                            'type': 'value',
                            'value': value,
                            'header': header
                        })
                        operation_count += 1
                        if self.logger:
                            self.logger.debug(f"    Added element operation: {element_name} -> '{value}'")
            
            # Group property operations
            if self.logger:
                self.logger.debug("Processing property mappings...")
            
            for header, parsed_header in classification['property_mapping'].items():
                if header in data_row:
                    element_name = parsed_header['element_name']
                    property_name = parsed_header['property_name']
                    value = data_row[header]
                    
                    if self.logger:
                        self.logger.debug(f"  Property mapping: {header} -> {element_name}.{property_name} = '{value}'")
                    
                    if element_name not in element_operations:
                        element_operations[element_name] = {
                            'elements': None,
                            'element_type': None,
                            'operations': []
                        }
                    
                    element_operations[element_name]['operations'].append({
                        'type': 'property',
                        'property_name': property_name,
                        'value': value,
                        'header': header
                    })
                    operation_count += 1
                    if self.logger:
                        self.logger.debug(f"    Added property operation: {element_name}.{property_name} -> '{value}'")
            
            if self.logger:
                self.logger.info(f"Operations grouped: {len(element_operations)} unique elements, {operation_count} total operations")
                self.logger.info(f"Layer operations: {len(layer_data)} layers")
            
            # Apply layer visibility first
            if layer_data:
                if self.logger:
                    self.logger.info("=" * 40)
                    self.logger.info("PROCESSING LAYER VISIBILITY")
                    self.logger.info("=" * 40)
                self.apply_layer_visibility(svg_root, layer_data, stats)
            else:
                if self.logger:
                    self.logger.debug("No layer visibility operations to process")
            
            # Remove invisible layers if option is enabled
            if apply_layer_visibility:
                if self.logger:
                    self.logger.info("=" * 40)
                    self.logger.info("REMOVING INVISIBLE LAYERS")
                    self.logger.info("=" * 40)
                self.remove_invisible_layers(svg_root, stats)
            else:
                if self.logger:
                    self.logger.debug("Layer removal disabled by configuration")
            
            # Process all element operations in optimized way
            self._process_element_operations(svg_root, element_operations, stats)
                        
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ ERROR applying data to template: {e}")
                self.logger.error(f"   Stack trace: ", exc_info=True)
            stats['errors'] += 1
        finally:
            if self.logger:
                self.logger.info("=" * 40)
                self.logger.info("SVG PROCESSING SUMMARY")
                self.logger.info("=" * 40)
                self.logger.info(f"📊 Final Statistics:")
                self.logger.info(f"   Text elements replaced: {stats['text_replaced']}")
                self.logger.info(f"   Images replaced: {stats['images_replaced']}")
                self.logger.info(f"   Properties modified: {stats['properties_modified']}")
                self.logger.info(f"   Layers modified: {stats['layers_modified']}")
                self.logger.info(f"   Errors encountered: {stats['errors']}")
                self.logger.info("=" * 60)
                self.logger.info("SVG TEMPLATE PROCESSING COMPLETED")
                self.logger.info("=" * 60)
              
        return stats
    
    def _process_element_operations(self, svg_root, element_operations: Dict[str, Any], stats: Dict[str, int]):
        """
        Process all operations for elements in an optimized way.
        
        Args:
            svg_root: SVG document root element
            element_operations: Dictionary of element operations grouped by element name
            stats: Statistics dictionary to update
        """
        if self.logger:
            self.logger.info("=" * 40)
            self.logger.info("PROCESSING ELEMENT OPERATIONS")
            self.logger.info("=" * 40)
        
        processed_elements = 0
        
        for element_name, operation_data in element_operations.items():
            if self.logger:
                self.logger.debug(f"Processing element: {element_name}")
                self.logger.debug(f"  Operations count: {len(operation_data['operations'])}")
                self.logger.debug(f"  Element type: {operation_data['element_type']}")
            
            # Load elements once per element name
            elements = self.find_elements_by_name(svg_root, element_name)
            if not elements:
                if self.logger:
                    self.logger.warning(f"  ❌ No elements found for: {element_name}")
                stats['errors'] += 1
                continue
            
            if self.logger:
                self.logger.debug(f"  ✅ Found {len(elements)} element(s) for: {element_name}")
                for i, elem in enumerate(elements):
                    elem_id = elem.get('id', 'no-id')
                    elem_label = elem.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}label", 'no-label')
                    self.logger.debug(f"    Element {i+1}: tag={elem.tag}, id={elem_id}, label={elem_label}")
            
            processed_elements += 1
            
            # Process all operations for this element
            for i, operation in enumerate(operation_data['operations']):
                if self.logger:
                    self.logger.debug(f"  Operation {i+1}/{len(operation_data['operations'])}: {operation['type']}")
                
                for j, element in enumerate(elements):
                    element_tag = element.tag.lower()
                    
                    if operation['type'] == 'property':
                        property_name = operation['property_name']
                        value = operation['value']
                        if self.logger:
                            self.logger.debug(f"    Element {j+1}: Applying property {property_name} = '{value}'")
                        if self.process_property(element, property_name, value, element.tag):
                            stats['properties_modified'] += 1
                            if self.logger:
                                self.logger.debug(f"      ✅ Property modified successfully")
                        else:
                            if self.logger:
                                self.logger.debug(f"      ⚠️ Property not modified (no change or error)")
                    
                    elif operation['type'] == 'value':
                        element_type = operation_data['element_type']
                        value = operation['value']
                        if self.logger:
                            self.logger.debug(f"    Element {j+1}: Setting value = '{value}' (type: {element_type})")
                        
                        # Process based on element type for better handling
                        if element_type == 'text' or element_tag in ['text', 'tspan', 'flowpara', 'flowspan']:
                            if self.process_text_element(element, element_name, value):
                                stats['text_replaced'] += 1
                                if self.logger:
                                    self.logger.debug(f"      ✅ Text replaced successfully")
                            else:
                                if self.logger:
                                    self.logger.debug(f"      ⚠️ Text not replaced (no change or error)")
                        elif element_type == 'image' or element_tag == 'image':
                            if self.process_image_element(element, element_name, value):
                                stats['images_replaced'] += 1
                                if self.logger:
                                    self.logger.debug(f"      ✅ Image replaced successfully")
                            else:
                                if self.logger:
                                    self.logger.debug(f"      ⚠️ Image not replaced (no change or error)")
                        # Skip layers in element processing (handled separately)
                        elif element_type == 'layer':
                            if self.logger:
                                self.logger.debug(f"      ⏭️ Skipping layer (handled separately)")
        
        if self.logger:
            self.logger.info(f"Processed {processed_elements} unique elements with {len(element_operations)} operation groups")
    
    def find_elements_by_name(self, svg_root, name: str):
        """
        Find elements by name using new search rules: label first, then ID.
        Uses caching for performance optimization.
        
        Args:
            svg_root: SVG document root element
            name: Element name to search for
            
        Returns:
            List of found elements
        """
        # Check cache first
        cache_key = f"{id(svg_root)}_{name}"
        if cache_key in self._element_cache:
            cached_elements = self._element_cache[cache_key]
            if self.logger:
                self.logger.debug(f"    🎯 Cache hit: found {len(cached_elements)} elements for: {name}")
                if len(cached_elements) > 0:
                    for i, elem in enumerate(cached_elements):
                        elem_id = elem.get('id', 'no-id')
                        elem_tag = elem.tag
                        self.logger.debug(f"      Cached {i+1}: tag={elem_tag}, id={elem_id}")
            return cached_elements
        
        if self.logger:
            self.logger.debug(f"    🔍 Searching for elements with name: {name}")
        
        # Optimize: Use single XPath query that checks both label and ID
        try:
            # Combined XPath query for better performance
            xpath_expr = f".//*[@inkscape:label='{name}' or @id='{name}']"
            elements = svg_root.xpath(xpath_expr, namespaces=config.SVG_NAMESPACES)
        except Exception:
            # Fallback to separate queries if combined query fails
            elements = utilities.xpath_query(svg_root, "labeled_elements", name=name)
            if not elements:
                elements = utilities.xpath_query(svg_root, "id_elements", name=name)
        
        if self.logger:
            search_type = "by label/ID" if elements else "No match"
            self.logger.debug(f"    {'📍 Found' if elements else '❌ No'} {len(elements)} elements {search_type} for: {name}")
            
        if elements:
            for i, elem in enumerate(elements):
                attrs = utilities.get_element_attributes(elem)
                if self.logger:
                    self.logger.debug(f"      {i+1}: tag={attrs['tag']}, id={attrs['id']}, label={attrs['label']}")
    
        # Cache result
        self._element_cache[cache_key] = elements
        return elements
    
    def clear_element_cache(self):
        """Clear the element lookup cache."""
        self._element_cache.clear()
        if self.logger:
            self.logger.debug("Element cache cleared")
    
    def apply_layer_visibility(self, svg_root, layer_data: Dict[str, str], stats: Dict[str, int]):
        """
        Apply layer visibility changes.
        
        Args:
            svg_root: SVG document root element
            layer_data: Dictionary mapping layer names to visibility values
            stats: Statistics dictionary to update
        """
        if self.logger:
            self.logger.debug(f"Processing {len(layer_data)} layer visibility operations...")
        
        for layer_name, visibility_value in layer_data.items():
            if self.logger:
                self.logger.debug(f"  Layer: {layer_name} -> '{visibility_value}'")
            
            elements = self.find_elements_by_name(svg_root, layer_name)
            
            for i, element in enumerate(elements):
                elem_id = element.get('id', 'no-id')
                elem_label = element.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}label", 'no-label')
                tmpTag = element.tag.split('}')[-1] if '}' in element.tag.lower() else element.tag.lower()
                is_layer =  tmpTag == 'g' and element.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}groupmode") == 'layer'
                
                if self.logger:
                    self.logger.debug(f"    Element {i+1}: tag={element.tag}, id={elem_id}, label={elem_label}, is_layer={is_layer}")
                
                if is_layer:
                    if self.process_layer_element(element, layer_name, visibility_value):
                        stats['layers_modified'] += 1
                        if self.logger:
                            self.logger.debug(f"      ✅ Layer visibility updated")
                    else:
                        if self.logger:
                            self.logger.debug(f"      ⚠️ Layer visibility not changed")
                else:
                    if self.logger:
                        self.logger.debug(f"      ❌ Element '{layer_name}' is not a layer, skipping visibility change")
    
    def remove_invisible_layers(self, svg_root, stats: Dict[str, int]):
        """
        Remove layers with display='none' from the SVG tree.
        
        Args:
            svg_root: SVG document root element
            stats: Statistics dictionary to update
        """
        if self.logger:
            self.logger.debug("Scanning for invisible layers...")
        
        removed_count = 0
        layers_to_remove = []
        
        # Find all invisible layers
        xpath_expr = config.COMMON_XPATH_EXPRESSIONS["invisible_layers"]
        invisible_layers = svg_root.xpath(xpath_expr, namespaces=config.SVG_NAMESPACES)
        
        if self.logger:
            self.logger.debug(f"  Found {len(invisible_layers)} invisible layers")
            
            for i, layer in enumerate(invisible_layers):
                layer_id = layer.get('id', 'no-id')
                layer_label = layer.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}label", 'no-label')
                current_display = layer.get('display', 'unknown')
                self.logger.debug(f"    {i+1}: id={layer_id}, label={layer_label}, display={current_display}")
        
        # Collect layers for removal
        for layer in invisible_layers:
            parent = layer.getparent()
            if parent is not None:
                layers_to_remove.append(layer)
        
        # Remove layers safely
        for layer in layers_to_remove:
            parent = layer.getparent()
            if parent is not None:
                layer_label = layer.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}label", layer.get('id', 'unknown'))
                if self.logger:
                    self.logger.debug(f"  🗑️ Removing layer: {layer_label}")
                parent.remove(layer)
                removed_count += 1
                if self.logger:
                    self.logger.debug(f"    ✅ Successfully removed: {layer_label}")
        
        if self.logger:
            self.logger.info(f"🗑️ Removed {removed_count} invisible layers from SVG tree")
        
        # Update stats (though this might be used differently)
        if removed_count > 0:
            stats['layers_modified'] += removed_count
    
    def export_svg_to_csv(self, svg_root, csv_path: str) -> bool:
        """
        Export SVG elements to CSV format based on supported scanning patterns.
        
        This method scans the SVG file and generates a CSV file with columns for:
        - Element labels (Text elements, Image elements, Layer elements)
        - Properties (fill, stroke, font-size, etc.) for various element types
        
        Args:
            svg_root: SVG document root element
            csv_path: Output CSV file path
            logger: Optional logger instance
            
        Returns:
            True if export successful, False otherwise
        """
        import csv
        import os
        
        if self.logger:
            self.logger.info(f"Exporting SVG elements to CSV: {csv_path}")
        
        try:
            # Collect all elements with labels or IDs
            element_data = {}
            
            # Scan for text elements
            text_elements = svg_root.xpath(config.COMMON_XPATH_EXPRESSIONS["text_elements"], namespaces=config.SVG_NAMESPACES)
            for elem in text_elements:
                label = elem.get('inkscape:label') or elem.get('id')
                if label:
                    element_data[f"{label}"] = elem.text or ""
            
            # Scan for image elements  
            image_elements = svg_root.xpath(config.COMMON_XPATH_EXPRESSIONS["image_elements"], namespaces=config.SVG_NAMESPACES)
            for elem in image_elements:
                label = elem.get('inkscape:label') or elem.get('id')
                if label:
                    href = elem.get('xlink:href') or elem.get('href', '')
                    # Extract filename from href
                    if href:
                        filename = os.path.basename(href)
                        element_data[f"{label}"] = filename
            
            # Scan for layer elements
            layer_elements = svg_root.xpath(config.COMMON_XPATH_EXPRESSIONS["layer_elements"], namespaces=config.SVG_NAMESPACES)
            for elem in layer_elements:
                label = elem.get('inkscape:label') or elem.get('id')
                if label:
                    display = elem.get('display', 'inline')
                    visibility = "visible" if display != 'none' else "invisible"
                    element_data[f"{label}"] = visibility
            
            # Scan for common properties on shapes
            for shape_type in config.SHAPE_TYPES:
                elements = svg_root.xpath(config.COMMON_XPATH_EXPRESSIONS["shape_element_base"].format(shape_type=shape_type), namespaces=config.SVG_NAMESPACES)
                for elem in elements:
                    label = elem.get('inkscape:label') or elem.get('id')
                    if label:
                        # Common properties to export
                        for prop in config.PROPERTIES_TO_CHECK:
                            value = elem.get(prop, '')
                            if value:  # Only include if property exists
                                element_data[f"{label}##{prop}"] = value
            
            if not element_data:
                if self.logger:
                    self.logger.warning("No elements with labels or IDs found in SVG")
                return False
            
            # Write CSV file
            #os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            csv_file = os.path.join(csv_path, config.EXPORT_CSV_FILENAME)
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = sorted(element_data.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerow(element_data)
            
            if self.logger:
                self.logger.info(f"Successfully exported {len(element_data)} elements/properties to CSV")
                self.logger.debug(f"CSV columns: {', '.join(sorted(element_data.keys()))}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error exporting SVG to CSV: {e}")
            return False
        