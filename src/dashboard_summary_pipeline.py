"""
Dashboard Summary Pipeline
Main orchestrator that combines all components to analyze dashboards and generate summaries.
"""

from typing import Optional, Dict, Any
from .luzmo_client import LuzmoClient
from .dashboard_analyzer import DashboardAnalyzer
from .llm_analyzer import LLMAnalyzer
from .summary_writer import SummaryWriter


class DashboardSummaryPipeline:
    """
    Complete pipeline for analyzing Luzmo dashboards and generating AI-powered summaries.
    """

    def __init__(
        self,
        luzmo_api_key: Optional[str] = None,
        luzmo_api_token: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        output_dir: str = "./summaries"
    ):
        """
        Initialize the pipeline with all required components.

        Args:
            luzmo_api_key: Luzmo API key
            luzmo_api_token: Luzmo API token
            anthropic_api_key: Anthropic API key
            output_dir: Directory for saving summaries
        """
        self.luzmo_client = LuzmoClient(api_key=luzmo_api_key, api_token=luzmo_api_token)
        self.analyzer = DashboardAnalyzer(self.luzmo_client)
        self.llm_analyzer = LLMAnalyzer(api_key=anthropic_api_key)
        self.writer = SummaryWriter(output_dir=output_dir)

    def generate_summary(
        self,
        dashboard_id: str,
        custom_prompt: Optional[str] = None,
        save_format: str = "markdown",
        include_raw_data: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a complete summary for a dashboard.

        Args:
            dashboard_id: Dashboard ID
            custom_prompt: Optional custom analysis instructions
            save_format: Output format ('text', 'markdown', 'json')
            include_raw_data: Whether to save raw data (only for JSON format)

        Returns:
            Dictionary with summary info and file path
        """
        print(f"Fetching dashboard data for {dashboard_id}...")
        dashboard_data = self.analyzer.get_full_dashboard_data(dashboard_id)

        print("Formatting data for LLM analysis...")
        formatted_data = self.analyzer.format_for_llm(dashboard_data)

        print("Generating summary with Claude...")
        summary = self.llm_analyzer.generate_summary(formatted_data, custom_prompt)

        print(f"Saving summary as {save_format}...")
        metadata = dashboard_data['metadata']

        if save_format == "json":
            if include_raw_data:
                filepath = self.writer.save_json_summary(dashboard_id, summary, dashboard_data)
            else:
                filepath = self.writer.save_json_summary(dashboard_id, summary, {'metadata': metadata})
        elif save_format == "markdown":
            filepath = self.writer.save_markdown_summary(dashboard_id, summary, metadata)
        else:  # text
            filepath = self.writer.save_text_summary(dashboard_id, summary, metadata)

        print(f"Summary saved to: {filepath}")

        return {
            'dashboard_id': dashboard_id,
            'dashboard_name': metadata['dashboard_name'],
            'summary': summary,
            'filepath': filepath,
            'charts_analyzed': len(metadata['charts'])
        }

    def generate_structured_summary(
        self,
        dashboard_id: str,
        sections: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured summary with multiple sections.

        Args:
            dashboard_id: Dashboard ID
            sections: List of sections to include

        Returns:
            Dictionary with summary info and file path
        """
        print(f"Fetching dashboard data for {dashboard_id}...")
        dashboard_data = self.analyzer.get_full_dashboard_data(dashboard_id)

        print("Formatting data for LLM analysis...")
        formatted_data = self.analyzer.format_for_llm(dashboard_data)

        print("Generating structured summary with Claude...")
        structured_summary = self.llm_analyzer.generate_structured_summary(formatted_data, sections)

        print("Saving structured summary...")
        metadata = dashboard_data['metadata']
        filepath = self.writer.save_structured_summary(dashboard_id, structured_summary, metadata)

        print(f"Structured summary saved to: {filepath}")

        return {
            'dashboard_id': dashboard_id,
            'dashboard_name': metadata['dashboard_name'],
            'structured_summary': structured_summary,
            'filepath': filepath,
            'sections': list(structured_summary.keys())
        }

    def compare_dashboards(
        self,
        dashboard_id1: str,
        dashboard_id2: str,
        comparison_focus: Optional[str] = None,
        save_format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Compare two dashboards and generate a comparison summary.

        Args:
            dashboard_id1: First dashboard ID
            dashboard_id2: Second dashboard ID
            comparison_focus: Optional focus area
            save_format: Output format

        Returns:
            Dictionary with comparison info and file path
        """
        print(f"Fetching data for dashboard {dashboard_id1}...")
        dashboard1_data = self.analyzer.get_full_dashboard_data(dashboard_id1)
        formatted_data1 = self.analyzer.format_for_llm(dashboard1_data)

        print(f"Fetching data for dashboard {dashboard_id2}...")
        dashboard2_data = self.analyzer.get_full_dashboard_data(dashboard_id2)
        formatted_data2 = self.analyzer.format_for_llm(dashboard2_data)

        print("Generating comparison with Claude...")
        comparison = self.llm_analyzer.compare_dashboards(formatted_data1, formatted_data2, comparison_focus)

        print("Saving comparison...")
        filename = f"comparison_{dashboard_id1}_vs_{dashboard_id2}"

        if save_format == "markdown":
            filepath = self.writer.save_markdown_summary(
                f"{dashboard_id1}_vs_{dashboard_id2}",
                comparison,
                {
                    'dashboard_name': f"Comparison: {dashboard1_data['metadata']['dashboard_name']} vs {dashboard2_data['metadata']['dashboard_name']}"
                },
                filename=f"{filename}.md"
            )
        else:
            filepath = self.writer.save_text_summary(
                f"{dashboard_id1}_vs_{dashboard_id2}",
                comparison,
                {
                    'dashboard_name': f"Comparison: {dashboard1_data['metadata']['dashboard_name']} vs {dashboard2_data['metadata']['dashboard_name']}"
                },
                filename=f"{filename}.txt"
            )

        print(f"Comparison saved to: {filepath}")

        return {
            'dashboard_ids': [dashboard_id1, dashboard_id2],
            'comparison': comparison,
            'filepath': filepath
        }

    def answer_question(
        self,
        dashboard_id: str,
        question: str
    ) -> str:
        """
        Answer a specific question about a dashboard.

        Args:
            dashboard_id: Dashboard ID
            question: Question to answer

        Returns:
            Answer text
        """
        print(f"Fetching dashboard data for {dashboard_id}...")
        dashboard_data = self.analyzer.get_full_dashboard_data(dashboard_id)

        print("Formatting data for LLM analysis...")
        formatted_data = self.analyzer.format_for_llm(dashboard_data)

        print("Getting answer from Claude...")
        answer = self.llm_analyzer.answer_question(formatted_data, question)

        return answer

    def batch_process_dashboards(
        self,
        dashboard_ids: list,
        custom_prompt: Optional[str] = None,
        save_format: str = "markdown"
    ) -> list:
        """
        Process multiple dashboards in batch.

        Args:
            dashboard_ids: List of dashboard IDs
            custom_prompt: Optional custom prompt for all
            save_format: Output format

        Returns:
            List of results for each dashboard
        """
        results = []

        for i, dashboard_id in enumerate(dashboard_ids, 1):
            print(f"\n{'='*80}")
            print(f"Processing dashboard {i}/{len(dashboard_ids)}: {dashboard_id}")
            print(f"{'='*80}\n")

            try:
                result = self.generate_summary(dashboard_id, custom_prompt, save_format)
                results.append({
                    'success': True,
                    'dashboard_id': dashboard_id,
                    'result': result
                })
            except Exception as e:
                print(f"Error processing {dashboard_id}: {str(e)}")
                results.append({
                    'success': False,
                    'dashboard_id': dashboard_id,
                    'error': str(e)
                })

        print(f"\n{'='*80}")
        print(f"Batch processing complete: {sum(1 for r in results if r['success'])}/{len(dashboard_ids)} successful")
        print(f"{'='*80}\n")

        return results
