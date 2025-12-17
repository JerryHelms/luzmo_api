"""
Summary Writer
Handles saving dashboard summaries to external files.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class SummaryWriter:
    """Writes dashboard summaries to files in various formats."""

    def __init__(self, output_dir: str = "./summaries"):
        """
        Initialize summary writer.

        Args:
            output_dir: Directory to save summaries
        """
        self.output_dir = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def _generate_filename(
        self,
        dashboard_id: str,
        extension: str = "txt",
        prefix: str = "summary"
    ) -> str:
        """
        Generate filename for summary.

        Args:
            dashboard_id: Dashboard ID
            extension: File extension
            prefix: Filename prefix

        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{dashboard_id}_{timestamp}.{extension}"

    def save_text_summary(
        self,
        dashboard_id: str,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Save summary as text file.

        Args:
            dashboard_id: Dashboard ID
            summary: Summary text
            metadata: Optional metadata to include
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if filename is None:
            filename = self._generate_filename(dashboard_id, "txt")

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write("="*80 + "\n")
            f.write(f"DASHBOARD SUMMARY\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Dashboard ID: {dashboard_id}\n")

            if metadata:
                f.write(f"Dashboard Name: {metadata.get('dashboard_name', 'N/A')}\n")
                if metadata.get('description'):
                    f.write(f"Description: {metadata.get('description')}\n")

            f.write("="*80 + "\n\n")

            # Write summary
            f.write(summary)
            f.write("\n\n")
            f.write("="*80 + "\n")

        return filepath

    def save_json_summary(
        self,
        dashboard_id: str,
        summary: str,
        dashboard_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Save summary with full data as JSON.

        Args:
            dashboard_id: Dashboard ID
            summary: Summary text
            dashboard_data: Complete dashboard data
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if filename is None:
            filename = self._generate_filename(dashboard_id, "json")

        filepath = os.path.join(self.output_dir, filename)

        output = {
            "dashboard_id": dashboard_id,
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "dashboard_data": dashboard_data
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        return filepath

    def save_markdown_summary(
        self,
        dashboard_id: str,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Save summary as markdown file.

        Args:
            dashboard_id: Dashboard ID
            summary: Summary text
            metadata: Optional metadata to include
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if filename is None:
            filename = self._generate_filename(dashboard_id, "md")

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Dashboard Summary\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**Dashboard ID:** {dashboard_id}  \n")

            if metadata:
                f.write(f"**Dashboard Name:** {metadata.get('dashboard_name', 'N/A')}  \n")
                if metadata.get('description'):
                    f.write(f"**Description:** {metadata.get('description')}  \n")

            f.write("\n---\n\n")

            # Write summary
            f.write(summary)
            f.write("\n")

        return filepath

    def save_structured_summary(
        self,
        dashboard_id: str,
        structured_summary: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Save structured summary as markdown with sections.

        Args:
            dashboard_id: Dashboard ID
            structured_summary: Dictionary with sections
            metadata: Optional metadata to include
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if filename is None:
            filename = self._generate_filename(dashboard_id, "md", "structured_summary")

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Dashboard Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**Dashboard ID:** {dashboard_id}  \n")

            if metadata:
                f.write(f"**Dashboard Name:** {metadata.get('dashboard_name', 'N/A')}  \n")
                if metadata.get('description'):
                    f.write(f"**Description:** {metadata.get('description')}  \n")

            f.write("\n---\n\n")

            # Write sections
            for section_name, section_content in structured_summary.items():
                section_title = section_name.replace('_', ' ').title()
                f.write(f"## {section_title}\n\n")
                f.write(section_content)
                f.write("\n\n")

        return filepath

    def append_to_log(
        self,
        dashboard_id: str,
        summary: str,
        log_filename: str = "dashboard_summaries_log.txt"
    ) -> str:
        """
        Append summary to a running log file.

        Args:
            dashboard_id: Dashboard ID
            summary: Summary text
            log_filename: Log filename

        Returns:
            Path to log file
        """
        filepath = os.path.join(self.output_dir, log_filename)

        with open(filepath, 'a', encoding='utf-8') as f:
            f.write("\n" + "="*80 + "\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Dashboard ID: {dashboard_id}\n")
            f.write("-"*80 + "\n")
            f.write(summary)
            f.write("\n" + "="*80 + "\n\n")

        return filepath

    def list_summaries(self) -> list:
        """
        List all saved summaries.

        Returns:
            List of summary files
        """
        summaries = []
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            if os.path.isfile(filepath):
                summaries.append({
                    'filename': filename,
                    'path': filepath,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath))
                })

        return sorted(summaries, key=lambda x: x['modified'], reverse=True)
