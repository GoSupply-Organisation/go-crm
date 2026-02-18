import asyncio
from celery import shared_task


@shared_task
def product_engine_research():
    """
    Periodic task that runs the product-engine research pipeline hourly.
    Uses the question from prompting.py as the search query.
    Saves reliability/urgency scores to Weaviate.
    """
    from .product_engine import run_pipeline
    from .prompting import question

    print("Starting product-engine research pipeline...")
    print(f"Search query: {question}")

    try:
        result = asyncio.run(run_pipeline(question))

        reliability_count = len(result.get('reliability', {}).get('rankings', []))
        urgency_count = len(result.get('urgency', []))

        print(f"Successfully completed research pipeline")
        print(f"- Found {reliability_count} reliability rankings")
        print(f"- Analyzed {urgency_count} items for urgency")
        print(f"- Data saved to Weaviate")

        return {
            'success': True,
            'search_query': question,
            'reliability_count': reliability_count,
            'urgency_count': urgency_count,
            'message': 'Research pipeline completed successfully'
        }

    except Exception as e:
        error_msg = f"Product engine research failed: {e}"
        print(error_msg)
        return {
            'success': False,
            'error': str(e),
            'message': 'Research pipeline failed'
        }
