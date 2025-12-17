"""
LLM Analyzer
Uses Anthropic Claude to generate insights and summaries from dashboard data.
"""

import os
from typing import Dict, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class LLMAnalyzer:
    """Uses Claude to analyze dashboard data and generate summaries."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        """
        Initialize LLM analyzer.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use (default: claude-3-haiku-20240307)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def generate_summary(
        self,
        dashboard_data: str,
        custom_prompt: Optional[str] = None,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate a summary of the dashboard using Claude.

        Args:
            dashboard_data: Formatted dashboard data as text
            custom_prompt: Optional custom analysis prompt
            max_tokens: Maximum tokens in response

        Returns:
            Generated summary
        """
        system_prompt = """You are a data analyst expert. Your job is to analyze dashboard data and provide clear, insightful summaries.

Focus on:
1. Key metrics and their values
2. Trends and patterns in the data
3. Notable findings or outliers
4. What the dashboard is accomplishing/showing
5. Actionable insights

Be specific and use exact numbers from the data. Write in a clear, professional tone."""

        user_prompt = f"""Analyze this dashboard data and provide a comprehensive summary:

{dashboard_data}

"""
        if custom_prompt:
            user_prompt += f"\nAdditional instructions: {custom_prompt}"

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")

    def generate_structured_summary(
        self,
        dashboard_data: str,
        sections: Optional[list] = None
    ) -> Dict[str, str]:
        """
        Generate a structured summary with specific sections.

        Args:
            dashboard_data: Formatted dashboard data as text
            sections: List of sections to include (e.g., ["overview", "key_metrics", "insights"])

        Returns:
            Dictionary with sections as keys and summaries as values
        """
        if sections is None:
            sections = ["overview", "key_metrics", "insights", "recommendations"]

        system_prompt = """You are a data analyst expert. Provide structured analysis of dashboard data."""

        user_prompt = f"""Analyze this dashboard data and provide a structured response with the following sections:
{', '.join(sections)}

Dashboard Data:
{dashboard_data}

Format your response as:
## Section Name
[content]

For each requested section."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            response_text = message.content[0].text

            # Parse structured response
            structured = {}
            current_section = None
            current_content = []

            for line in response_text.split('\n'):
                if line.startswith('## '):
                    if current_section:
                        structured[current_section] = '\n'.join(current_content).strip()
                    current_section = line[3:].strip().lower().replace(' ', '_')
                    current_content = []
                elif current_section:
                    current_content.append(line)

            if current_section:
                structured[current_section] = '\n'.join(current_content).strip()

            return structured

        except Exception as e:
            raise Exception(f"Failed to generate structured summary: {str(e)}")

    def compare_dashboards(
        self,
        dashboard1_data: str,
        dashboard2_data: str,
        comparison_focus: Optional[str] = None
    ) -> str:
        """
        Compare two dashboards using Claude.

        Args:
            dashboard1_data: First dashboard data
            dashboard2_data: Second dashboard data
            comparison_focus: Optional focus area for comparison

        Returns:
            Comparison analysis
        """
        system_prompt = """You are a data analyst expert. Compare two dashboards and identify key differences, similarities, and insights."""

        user_prompt = f"""Compare these two dashboards:

DASHBOARD 1:
{dashboard1_data}

DASHBOARD 2:
{dashboard2_data}

Provide a comparison highlighting:
1. Key differences in metrics
2. Similarities
3. Which dashboard shows better performance (if applicable)
4. Unique insights from each
"""

        if comparison_focus:
            user_prompt += f"\n\nFocus particularly on: {comparison_focus}"

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            raise Exception(f"Failed to compare dashboards: {str(e)}")

    def answer_question(
        self,
        dashboard_data: str,
        question: str
    ) -> str:
        """
        Answer a specific question about the dashboard data.

        Args:
            dashboard_data: Formatted dashboard data
            question: Question to answer

        Returns:
            Answer based on the data
        """
        system_prompt = """You are a data analyst expert. Answer questions about dashboard data accurately using the exact numbers and information provided."""

        user_prompt = f"""Based on this dashboard data:

{dashboard_data}

Question: {question}

Provide a clear, accurate answer using specific numbers and details from the data."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            raise Exception(f"Failed to answer question: {str(e)}")
