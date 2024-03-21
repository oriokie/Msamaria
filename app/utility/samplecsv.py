import csv

# Sample data
data = [
    {
        "member_name": "John Doe",
        "member_id_number": "123456",
        "member_phone_number": "123-456-7890",
        "Spouse": "Jane Doe",
        "Contributor's Father": "John Doe Sr.",
        "Contributor's Mother": "Jane Doe Sr.",
        "Spouse's Father": "Mary Smith Sr.",
        "Spouse's Mother": "Robert Smith Sr.",
        "First Child": "Jack Doe",
        "Second Child": "Jill Doe",
        "Third Child": "Jim Doe",
        "Fourth Child": "Jenny Doe",
        "Fifth Child": "Joe Doe"
    },
    {
        "member_name": "Alice Johnson",
        "member_id_number": "789012",
        "member_phone_number": "987-654-3210",
        "Spouse": "Bob Johnson",
        "Contributor's Father": "Alice Johnson Sr.",
        "Contributor's Mother": "Carol Johnson Sr.",
        "Spouse's Father": "Robert Thompson Sr.",
        "Spouse's Mother": "Martha Thompson Sr.",
        "First Child": "Bob Johnson",
        "Second Child": "Susan Johnson",
        "Third Child": "Sam Johnson",
        "Fourth Child": "Sarah Johnson",
        "Fifth Child": "Scott Johnson"
    }
]

# Specify the CSV file path
csv_file_path = "sample.csv"

# Write data to CSV file
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)

print("CSV file created successfully:", csv_file_path)
