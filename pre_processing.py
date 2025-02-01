import json
with open('C:/Users/filip/Downloads/helpful_info.json', 'r') as file:
    files = json.load(file)


def clean_and_format_data(data,selected_fields):
    formatted_data = {}

    for category, records in data.items():
        cleaned_records = []

        for record in records:
            cleaned_record = {
                k.lstrip("#").split("\\n")[0].split("\n")[0].strip(): v.lstrip("#").split("\\n")[0].strip()
                # Remove `#`, `\n`, and extra spaces
                for k, v in record.items()
                if v.strip().lower() not in ["nan", ""]  # Remove empty or 'nan' values
            }
            print(cleaned_record)
            # Keep only selected fields
            filtered_record = {
                key: value for key, value in cleaned_record.items() if key in selected_fields
            }

            if filtered_record:  # Only add records with selected fields
                cleaned_records.append(filtered_record)

        if cleaned_records:  # Only add categories with valid records
            formatted_data[category] = cleaned_records

    return formatted_data

cleaned_data = clean_and_format_data({"Offers": files["Offers"],"Sub-Categories": files["Sub-Categories"]},
                                     ["Unnamed: 0", 'Unique URL (only "a-z 0-9" or "-")',
                                      'Phone Number','Sub-Category Description','Opening Hours Weekdays',
                                      'Opening Hours Weekends','What do you need to know?','Added on (date)'])

print(cleaned_data)

with open('data_cleaned.json', 'w') as f:
    json.dump(cleaned_data, f)