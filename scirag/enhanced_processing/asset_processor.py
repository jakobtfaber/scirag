"""
Asset processing module for Enhanced SciRAG.

This module provides processing capabilities for figures, tables, and other
visual assets in scientific documents.
"""

import re
from typing import Dict, Any, Optional, List
from .enhanced_chunk import AssetContent


class AssetProcessor:
    """Asset processor for figures, tables, and other visual content."""
    
    def __init__(self):
        """Initialize asset processor."""
        self.figure_patterns = [
            r'\\begin\{figure\}',
            r'\\includegraphics',
            r'\\begin\{picture\}',
            r'\\begin\{tikzpicture\}'
        ]
        
        self.table_patterns = [
            r'\\begin\{table\}',
            r'\\begin\{tabular\}',
            r'\\begin\{array\}',
            r'\\begin\{longtable\}'
        ]
    
    def process_asset(self, text: str, source_id: str) -> Optional[AssetContent]:
        """
        Process asset content from text.
        
        Args:
            text: Text containing asset content
            source_id: Source document ID
            
        Returns:
            AssetContent object or None if no asset found
        """
        if not text:
            return None
        
        # Check for figures
        figure_content = self._process_figure(text, source_id)
        if figure_content:
            return figure_content
        
        # Check for tables
        table_content = self._process_table(text, source_id)
        if table_content:
            return table_content
        
        return None
    
    def _process_figure(self, text: str, source_id: str) -> Optional[AssetContent]:
        """Process figure content."""
        if not self._contains_figure(text):
            return None
        
        # Extract figure information
        caption = self._extract_caption(text)
        file_path = self._extract_file_path(text)
        alt_text = self._extract_alt_text(text)
        label = self._extract_label(text)
        
        return AssetContent(
            asset_type="figure",
            caption=caption,
            file_path=file_path,
            alt_text=alt_text,
            label=label,
            source_id=source_id
        )
    
    def _process_table(self, text: str, source_id: str) -> Optional[AssetContent]:
        """Process table content."""
        if not self._contains_table(text):
            return None
        
        # Extract table information
        caption = self._extract_caption(text)
        label = self._extract_label(text)
        table_data = self._extract_table_data(text)
        
        return AssetContent(
            asset_type="table",
            caption=caption,
            file_path=None,
            alt_text=None,
            label=label,
            source_id=source_id,
            table_data=table_data
        )
    
    def _contains_figure(self, text: str) -> bool:
        """Check if text contains figure content."""
        for pattern in self.figure_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _contains_table(self, text: str) -> bool:
        """Check if text contains table content."""
        for pattern in self.table_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_caption(self, text: str) -> Optional[str]:
        """Extract caption from asset content."""
        # Look for \caption{...} command
        caption_match = re.search(r'\\caption\{([^}]+)\}', text, re.IGNORECASE)
        if caption_match:
            return caption_match.group(1).strip()
        
        # Look for caption in figure environment
        figure_match = re.search(r'\\begin\{figure\}.*?\\caption\{([^}]+)\}', text, re.DOTALL | re.IGNORECASE)
        if figure_match:
            return figure_match.group(1).strip()
        
        return None
    
    def _extract_file_path(self, text: str) -> Optional[str]:
        """Extract file path from asset content."""
        # Look for \includegraphics{...} command
        graphics_match = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text, re.IGNORECASE)
        if graphics_match:
            return graphics_match.group(1).strip()
        
        return None
    
    def _extract_alt_text(self, text: str) -> Optional[str]:
        """Extract alt text from asset content."""
        # Look for alt text in \includegraphics options
        alt_match = re.search(r'\\includegraphics\[[^\]]*alt=\{([^}]+)\}[^\]]*\]', text, re.IGNORECASE)
        if alt_match:
            return alt_match.group(1).strip()
        
        return None
    
    def _extract_label(self, text: str) -> Optional[str]:
        """Extract label from asset content."""
        # Look for \label{...} command
        label_match = re.search(r'\\label\{([^}]+)\}', text, re.IGNORECASE)
        if label_match:
            return label_match.group(1).strip()
        
        return None
    
    def _extract_table_data(self, text: str) -> Optional[List[List[str]]]:
        """Extract table data from table content."""
        # Look for tabular environment
        tabular_match = re.search(r'\\begin\{tabular\}\{[^}]+\}(.*?)\\end\{tabular\}', text, re.DOTALL | re.IGNORECASE)
        if not tabular_match:
            return None
        
        tabular_content = tabular_match.group(1)
        
        # Split by rows (\\)
        rows = tabular_content.split('\\\\')
        
        table_data = []
        for row in rows:
            if not row.strip():
                continue
            
            # Split by columns (&)
            columns = row.split('&')
            row_data = [col.strip() for col in columns]
            table_data.append(row_data)
        
        return table_data if table_data else None
    
    def extract_all_assets(self, text: str, source_id: str) -> List[AssetContent]:
        """
        Extract all assets from text.
        
        Args:
            text: Text to extract assets from
            source_id: Source document ID
            
        Returns:
            List of AssetContent objects
        """
        assets = []
        
        # Split text into potential asset blocks
        asset_blocks = self._split_into_asset_blocks(text)
        
        for block in asset_blocks:
            asset = self.process_asset(block, source_id)
            if asset:
                assets.append(asset)
        
        return assets
    
    def _split_into_asset_blocks(self, text: str) -> List[str]:
        """Split text into potential asset blocks."""
        blocks = []
        
        # Split by figure environments
        figure_blocks = re.split(r'(\\begin\{figure\}.*?\\end\{figure\})', text, re.DOTALL)
        for block in figure_blocks:
            if block.strip():
                blocks.append(block)
        
        # Split by table environments
        table_blocks = re.split(r'(\\begin\{table\}.*?\\end\{table\})', text, re.DOTALL)
        for block in table_blocks:
            if block.strip():
                blocks.append(block)
        
        return blocks
    
    def get_asset_statistics(self, assets: List[AssetContent]) -> Dict[str, Any]:
        """
        Get statistics about assets.
        
        Args:
            assets: List of AssetContent objects
            
        Returns:
            Dictionary containing asset statistics
        """
        if not assets:
            return {}
        
        # Count asset types
        asset_type_counts = {}
        for asset in assets:
            asset_type = asset.asset_type
            asset_type_counts[asset_type] = asset_type_counts.get(asset_type, 0) + 1
        
        # Count assets with captions
        assets_with_captions = sum(1 for asset in assets if asset.caption)
        
        # Count assets with labels
        assets_with_labels = sum(1 for asset in assets if asset.label)
        
        return {
            'total_assets': len(assets),
            'asset_type_distribution': asset_type_counts,
            'assets_with_captions': assets_with_captions,
            'assets_with_labels': assets_with_labels,
            'caption_rate': assets_with_captions / len(assets) if assets else 0,
            'label_rate': assets_with_labels / len(assets) if assets else 0
        }