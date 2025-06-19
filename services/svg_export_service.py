"""
SVG Export Service for Element Designer.
"""
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, Dict, Any
from models.window_element import WindowElement, WindowType, ProfileType
from utils.logger import get_logger

logger = get_logger(__name__)


class SVGExportService:
    """Service for exporting window elements as SVG."""
    
    def __init__(self):
        """Initialize SVG export service."""
        self.template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'schnitt')
        
    def export_window_element(self, window_type: WindowType, export_path: str, 
                            project_name: str = "Unbenanntes Projekt") -> bool:
        """
        Export a window element as SVG.
        
        Args:
            window_type: The window type to export
            export_path: Path where to save the SVG file
            project_name: Name of the current project
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Create SVG document
            svg_content = self._create_svg_document(window_type, project_name)
            
            # Write to file
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
                
            logger.info(f"SVG exported successfully: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"SVG export failed: {e}")
            return False
    
    def _create_svg_document(self, window_type: WindowType, project_name: str) -> str:
        """
        Create SVG document content for window type.
        
        Args:
            window_type: Window type to create SVG for
            project_name: Project name for metadata
            
        Returns:
            SVG content as string
        """
        # SVG header with metadata
        svg_header = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" viewBox="0 0 800 600" 
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink">
  
  <!-- Metadata -->
  <metadata>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <rdf:Description>
        <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">
          {window_type.display_name} - {project_name}
        </dc:title>
        <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">
          ElementDesigner v1.0
        </dc:creator>
        <dc:date xmlns:dc="http://purl.org/dc/elements/1.1/">
          {datetime.now().isoformat()}
        </dc:date>
        <dc:description xmlns:dc="http://purl.org/dc/elements/1.1/">
          {window_type.description}
        </dc:description>
      </rdf:Description>
    </rdf:RDF>
  </metadata>
  
  <!-- Styles -->
  <defs>
    <style type="text/css"><![CDATA[
      .frame {{ fill: none; stroke: #2c3e50; stroke-width: 3; }}
      .sash {{ fill: none; stroke: #34495e; stroke-width: 2; }}
      .glass {{ fill: #ecf0f1; stroke: #bdc3c7; stroke-width: 1; opacity: 0.7; }}
      .hardware {{ fill: #7f8c8d; stroke: #2c3e50; stroke-width: 1; }}
      .dimension {{ fill: none; stroke: #e74c3c; stroke-width: 1; }}
      .text {{ font-family: Arial, sans-serif; font-size: 12px; fill: #2c3e50; }}
      .title {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #2c3e50; }}
    ]]></style>
  </defs>
  
  <!-- Background -->
  <rect width="800" height="600" fill="#ffffff"/>
  
  <!-- Title -->
  <text x="400" y="30" text-anchor="middle" class="title">
    {window_type.code} - {window_type.display_name}
  </text>
  
  <!-- Window drawing -->
  <g transform="translate(200, 100)">
'''
        
        # Add window-specific geometry
        window_geometry = self._get_window_geometry(window_type)
        
        # SVG footer
        svg_footer = '''
  </g>
  
  <!-- Legend -->
  <g transform="translate(50, 500)">
    <text x="0" y="0" class="text">Legende:</text>
    <line x1="0" y1="15" x2="20" y2="15" class="frame"/>
    <text x="25" y="19" class="text">Blendrahmen</text>
    <line x1="0" y1="35" x2="20" y2="35" class="sash"/>
    <text x="25" y="39" class="text">Flügelrahmen</text>
    <rect x="0" y="45" width="20" height="10" class="glass"/>
    <text x="25" y="54" class="text">Verglasung</text>
  </g>
  
</svg>'''
        
        return svg_header + window_geometry + svg_footer
    
    def _get_window_geometry(self, window_type: WindowType) -> str:
        """
        Get SVG geometry for specific window type.
        
        Args:
            window_type: Window type to generate geometry for
            
        Returns:
            SVG geometry as string
        """
        # Basic window dimensions
        width = 400
        height = 300
        frame_width = 10
        
        if window_type == WindowType.FT_F:
            # Fixed window - just frame and glass
            return f'''
    <!-- Fixed Window -->
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    <rect x="{frame_width}" y="{frame_width}" 
          width="{width - 2*frame_width}" height="{height - 2*frame_width}" class="glass"/>
    
    <!-- Dimensions -->
    <g class="dimension">
      <line x1="-20" y1="0" x2="-20" y2="{height}"/>
      <line x1="-25" y1="0" x2="-15" y2="0"/>
      <line x1="-25" y1="{height}" x2="-15" y2="{height}"/>
      <text x="-35" y="{height//2}" class="text" transform="rotate(-90, -35, {height//2})">{height}mm</text>
    </g>
    
    <g class="dimension">
      <line x1="0" y1="-20" x2="{width}" y2="-20"/>
      <line x1="0" y1="-25" x2="0" y2="-15"/>
      <line x1="{width}" y1="-25" x2="{width}" y2="-15"/>
      <text x="{width//2}" y="-10" class="text" text-anchor="middle">{width}mm</text>
    </g>
'''
        
        elif window_type == WindowType.FT_D:
            # Turn window - frame, sash, glass, hinges
            sash_offset = 15
            return f'''
    <!-- Turn Window -->
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    <rect x="{sash_offset}" y="{sash_offset}" 
          width="{width - 2*sash_offset}" height="{height - 2*sash_offset}" class="sash"/>
    <rect x="{sash_offset + 5}" y="{sash_offset + 5}" 
          width="{width - 2*sash_offset - 10}" height="{height - 2*sash_offset - 10}" class="glass"/>
    
    <!-- Hinges -->
    <rect x="5" y="30" width="8" height="15" class="hardware"/>
    <rect x="5" y="{height//2 - 7}" width="8" height="15" class="hardware"/>
    <rect x="5" y="{height - 45}" width="8" height="15" class="hardware"/>
    
    <!-- Handle -->
    <circle cx="{width - 30}" cy="{height//2}" r="6" class="hardware"/>
'''
        
        elif window_type == WindowType.FT_DK:
            # Turn-tilt window - frame, sash, glass, hardware
            sash_offset = 15
            return f'''
    <!-- Turn-Tilt Window -->
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    <rect x="{sash_offset}" y="{sash_offset}" 
          width="{width - 2*sash_offset}" height="{height - 2*sash_offset}" class="sash"/>
    <rect x="{sash_offset + 5}" y="{sash_offset + 5}" 
          width="{width - 2*sash_offset - 10}" height="{height - 2*sash_offset - 10}" class="glass"/>
    
    <!-- Turn hinges -->
    <rect x="5" y="30" width="8" height="15" class="hardware"/>
    <rect x="5" y="{height - 45}" width="8" height="15" class="hardware"/>
    
    <!-- Tilt hardware -->
    <rect x="50" y="{height - 10}" width="15" height="8" class="hardware"/>
    <rect x="{width - 65}" y="{height - 10}" width="15" height="8" class="hardware"/>
    
    <!-- Handle -->
    <circle cx="{width - 30}" cy="{height//2}" r="6" class="hardware"/>
    <text x="{width - 30}" y="{height//2 + 25}" class="text" text-anchor="middle" font-size="8">DK</text>
'''
        
        elif window_type == WindowType.FT_HS:
            # Lift-slide - multiple panels
            panel_width = width // 2
            return f'''
    <!-- Lift-Slide Window -->
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    
    <!-- Fixed panel -->
    <rect x="{frame_width}" y="{frame_width}" 
          width="{panel_width - frame_width}" height="{height - 2*frame_width}" class="glass"/>
    
    <!-- Sliding panel -->
    <rect x="{panel_width + 5}" y="{frame_width}" 
          width="{panel_width - frame_width - 5}" height="{height - 2*frame_width}" class="sash"/>
    <rect x="{panel_width + 10}" y="{frame_width + 5}" 
          width="{panel_width - frame_width - 15}" height="{height - 2*frame_width - 10}" class="glass"/>
    
    <!-- Track -->
    <line x1="0" y1="{height - 5}" x2="{width}" y2="{height - 5}" class="hardware" stroke-width="3"/>
    
    <!-- Handle -->
    <rect x="{width - 20}" y="{height//2 - 20}" width="4" height="40" class="hardware"/>
'''
        
        else:
            # Default window for other types
            return f'''
    <!-- {window_type.display_name} -->
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    <rect x="{frame_width}" y="{frame_width}" 
          width="{width - 2*frame_width}" height="{height - 2*frame_width}" class="glass"/>
    
    <!-- Type indicator -->
    <text x="{width//2}" y="{height//2}" class="text" text-anchor="middle" font-size="24" opacity="0.3">
      {window_type.code}
    </text>
'''