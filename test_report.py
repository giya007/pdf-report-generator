import json

from report_queries import get_report_data


report = get_report_data()

print(json.dumps(report, indent=4))