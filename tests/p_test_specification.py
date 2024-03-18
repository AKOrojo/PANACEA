from src.unifying_model.mapper import m
from src.policy.specification import split_and_bind_policies_to_urp
from src.utils.util_functions import print_urp

# List of email documents, each structured as a separate document
email_documents = [
    {"_id": "email01", "email": {"header": "Subject: Test 1", "body": "I'm ready, are you?"}},
    {"_id": "email02", "email": {"header": "Subject: Test 2", "body": "Meeting at 10 AM."}},
    {"_id": "email03", "email": {"header": "Subject: Test 3", "body": "Lunch at noon?"}},
    {"_id": "email04", "email": {"header": "Subject: Test 4", "body": "Project deadline reminder."}},
    {"_id": "email05", "email": {"header": "Subject: Test 5", "body": "Friday's agenda."}},
    {"_id": "email06", "email": {"header": "Subject: Test 6", "body": "Updated proposal attached."}},
    {"_id": "email07", "email": {"header": "Subject: Test 7", "body": "Happy Birthday wishes!"}},
    {"_id": "email08", "email": {"header": "Subject: Test 8", "body": "Training session next week."}},
    {"_id": "email09", "email": {"header": "Subject: Test 9", "body": "Important security update."}},
    {"_id": "email10", "email": {"header": "Subject: Test 10", "body": "Team building event."}}
]

# Initialize an empty list to hold the mapped results for all emails
mapped_results_all_emails = []

# Iterate over the list of email documents, processing each through the m function
for email_document in email_documents:
    mapped_result = m(email_document)
    mapped_results_all_emails.append(mapped_result)

flat_mapped_results = [item for sublist in mapped_results_all_emails for item in sublist]

print_urp(mapped_results_all_emails)

security_metadata_variations = [
    [{"aip": ["research"]}],
    [{"aip": ["administration"]}],
    [{"aip": ["marketing"]}],
    [{"aip": ["finance"]}],
    [{"aip": ["engineering"]}],
]

policy_variations = [
    # Group 1 policies: Positive access for research
    [{"exp": "s.ap in meta.aip", "tp": "positive"}],

    # Group 2 policies: Negative access for administration
    [{"exp": "s.ap not in meta.aip", "tp": "negative"}],

    # Group 3 policies: Mixed, positive for marketing but with conditions
    [{"exp": "s.role == 'Manager' and s.ap in meta.aip", "tp": "positive"}],

    # Group 4 policies: Positive access during specific times
    [{"exp": "s.ap in meta.aip and s.time == 'BusinessHours'", "tp": "positive"}],

    # Group 5 policies: Negative for non-engineering roles
    [{"exp": "s.role != 'Engineer' and s.ap not in meta.aip", "tp": "negative"}],
]

split_count = 5
security_urps = split_and_bind_policies_to_urp(flat_mapped_results, "body", security_metadata_variations, policy_variations, split_count)
print(security_urps)