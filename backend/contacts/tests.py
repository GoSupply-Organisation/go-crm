from apex.models import apex_research
from super_researcher.models import SuperResearcher


# Method 1: create() method (most common)
apex_record = apex_research.objects.create(
      company="Tech Corp",
      website="https://techcorp.com",
      phone_number=5551234567,
      email="contact@techcorp.com",
      full_name="John Doe",
      promoted=False
  )
apex_record.save()

  # Method 2: Constructor + save()
super_record = SuperResearcher(
      company="Data Inc",
      website="https://datainc.com",
      phone_number=5559876543,
      email="info@datainc.com",
      full_name="Jane Smith",
      promoted=True
  )
super_record.save()

#   2. Bulk Creation (Fastest for multiple records)
