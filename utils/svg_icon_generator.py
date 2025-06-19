"""
SVG Icon Generator for Window Types.
Generates clean SVG icons to replace PNG files.
"""
import os
from models.window_element import WindowType


class SVGIconGenerator:
    """Generator for clean SVG icons of window types."""
    
    def __init__(self):
        """Initialize SVG icon generator."""
        self.icon_size = 64
        self.icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons', 'fenster_types')
        
    def generate_all_icons(self):
        """Generate SVG icons for all window types."""
        os.makedirs(self.icon_path, exist_ok=True)
        
        for window_type in WindowType:
            svg_content = self._create_window_icon(window_type)
            icon_file = os.path.join(self.icon_path, f"{window_type.code}.svg")
            
            with open(icon_file, 'w', encoding='utf-8') as f:
                f.write(svg_content)
                
        print(f"Generated {len(WindowType)} SVG icons in {self.icon_path}")
        
    def _create_window_icon(self, window_type: WindowType) -> str:
        """
        Create SVG icon for specific window type.
        
        Args:
            window_type: Window type to create icon for
            
        Returns:
            SVG content as string
        """
        size = self.icon_size
        
        svg_header = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" 
     xmlns="http://www.w3.org/2000/svg">
  
  <defs>
    <style type="text/css"><![CDATA[
      .frame {{ fill: none; stroke: #2c3e50; stroke-width: 2; }}
      .sash {{ fill: none; stroke: #34495e; stroke-width: 1.5; }}
      .glass {{ fill: #ecf0f1; stroke: #bdc3c7; stroke-width: 0.5; opacity: 0.8; }}
      .hardware {{ fill: #7f8c8d; stroke: #2c3e50; stroke-width: 0.5; }}
      .direction {{ fill: none; stroke: #e74c3c; stroke-width: 1; }}
    ]]></style>
  </defs>
  
  <rect width="{size}" height="{size}" fill="#ffffff" rx="4"/>
'''
        
        # Get window-specific geometry
        icon_geometry = self._get_icon_geometry(window_type, size)
        
        svg_footer = '</svg>'
        
        return svg_header + icon_geometry + svg_footer
    
    def _get_icon_geometry(self, window_type: WindowType, size: int) -> str:
        """Get SVG geometry for window type icon."""
        margin = 8
        width = size - 2 * margin
        height = width * 0.75  # 4:3 aspect ratio
        x = margin
        y = (size - height) // 2
        frame_width = 3
        
        if window_type == WindowType.FT_F:
            # Fixed window - simple frame
            return f'''
  <g transform="translate({x}, {y})">
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    <rect x="{frame_width}" y="{frame_width}" 
          width="{width - 2*frame_width}" height="{height - 2*frame_width}" class="glass"/>
  </g>
'''
        
        elif window_type == WindowType.FT_D:
            # Turn window - with hinge indication
            return f'''
  <g transform="translate({x}, {y})">
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    <rect x="{frame_width}" y="{frame_width}" 
          width="{width - 2*frame_width}" height="{height - 2*frame_width}" class="sash"/>
    <rect x="{frame_width + 2}" y="{frame_width + 2}" 
          width="{width - 2*frame_width - 4}" height="{height - 2*frame_width - 4}" class="glass"/>
    
    <!-- Hinges -->
    <rect x="1" y="{height * 0.2}" width="4" height="6" class="hardware"/>
    <rect x="1" y="{height * 0.7}" width="4" height="6" class="hardware"/>
    
    <!-- Opening direction -->
    <path d="M {width * 0.7} {height * 0.5} L {width * 0.9} {height * 0.4} L {width * 0.9} {height * 0.6} Z" 
          class="direction"/>
  </g>
'''
        
        elif window_type == WindowType.FT_K:
            # Tilt window - with tilt indication
            return f'''
  <g transform="translate({x}, {y})">
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    <rect x="{frame_width}" y="{frame_width}" 
          width="{width - 2*frame_width}" height="{height - 2*frame_width}" class="sash"/>
    <rect x="{frame_width + 2}" y="{frame_width + 2}" 
          width="{width - 2*frame_width - 4}" height="{height - 2*frame_width - 4}" class="glass"/>
    
    <!-- Tilt hardware -->
    <rect x="{width * 0.3}" y="{height - 4}" width="8" height="3" class="hardware"/>
    <rect x="{width * 0.6}" y="{height - 4}" width="8" height="3" class="hardware"/>
    
    <!-- Tilt direction -->
    <path d="M {width * 0.2} {height * 0.15} L {width * 0.8} {height * 0.05} L {width * 0.8} {height * 0.25}" 
          class="direction" fill="none"/>
  </g>
'''
        
        elif window_type == WindowType.FT_DK:
            # Turn-tilt window - combined indicators
            return f'''
  <g transform="translate({x}, {y})">
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    <rect x="{frame_width}" y="{frame_width}" 
          width="{width - 2*frame_width}" height="{height - 2*frame_width}" class="sash"/>
    <rect x="{frame_width + 2}" y="{frame_width + 2}" 
          width="{width - 2*frame_width - 4}" height="{height - 2*frame_width - 4}" class="glass"/>
    
    <!-- Turn hinges -->
    <rect x="1" y="{height * 0.25}" width="3" height="5" class="hardware"/>
    <rect x="1" y="{height * 0.65}" width="3" height="5" class="hardware"/>
    
    <!-- Tilt hardware -->
    <rect x="{width * 0.4}" y="{height - 3}" width="6" height="2" class="hardware"/>
    
    <!-- Handle -->
    <circle cx="{width - 8}" cy="{height * 0.5}" r="2" class="hardware"/>
  </g>
'''
        
        elif window_type == WindowType.FT_DD:
            # Double turn windows
            mid = width // 2
            return f'''
  <g transform="translate({x}, {y})">
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    <!-- Left sash -->
    <rect x="{frame_width}" y="{frame_width}" 
          width="{mid - frame_width - 1}" height="{height - 2*frame_width}" class="sash"/>
    <rect x="{frame_width + 2}" y="{frame_width + 2}" 
          width="{mid - frame_width - 5}" height="{height - 2*frame_width - 4}" class="glass"/>
    <!-- Right sash -->
    <rect x="{mid + 1}" y="{frame_width}" 
          width="{mid - frame_width - 1}" height="{height - 2*frame_width}" class="sash"/>
    <rect x="{mid + 3}" y="{frame_width + 2}" 
          width="{mid - frame_width - 5}" height="{height - 2*frame_width - 4}" class="glass"/>
    
    <!-- Mullion -->
    <rect x="{mid - 1}" y="0" width="2" height="{height}" class="frame"/>
    
    <!-- Hinges -->
    <rect x="1" y="{height * 0.3}" width="3" height="4" class="hardware"/>
    <rect x="{width - 4}" y="{height * 0.3}" width="3" height="4" class="hardware"/>
  </g>
'''
        
        elif window_type == WindowType.FT_HS:
            # Lift-slide window
            panel_width = width // 2
            return f'''
  <g transform="translate({x}, {y})">
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    
    <!-- Fixed panel -->
    <rect x="{frame_width}" y="{frame_width}" 
          width="{panel_width - frame_width}" height="{height - 2*frame_width}" class="glass"/>
    
    <!-- Sliding panel -->
    <rect x="{panel_width + 2}" y="{frame_width}" 
          width="{panel_width - frame_width - 2}" height="{height - 2*frame_width}" class="sash"/>
    <rect x="{panel_width + 4}" y="{frame_width + 2}" 
          width="{panel_width - frame_width - 6}" height="{height - 2*frame_width - 4}" class="glass"/>
    
    <!-- Track -->
    <line x1="0" y1="{height - 2}" x2="{width}" y2="{height - 2}" class="hardware" stroke-width="2"/>
    
    <!-- Slide direction -->
    <path d="M {width * 0.7} {height * 0.9} L {width * 0.9} {height * 0.85} L {width * 0.9} {height * 0.95} Z" 
          class="direction"/>
  </g>
'''
        
        else:
            # Default icon for other window types
            return f'''
  <g transform="translate({x}, {y})">
    <rect x="0" y="0" width="{width}" height="{height}" class="frame"/>
    <rect x="{frame_width}" y="{frame_width}" 
          width="{width - 2*frame_width}" height="{height - 2*frame_width}" class="glass"/>
    
    <!-- Type code -->
    <text x="{width//2}" y="{height//2 + 3}" text-anchor="middle" 
          font-family="Arial" font-size="8" fill="#2c3e50" font-weight="bold">
      {window_type.code.replace('FT_', '')}
    </text>
  </g>
'''


if __name__ == '__main__':
    generator = SVGIconGenerator()
    generator.generate_all_icons()