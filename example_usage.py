"""
Example usage of the Luzmo API + LLM Dashboard Analysis Pipeline
"""

from src.dashboard_summary_pipeline import DashboardSummaryPipeline


def example_basic_summary():
    """Example: Generate a basic summary of a dashboard."""
    print("Example 1: Basic Dashboard Summary")
    print("-" * 80)

    # Initialize pipeline (will use credentials from .env file)
    pipeline = DashboardSummaryPipeline(output_dir="./summaries")

    # Generate summary for a dashboard
    dashboard_id = "your-dashboard-id-here"

    result = pipeline.generate_summary(
        dashboard_id=dashboard_id,
        save_format="markdown"  # Options: 'text', 'markdown', 'json'
    )

    print(f"\nDashboard: {result['dashboard_name']}")
    print(f"Charts analyzed: {result['charts_analyzed']}")
    print(f"Summary saved to: {result['filepath']}")
    print(f"\nSummary preview:\n{result['summary'][:500]}...")


def example_structured_summary():
    """Example: Generate a structured summary with specific sections."""
    print("\nExample 2: Structured Summary")
    print("-" * 80)

    pipeline = DashboardSummaryPipeline(output_dir="./summaries")

    dashboard_id = "your-dashboard-id-here"

    result = pipeline.generate_structured_summary(
        dashboard_id=dashboard_id,
        sections=["overview", "key_metrics", "trends", "insights", "recommendations"]
    )

    print(f"\nDashboard: {result['dashboard_name']}")
    print(f"Sections generated: {', '.join(result['sections'])}")
    print(f"Summary saved to: {result['filepath']}")


def example_custom_analysis():
    """Example: Generate summary with custom analysis instructions."""
    print("\nExample 3: Custom Analysis")
    print("-" * 80)

    pipeline = DashboardSummaryPipeline(output_dir="./summaries")

    dashboard_id = "your-dashboard-id-here"

    custom_prompt = """
    Focus on:
    1. Month-over-month growth rates
    2. Top 3 performing products/categories
    3. Any concerning trends or red flags
    4. Recommendations for improvement
    """

    result = pipeline.generate_summary(
        dashboard_id=dashboard_id,
        custom_prompt=custom_prompt,
        save_format="markdown"
    )

    print(f"\nCustom analysis completed")
    print(f"Summary saved to: {result['filepath']}")


def example_compare_dashboards():
    """Example: Compare two dashboards."""
    print("\nExample 4: Dashboard Comparison")
    print("-" * 80)

    pipeline = DashboardSummaryPipeline(output_dir="./summaries")

    dashboard_id1 = "dashboard-1-id"
    dashboard_id2 = "dashboard-2-id"

    result = pipeline.compare_dashboards(
        dashboard_id1=dashboard_id1,
        dashboard_id2=dashboard_id2,
        comparison_focus="Sales performance and customer metrics"
    )

    print(f"\nComparison completed")
    print(f"Dashboards compared: {result['dashboard_ids']}")
    print(f"Comparison saved to: {result['filepath']}")


def example_answer_question():
    """Example: Answer a specific question about a dashboard."""
    print("\nExample 5: Answer Question")
    print("-" * 80)

    pipeline = DashboardSummaryPipeline(output_dir="./summaries")

    dashboard_id = "your-dashboard-id-here"
    question = "What was the total revenue in the last quarter and how does it compare to the previous quarter?"

    answer = pipeline.answer_question(dashboard_id, question)

    print(f"\nQuestion: {question}")
    print(f"Answer: {answer}")


def example_batch_processing():
    """Example: Process multiple dashboards in batch."""
    print("\nExample 6: Batch Processing")
    print("-" * 80)

    pipeline = DashboardSummaryPipeline(output_dir="./summaries")

    dashboard_ids = [
        "dashboard-1-id",
        "dashboard-2-id",
        "dashboard-3-id"
    ]

    results = pipeline.batch_process_dashboards(
        dashboard_ids=dashboard_ids,
        save_format="markdown"
    )

    print(f"\nBatch processing results:")
    for result in results:
        if result['success']:
            print(f"✓ {result['dashboard_id']}: Success")
        else:
            print(f"✗ {result['dashboard_id']}: {result['error']}")


if __name__ == "__main__":
    # Run the examples
    # Uncomment the examples you want to run

    # example_basic_summary()
    # example_structured_summary()
    # example_custom_analysis()
    # example_compare_dashboards()
    # example_answer_question()
    # example_batch_processing()

    print("\n" + "="*80)
    print("To run these examples:")
    print("1. Copy .env.example to .env and add your API credentials")
    print("2. Uncomment the example you want to run")
    print("3. Replace 'your-dashboard-id-here' with actual dashboard IDs")
    print("4. Run: python example_usage.py")
    print("="*80)
