# library_management.py
import json
from typing import List, Dict
from datetime import datetime, timedelta

# Represents a single book
class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self._title = title  # Book title
        self._author = author  # Author name
        self._isbn = isbn  # Unique ISBN
        self._is_borrowed = False  # Book status
        self._due_date = None  # Due date for return
        self._borrowed_date = None  # Date when borrowed

    @property
    def title(self): return self._title  # Get title

    @property
    def author(self): return self._author  # Get author

    @property
    def isbn(self): return self._isbn  # Get ISBN

    @property
    def is_borrowed(self): return self._is_borrowed  # Get status

    @property
    def due_date(self): return self._due_date

    @property
    def borrowed_date(self): return self._borrowed_date

    @is_borrowed.setter
    def is_borrowed(self, value: bool):
        if isinstance(value, bool):
            self._is_borrowed = value  # Set status

    def borrow(self, days_to_return=14) -> bool:
        if not self._is_borrowed:
            self._is_borrowed = True  # Borrow book
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
            
            self._is_borrowed = False  # Return book
            self._due_date = None
            self._borrowed_date = None
            return True, fine
        return False, 0

    def __str__(self):
        status = "Borrowed" if self._is_borrowed else "Available"
        due_info = f", Due: {self._due_date.strftime('%Y-%m-%d')}" if self._due_date else ""
        return f"Title: {self._title}, Author: {self._author}, ISBN: {self._isbn}, Status: {status}{due_info}"

    def to_dict(self):
        return {
            "title": self._title,
            "author": self._author,
            "isbn": self._isbn,
            "is_borrowed": self._is_borrowed,
            "due_date": self._due_date.isoformat() if self._due_date else None,
            "borrowed_date": self._borrowed_date.isoformat() if self._borrowed_date else None
        }

    @staticmethod
    def from_dict(data):
        book = Book(data['title'], data['author'], data['isbn'])
        book._is_borrowed = data.get('is_borrowed', False)
        if data.get('due_date'):
            book._due_date = datetime.fromisoformat(data['due_date'])
        if data.get('borrowed_date'):
            book._borrowed_date = datetime.fromisoformat(data['borrowed_date'])
        return book

# Represents a user
class User:
    def __init__(self, name: str, user_id: str):
        self._name = name  # User name
        self._user_id = user_id  # User ID
        self._borrowed_books_isbns: List[str] = []  # Borrowed book list
        self._total_fine = 0  # Total fine amount

    @property
    def name(self): return self._name

    @property
    def user_id(self): return self._user_id

    @property
    def borrowed_books_isbns(self): return self._borrowed_books_isbns[:]

    @property
    def total_fine(self): return self._total_fine

    def add_borrowed_book_isbn(self, isbn: str):
        if isbn not in self._borrowed_books_isbns:
            self._borrowed_books_isbns.append(isbn)  # Add borrowed book

    def remove_borrowed_book_isbn(self, isbn: str):
        if isbn in self._borrowed_books_isbns:
            self._borrowed_books_isbns.remove(isbn)  # Remove book from list

    def add_fine(self, amount: float):
        self._total_fine += amount

    def pay_fine(self, amount: float) -> bool:
        if amount <= self._total_fine:
            self._total_fine -= amount
            return True
        return False

    def __str__(self):
        fine_info = f", Fine: ${self._total_fine}" if self._total_fine > 0 else ""
        return f"User: {self._name} (ID: {self._user_id}), Borrowed Books: {len(self._borrowed_books_isbns)}{fine_info}"

    def to_dict(self):
        return {
            "name": self._name,
            "user_id": self._user_id,
            "borrowed_books_isbns": self._borrowed_books_isbns,
            "total_fine": self._total_fine
        }

    @staticmethod
    def from_dict(data):
        user = User(data['name'], data['user_id'])
        user._borrowed_books_isbns = data.get('borrowed_books_isbns', [])
        user._total_fine = data.get('total_fine', 0)
        return user

# Manages the overall library
class Library:
    def __init__(self, book_file='books.json', user_file='users.json'):
        self._books: Dict[str, Book] = {}  # Book store
        self._users: Dict[str, User] = {}  # User store
        self._data_file_books = book_file
        self._data_file_users = user_file
        self._load_data()  # Load data from JSON

    def _load_data(self):
        try:
            with open(self._data_file_books, 'r') as bf:
                books = json.load(bf)
                for data in books:
                    book = Book.from_dict(data)
                    self._books[book.isbn] = book
        except FileNotFoundError:
            pass  # No book file yet

        try:
            with open(self._data_file_users, 'r') as uf:
                users = json.load(uf)
                for data in users:
                    user = User.from_dict(data)
                    self._users[user.user_id] = user
        except FileNotFoundError:
            pass  # No user file yet

    def _save_data(self):
        # Save books and users to file
        with open(self._data_file_books, 'w') as bf:
            json.dump([book.to_dict() for book in self._books.values()], bf, indent=2)
        with open(self._data_file_users, 'w') as uf:
            json.dump([user.to_dict() for user in self._users.values()], uf, indent=2)

    def add_book(self, book: Book) -> bool:
        if book.isbn not in self._books:
            self._books[book.isbn] = book
            self._save_data()
            return True
        return False

    def remove_book(self, isbn: str) -> bool:
        if isbn in self._books and not self._books[isbn].is_borrowed:
            del self._books[isbn]  # Delete only if not borrowed
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
        if user and not user.borrowed_books_isbns and user.total_fine == 0:
            del self._users[user_id]  # Delete user with no borrowed books and no fine
            self._save_data()
            return True
        return False

    def borrow_book(self, isbn: str, user_id: str, days_to_return=14) -> bool:
        book = self._books.get(isbn)
        user = self._users.get(user_id)
        if book and user and not book.is_borrowed:
            if book.borrow(days_to_return):
                user.add_borrowed_book_isbn(isbn)  # Update both records
                self._save_data()
                # Show due date message
                due_date = book.due_date.strftime('%Y-%m-%d')
                print(f"\n⚠️  IMPORTANT NOTICE ⚠️")
                print(f"Book '{book.title}' must be returned by {due_date}")
                print(f"Late return will result in a fine of $5 per day!")
                print(f"Please return the book on time to avoid penalties.\n")
                return True
        return False

    def return_book(self, isbn: str, user_id: str) -> tuple:
        book = self._books.get(isbn)
        user = self._users.get(user_id)
        if book and user and isbn in user.borrowed_books_isbns:
            success, fine = book.return_book()
            if success:
                user.remove_borrowed_book_isbn(isbn)
                if fine > 0:
                    user.add_fine(fine)
                    print(f"\n📚 Book returned successfully!")
                    print(f"💰 Late return fine: ${fine}")
                    print(f"💳 Total outstanding fine: ${user.total_fine}")
                    print("Please pay your fine at the library counter.\n")
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
                if query in book.title.lower() or query in book.author.lower() or query in book.isbn]

    def display_all_books(self, show_available_only=False):
        for book in self._books.values():
            if not show_available_only or not book.is_borrowed:
                print(book)  # Print all or only available books

    def display_all_users(self):
        for user in self._users.values():
            print(user)  # Print all users

    def display_user_borrowed_books(self, user_id: str):
        user = self._users.get(user_id)
        if user:
            for isbn in user.borrowed_books_isbns:
                print(self._books.get(isbn))  # Show borrowed books
        else:
            print("User not found.")

    def display_overdue_books(self):
        print("\n📋 OVERDUE BOOKS:")
        current_date = datetime.now()
        for book in self._books.values():
            if book.is_borrowed and book.due_date and current_date > book.due_date:
                days_overdue = (current_date - book.due_date).days
                print(f"{book} - {days_overdue} days overdue")

# Console UI interaction

def main():
    lib = Library()
    while True:
        print("\nLibrary Menu:")
        print("1. Add Book\n2. Remove Book\n3. Register User\n4. Remove User")
        print("5. Borrow Book\n6. Return Book\n7. Search Book\n8. Show All Books")
        print("9. Show All Users\n10. Show User Borrowed Books\n11. Pay Fine")
        print("12. Show Overdue Books\n13. Exit")
        choice = input("Enter choice: ")

        try:
            if choice == '1':
                title = input("Title: ")
                author = input("Author: ")
                isbn = input("ISBN: ")
                success = lib.add_book(Book(title, author, isbn))
                print("Book added." if success else "ISBN already exists.")

            elif choice == '2':
                isbn = input("Enter ISBN to remove: ")
                print("Book removed." if lib.remove_book(isbn) else "Failed to remove book.")

            elif choice == '3':
                name = input("User Name: ")
                user_id = input("User ID: ")
                print("User registered." if lib.register_user(User(name, user_id)) else "User ID already exists.")

            elif choice == '4':
                user_id = input("User ID to remove: ")
                print("User removed." if lib.remove_user(user_id) else "Failed to remove user.")

            elif choice == '5':
                isbn = input("ISBN: ")
                user_id = input("User ID: ")
                days = input("Days to return (default 14): ")
                days = int(days) if days else 14
                print("Book borrowed." if lib.borrow_book(isbn, user_id, days) else "Borrow failed.")

            elif choice == '6':
                isbn = input("ISBN: ")
                user_id = input("User ID: ")
                success, fine = lib.return_book(isbn, user_id)
                if not success:
                    print("Return failed.")

            elif choice == '7':
                query = input("Search query: ")
                results = lib.search_book(query)
                print("Search Results:")
                for book in results:
                    print(book)

            elif choice == '8':
                lib.display_all_books()

            elif choice == '9':
                lib.display_all_users()

            elif choice == '10':
                user_id = input("User ID: ")
                lib.display_user_borrowed_books(user_id)

            elif choice == '11':
                user_id = input("User ID: ")
                amount = float(input("Amount to pay: $"))
                if lib.pay_fine(user_id, amount):
                    print("Fine payment successful.")
                else:
                    print("Payment failed. Check user ID and amount.")

            elif choice == '12':
                lib.display_overdue_books()

            elif choice == '13':
                print("Exiting...")
                break
            else:
                print("Invalid choice.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
