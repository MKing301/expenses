import csv
from expense_tracking.models import Expense


def run():
    # CSV file containing data to load into database
    file = open('/path/to/csv/file')
    read_file = csv.reader(file)

    # Start count at 1 for header row
    count = 1

    # Iterate over each row in the csv data
    for record in read_file:
        # Check if header row
        if count == 1:
            # Skip header row
            pass
        else:
            # Insert record into database
            Expense.objects.create(
                expense_date=record[0],
                expense_type_id=record[1],
                name=record[2],
                org=record[3],
                amount=record[4],
                notes=record[5]
            )
        # Increment row by 1
        count += 1
