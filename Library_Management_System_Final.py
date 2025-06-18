# library_management.py
import json
from typing import List, Dict
from datetime import datetime, timedelta

# Represents a single book
class Book:
    def __init__(self, title: str, author: str):
        self._title = title  # Book title
        self._author = author  # Author name
        self._is_borrowed = False  # Book status
        self._due_date = None  # Due date for return
        self._borrowed_date = None  # Date when borrowed

    @property
    def title(self): return self._title

    @property
    def author(self): return self._author

    @property
    def is_borrowed(self): return self._is_borrowed

    @property
    def due_date(self): return self._due_date

    @property
    def borrowed_date(self): return self._borrowed_date

    def borrow(self, days_to_return=14) -> bool:
        if not self._is_borrowed:
            self._is_borrowed = True
            self._borrowed_date = datetime.now()
            self._due_date = self._borrowed_date + timedelta(days=days_to_return)
            return True
        return False

    def return_book(self) -> tuple:
        if self._is_borrowed:
            return_date = datetime.now()
            fine = 0
            if return_date > self._due_date:
                days_late = (return_date - self._due_date).days
                fine = days_late * 5  # $5 per day fine
            
            self._is_borrowed = False
            self._due_date = None
            self._borrowed_date = None
            return True, fine
        return False, 0

    def __str__(self):
        status = "Borrowed" if self._is_borrowed else "Available"
        due_info = f", Due: {self._due_date.strftime('%Y-%m-%d')}" if self._due_date else ""
        return f"📖 {self._title} by {self._author} - {status}{due_info}"

    def to_dict(self):
        return {
            "title": self._title,
            "author": self._author,
            "is_borrowed": self._is_borrowed,
            "due_date": self._due_date.isoformat() if self._due_date else None,
            "borrowed_date": self._borrowed_date.isoformat() if self._borrowed_date else None
        }

    @staticmethod
    def from_dict(data):
        book = Book(data['title'], data['author'])
        book._is_borrowed = data.get('is_borrowed', False)
        if data.get('due_date'):
            book._due_date = datetime.fromisoformat(data['due_date'])
        if data.get('borrowed_date'):
            book._borrowed_date = datetime.fromisoformat(data['borrowed_date'])
        return book

# Represents a user
class User:
    def __init__(self, name: str, user_id: str):
        self._name = name
        self._user_id = user_id
        self._borrowed_books: List[str] = []  # List of borrowed book titles
        self._total_fine = 0

    @property
    def name(self): return self._name

    @property
    def user_id(self): return self._user_id

    @property
    def borrowed_books(self): return self._borrowed_books[:]

    @property
    def total_fine(self): return self._total_fine

    def add_borrowed_book(self, title: str):
        if title not in self._borrowed_books:
            self._borrowed_books.append(title)

    def remove_borrowed_book(self, title: str):
        if title in self._borrowed_books:
            self._borrowed_books.remove(title)

    def add_fine(self, amount: float):
        self._total_fine += amount

    def pay_fine(self, amount: float) -> bool:
        if amount <= self._total_fine:
            self._total_fine -= amount
            return True
        return False

    def __str__(self):
        fine_info = f", Fine: ${self._total_fine}" if self._total_fine > 0 else ""
        return f"👤 {self._name} (ID: {self._user_id}), Books: {len(self._borrowed_books)}{fine_info}"

    def to_dict(self):
        return {
            "name": self._name,
            "user_id": self._user_id,
            "borrowed_books": self._borrowed_books,
            "total_fine": self._total_fine
        }

    @staticmethod
    def from_dict(data):
        user = User(data['name'], data['user_id'])
        user._borrowed_books = data.get('borrowed_books', [])
        user._total_fine = data.get('total_fine', 0)
        return user

# Manages the library
class Library:
    def __init__(self, book_file='books.json', user_file='users.json'):
        self._books: Dict[str, Book] = {}  # Book store by title
        self._users: Dict[str, User] = {}  # User store
        self._data_file_books = book_file
        self._data_file_users = user_file
        self._load_data()

    def _load_data(self):
        try:
            with open(self._data_file_books, 'r') as bf:
                books = json.load(bf)
                for data in books:
                    book = Book.from_dict(data)
                    self._books[book.title] = book
        except FileNotFoundError:
            pass

        try:
            with open(self._data_file_users, 'r') as uf:
                users = json.load(uf)
                for data in users:
                    user = User.from_dict(data)
                    self._users[user.user_id] = user
        except FileNotFoundError:
            pass

    def _save_data(self):
        with open(self._data_file_books, 'w') as bf:
            json.dump([book.to_dict() for book in self._books.values()], bf, indent=2)
        with open(self._data_file_users, 'w') as uf:
            json.dump([user.to_dict() for user in self._users.values()], uf, indent=2)

    def add_book(self, book: Book) -> bool:
        if book.title not in self._books:
            self._books[book.title] = book
            self._save_data()
            return True
        return False

    def remove_book(self, title: str) -> bool:
        if title in self._books and not self._books[title].is_borrowed:
            del self._books[title]
            self._save_data()
            return True
        return False

    def register_user(self, user: User) -> bool:
        if user.user_id not in self._users:
            self._users[user.user_id] = user
            self._save_data()
            return True
        return False

    def remove_user(self, user_id: str) -> bool:
        user = self._users.get(user_id)
        if user and not user.borrowed_books and user.total_fine == 0:
            del self._users[user_id]
            self._save_data()
            return True
        return False

    def borrow_book(self, title: str, user_id: str, days_to_return=14) -> bool:
        book = self._books.get(title)
        user = self._users.get(user_id)
        if book and user and not book.is_borrowed:
            if book.borrow(days_to_return):
                user.add_borrowed_book(title)
                self._save_data()
                return True
        return False

    def return_book(self, title: str, user_id: str) -> tuple:
        book = self._books.get(title)
        user = self._users.get(user_id)
        if book and user and title in user.borrowed_books:
            success, fine = book.return_book()
            if success:
                user.remove_borrowed_book(title)
                if fine > 0:
                    user.add_fine(fine)
                self._save_data()
                return True, fine
        return False, 0

    def pay_fine(self, user_id: str, amount: float) -> bool:
        user = self._users.get(user_id)
        if user and user.pay_fine(amount):
            self._save_data()
            return True
        return False

    def search_book(self, query: str) -> List[Book]:
        query = query.lower()
        return [book for book in self._books.values()
                if query in book.title.lower() or query in book.author.lower()]

    def display_all_books(self):
        for book in self._books.values():
            print(book)

    def display_all_users(self):
        for user in self._users.values():
            print(user)

    def display_user_borrowed_books(self, user_id: str):
        user = self._users.get(user_id)
        if user:
            if user.borrowed_books:
                for title in user.borrowed_books:
                    print(self._books.get(title))
            else:
                print("📚 No books borrowed!")
        else:
            print("❌ User not found.")

def main():
    lib = Library()
    print("🌟 Welcome to Our Friendly Library! 🌟")
    
    while True:
        print("\n📚 NIET Library Management System:")
        print("1. Add Book 📖")
        print("2. Remove Book 🗑️")
        print("3. Register User 👤")
        print("4. Remove User ❌")
        print("5. Borrow Book 📚")
        print("6. Return Book 📤")
        print("7. Search Book 🔍")
        print("8. Show All Books 📋")
        print("9. Show All Users 👥")
        print("10. Show My Books 📖")
        print("11. Pay Fine 💰")
        print("12. Exit 👋")
        
        choice = input("Enter your choice: ")

        try:
            if choice == '1':
                title = input("📖 Book title: ")
                author = input("✍️ Author name: ")
                if lib.add_book(Book(title, author)):
                    print("🎉 Yay! Book added successfully! 📚✨")
                else:
                    print("😅 Oops! This book already exists!")

            elif choice == '2':
                title = input("📖 Book title to remove: ")
                if lib.remove_book(title):
                    print("🗑️ Book removed successfully! All clean! ✨")
                else:
                    print("😕 Couldn't remove the book. Maybe it's borrowed?")

            elif choice == '3':
                name = input("👤 Your name: ")
                user_id = input("🆔 User ID: ")
                if lib.register_user(User(name, user_id)):
                    print("🎊 Welcome to our library family! 👨‍👩‍👧‍👦")
                else:
                    print("😅 This User ID already exists!")

            elif choice == '4':
                user_id = input("🆔 User ID to remove: ")
                if lib.remove_user(user_id):
                    print("👋 User removed successfully! We'll miss you!")
                else:
                    print("😕 Couldn't remove user. Check if they have books or fines!")

            elif choice == '5':
                title = input("📖 Book title to borrow: ")
                user_id = input("🆔 Your User ID: ")
                
                # Check if user is registered
                if user_id not in lib._users:
                    print("❌ User not registered! Please register first.")
                elif lib.borrow_book(title, user_id):
                    book = lib._books.get(title)
                    if book:
                        due_date = book.due_date.strftime('%Y-%m-%d')
                        print("🎉 Book borrowed successfully! Happy reading! 📚")
                        print(f"📅 Please return by {due_date}")
                else:
                    print("😕 Couldn't borrow the book. Is it available?")

            elif choice == '6':
                title = input("📖 Book title to return: ")
                user_id = input("🆔 Your User ID: ")
                success, fine = lib.return_book(title, user_id)
                if success:
                    if fine > 0:
                        print("📚 Book returned! But there's a small fine 💰")
                        print(f"💸 Fine amount: ${fine}")
                    else:
                        print("🎉 Book returned successfully! Thank you! 😊")
                else:
                    print("😕 Couldn't return the book. Check the details!")

            elif choice == '7':
                query = input("🔍 Search for: ")
                results = lib.search_book(query)
                if results:
                    print("🔍 Found these books:")
                    for book in results:
                        print(book)
                    print("✨ Search completed successfully!")
                else:
                    print("😔 No books found. Try another search!")

            elif choice == '8':
                print("📋 All our wonderful books:")
                lib.display_all_books()
                print("✨ That's our complete collection!")

            elif choice == '9':
                print("👥 Our amazing library members:")
                lib.display_all_users()
                print("✨ These are all our users!")

            elif choice == '10':
                user_id = input("🆔 Your User ID: ")
                print("📖 Your borrowed books:")
                lib.display_user_borrowed_books(user_id)
                print("✨ List displayed successfully!")

            elif choice == '11':
                user_id = input("🆔 Your User ID: ")
                amount = float(input("💰 Amount to pay: $"))
                if lib.pay_fine(user_id, amount):
                    print("💳 Payment successful! Thank you! 😊✨")
                else:
                    print("😕 Payment failed. Check your details!")

            elif choice == '12':
                print("👋 Thank you for visiting our library! Come back soon! 🌟")
                break
            else:
                print("😅 Invalid choice! Please try again!")
                
        except Exception as e:
            print(f"😔 Oops! Something went wrong: {e}")

if __name__ == "__main__":
    main()
