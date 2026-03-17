# Utilities
from datetime import datetime
from storage import CounterFile


COUNTER_DATE_FORMAT = "%d%m%Y"

counter = CounterFile()


# Generate snippet ID
def generate_snippet_id():

    current_date = datetime.now().strftime(COUNTER_DATE_FORMAT)
    counter_data = counter.json_handler.read_all()

    if current_date == counter_data["last_date"]:
        next_id = counter_data["last_id"] + 1
        counter_data["last_id"] = next_id
    elif current_date > counter_data["last_date"]:
        counter_data["last_date"] = current_date
        next_id = 1
        counter_data["last_id"] = next_id

    counter.json_handler.write_all(counter_data)
    return f"{current_date}_{next_id:05d}"


# print(generate_snippet_id())
