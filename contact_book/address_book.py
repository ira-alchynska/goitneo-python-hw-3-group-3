from collections import defaultdict
from datetime import datetime, timedelta
import re

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Invalid phone number format")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', value):
            raise ValueError("Invalid birthday format. Use DD.MM.YYYY")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_info = '; '.join(str(phone) for phone in self.phones)
        birthday_info = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_info}{birthday_info}"

class AddressBook:
    def __init__(self):
        self.data = defaultdict(Record)

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        deleted = self.data.pop(name, None)
        if deleted:
            print(f"Record for {name} deleted.")
        else:
            print(f"No record found for {name}.")

    def get_birthdays_per_week(self):
        birthdays_per_week = defaultdict(list)
        today = datetime.today().date()
        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value
                birthday_date = datetime.strptime(birthday, '%d.%m.%Y').date()
                delta_days = (birthday_date - today).days
                if 0 <= delta_days < 7:
                    if delta_days == 0 and today.strftime('%A') == 'Saturday':
                        birthday_weekday = 'Monday'
                    else:
                        birthday_weekday = birthday_date.strftime('%A')
                    birthdays_per_week[birthday_weekday].append(record.name.value)
                elif delta_days >= 7 and delta_days < 14:
                    birthdays_per_week[(today + timedelta(days=delta_days)).strftime('%A')].append(record.name.value)
        if birthdays_per_week:
            for day, names in birthdays_per_week.items():
                print(f"{day}: {', '.join(names)}")
        else:
            print("No upcoming birthdays in the next week.")


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter user name."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Invalid command."

    return inner

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."

@input_error
def add_contact(args, book):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."

@input_error
def change_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.edit_phone(record.phones[0].value, phone)
        return "Contact updated."
    else:
        return "Contact not found."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return record.phones[0].value if record.phones else "No phone number found for this contact."
    else:
        return "Contact not found."

def show_all(book):
    if book.data:
        for record in book.data.values():
            print(record)
    else:
        print("No contacts saved.")

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return str(record.birthday)
    elif record:
        return "Birthday not found for this contact."
    else:
        return "Contact not found."

@input_error
def birthdays(book):
    book.get_birthdays_per_week()

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").lower()
        command, *args = user_input.split()

        if command == "close" or command == "exit":
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add" and len(args) == 2:
            print(add_contact(args, book))
        elif command == "change" and len(args) == 2:
            print(change_contact(args, book))
        elif command == "phone" and len(args) == 1:
            print(show_phone(args, book))
        elif command == "all" and not args:
            show_all(book)
        elif command == "add-birthday" and len(args) == 2:
            print(add_birthday(args, book))
        elif command == "show-birthday" and len(args) == 1:
            print(show_birthday(args, book))
        elif command == "birthdays" and not args:
            birthdays(book)
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
