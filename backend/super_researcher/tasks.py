import asyncio
from celery import shared_task


@shared_task
def product_engine_research():
    """
    Periodic task that runs the product-engine research pipeline hourly.
    Uses the question from prompting.py as the search query.
    Saves reliability/urgency scores to Weaviate and creates SuperResearcher leads.
    """
    from .product_engine import run_pipeline
    from .prompting import question
    from .models import SuperResearcher

    print("Starting product-engine research pipeline...")
    print(f"Search query: {question}")

    try:
        result = asyncio.run(run_pipeline(question))

        # Extract urgency output (contains the main data to save)
        urgency_output = result.get('urgency', [])
        reliability_output = result.get('reliability', {})

        # Map reliability scores to URLs for easy lookup
        reliability_map = {
            r_item['url']: r_item['score']
            for r_item in reliability_output.get('rankings', [])
        }

        # Save each result as a SuperResearcher lead
        leads_created = 0
        leads_updated = 0

        for item in urgency_output:
            url = item.get('url')
            urgency_score = item.get('urgency_score', 0)
            reliability_score = reliability_map.get(url, 0)

            # Check if lead already exists by source_url
            existing_lead = SuperResearcher.objects.filter(source_url=url).first()

            # Prepare combined data as JSON
            data = {
                'title': item.get('title', 'No Title'),
                'snippet': item.get('snippet', ''),
                'date': item.get('date', 'N/A'),
                'urgency_score': urgency_score,
                'reliability_score': reliability_score,
                'top_urgency_indicators': item.get('top_urgency_indicators', []),
                'search_query': result.get('search_query', question),
            }

            if existing_lead:
                # Update existing lead with new research data
                existing_lead.data = data
                existing_lead.save()
                leads_updated += 1
            else:
                # Determine result type based on content
                result_type = 'company'  # Default to company

                # Create new lead
                SuperResearcher.objects.create(
                    result=result_type,
                    data=data,
                    source_url=url,
                )
                leads_created += 1

        reliability_count = len(result.get('reliability', {}).get('rankings', []))
        urgency_count = len(result.get('urgency', []))

        print(f"Successfully completed research pipeline")
        print(f"- Found {reliability_count} reliability rankings")
        print(f"- Analyzed {urgency_count} items for urgency")
        print(f"- Created {leads_created} new leads")
        print(f"- Updated {leads_updated} existing leads")
        print(f"- Data saved to Weaviate and SuperResearcher model")

        return {
            'success': True,
            'search_query': question,
            'reliability_count': reliability_count,
            'urgency_count': urgency_count,
            'leads_created': leads_created,
            'leads_updated': leads_updated,
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
