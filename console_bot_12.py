import datetime
import pickle
from pathlib import Path
from collections import UserDict
from datetime import date



class Field:
    def __init__(self, value) -> None:
        self.value = value
    def __str__(self) -> str:
        return f'{self.value}'
    def __eq__(self, other) -> bool:
        return self.value == other.value #otherwise python uses is and returns False when comparing two objects, here we specify that we want to compare value

class Name(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        self.__value = value


class Phone(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        result = None
        phone = value.replace("+", "").replace("(", "").replace(")", "").replace("-", "")
        if phone.isdigit():
            result = phone
        if result is None:
            raise ValueError
        self.__value = result
            
 
class WrongDate(Exception):
    pass

class Birthday(Field):
    
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if value is None:
            self.__value = None
        else:
            try:
                self.__value = datetime.datetime.strptime(value, "%d.%m.%Y").date()
            except ValueError:
                raise WrongDate


    def days_to_next(self):
        days = 0
        while True:
            then = datetime.datetime.now() + datetime.timedelta(days=days)
            if then.day == self.value.day and then.month == self.value.month:
                return f'You have {days} days to buy a gift'
            days += 1

class Record:
    def __init__(self, name: Name, phones=[]) -> None:
        self.name = name
        self.phones = phones
        self.birthday = None
    
    def __str__(self) -> str:
        return f'User: {self.name} Phone(s): {", ".join([phone.value for phone in self.phones])}'

    def add_phone(self, phone: Phone) -> None:
        self.phones.append(phone)

    def delete_phone(self, phone: Phone) -> None:
        self.phones.remove(phone)

    def edit_phone(self, phone: Phone, new_phone: Phone) -> None:
        self.phones.remove(phone)
        self.phones.append(new_phone)

    def set_birthday(self, bday: Birthday):
        self.birthday = bday

    def get_days(self):
        return self.birthday.days_to_next()

    

class AddressBook(UserDict):

    def __init__(self, filename: str) -> None:
        super().__init__()  
        self.filename = Path(filename)
        if self.filename.exists():
            with open(self.filename, 'rb') as db:
                self.data = pickle.load(db)

    def save(self):
        with open(self.filename, 'wb') as db:
            pickle.dump(self.data, db)


    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def iterator(self, max_value = 2):
        page = 1
        index = 0
        result = '\n'
        for i in self.data:
            result += f'{self.data[i]}\n'
            index += 1
            if index >= max_value:
                yield result
                result = '***' * 5 + 'page ' + str(page) + '***' * 5 + '\n'
                index = 0
                page += 1
        yield result

class PhoneExists(Exception):
    pass

class BirthdayNotExists(Exception):
    pass


class InputError:
    def __init__(self, func) -> None:
        self.func = func
    def __call__(self, contacts, *args):
        try:
            return self.func(contacts, *args)
        except ValueError:
            return "Please make sure to add data in the correct format"
        except KeyError:
            return "There is no such user"
        except IndexError:
            return "Your entry should include a name and a phone"
        except PhoneExists:
            return "This phone already exists in the address book"
        except BirthdayNotExists:
            return "Use bds command to add a birthday to the user first"
        except WrongDate:
            return "You have entered an invalid date. Make sure you write it in the following format: dd.mm.yyyy"

def hello_func(*args):
    return "Hello! How can I help you?"

@InputError
def add(contacts, *args): # when you add name and phone it adds the contact to the address book
    name = Name(args[0])
    phone = Phone(args[1])
    if name.value in contacts:
        if phone in contacts[name.value].phones:
            raise PhoneExists
        else:
            contacts[name.value].add_phone(phone)
    else:
        contacts[name.value] = Record(name, [phone])
        return f'Added {phone} to user {name}'

@InputError
def change_phone(contacts, *args): #when you enter user's name and phone it chnages it to the new one
    name = args[0]
    phone = args [1]
    new_phone = args[2]
    contacts[name].edit_phone(Phone(phone), Phone(new_phone))
    print(contacts[name])
    return f'Phone {phone} changed to {new_phone} for {name}'

@InputError
def phone(contacts, *args): # when you enter user's name it returns users phones
    name = args[0]
    phone = contacts[name]
    return f'{phone}'

#@InputError
#def show_all(contacts, *args): #shows all contacts in address book
    #result = ""
    #for _ in contacts:
        #result = result + f' {contacts[_]}'
    #return result


@InputError
def show_all(contacts, *args):
    if len(contacts) == 0:
        raise IndexError
    else:
        users = ''
        for key in contacts.iterator():
            users += f'{key}\n'
        return users 

@InputError
def set_birthday(contacts, *args):
    name = Name(args[0])
    bday = Birthday(args[1])
    if name.value in contacts:
        contacts[name.value].set_birthday(bday)
        return 'Birthday is set'
    else:
        raise KeyError

@InputError
def get_days(contacts, *args):
    name = Name(args[0])
    if name.value in contacts:
        return contacts[name.value].get_days()
    else:
        raise KeyError

def exit(contacts, *args):
    contacts.save()
    return "Good bye!"


def search(contacts, *args):
    substring = args[0]
    if contacts:
    # [phone.value for phone in self.phones]
        for name, data in contacts.items():
            if substring.lower() in name.lower():
                return f'{data}'
            for phone in data.phones:
                if substring in str(phone):
                    return f"The phone is {phone} and belongs to {name}"
    else:
        return "Address Book is empty"



 
def help(*args):
    return """Commands format - Command meaning
    "help" - returns a list of available commands with formatting
    "hello" - returns a greeting
    "exit" or "." or "bye" - exits the program
    "add" or "добавь" or "додай name phone" - adds a phone to a contact
    "change name phone new phone" - changes a phone number to a new one
    "phone name" = finds a phone for name
    "show all" - displays all contacts
    "bds name birthday" - adds a birthday for contact
    "bdg name" - let's you know how many days until the next birthday of the user
    "find" + any strings - finds matches in the adress book and returns the findings
    """

COMMANDS = {
    hello_func: ["hello"], # hello
    exit: ["exit", ".", "bye"], # exit
    add: ["add", "добавь", "додай"], # add name phone
    change_phone: ["change"], # change name phone new phone
    phone: ["phone"], # phone name
    show_all: ["show all", "show"], # show
    set_birthday: ["bds"], # bds name birthday
    get_days: ["bdg"], # bdg name
    help: ["help"],
    search: ["find"]
    
}


def parse_command(user_input: str):
    for k,v in COMMANDS.items():
        for i in v:
            if user_input.lower().startswith(i.lower()):
                return k, user_input[len(i):].strip().split(" ")
            

def main():
    contacts = AddressBook(filename='ab.dat')
    while True:
        user_input = input(">>>")
        result, data = parse_command(user_input)
        print(result(contacts, *data), '\n')
        if result is exit:
            break

if __name__ == '__main__':
    main()

   












        
