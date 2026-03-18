# Utilities
from datetime import datetime
import hashlib
from counter_storage import CounterFile


COUNTER_DATE_FORMAT = "%d%m%Y"

counter = CounterFile()


# Generate snippet ID
def generate_snippet_id():

    current_date = datetime.now().strftime(COUNTER_DATE_FORMAT)
    counter_data = counter.read_all()

    if current_date == counter_data["last_date"]:
        next_id = counter_data["last_id"] + 1
        counter_data["last_id"] = next_id
    elif current_date > counter_data["last_date"]:
        counter_data["last_date"] = current_date
        next_id = 1
        counter_data["last_id"] = next_id

    counter.write_all(counter_data)
    return f"{current_date}_{next_id:05d}"


# generate sha256 hash
def generate_hash(password_str):

    password_hash = hashlib.sha256(password_str.encode()).hexdigest()
    return password_hash


if __name__ == "__main__":
    print(generate_snippet_id())
    # print(generate_hash("vks123"))
