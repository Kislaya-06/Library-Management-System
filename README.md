Library Management System - Class Assignment Report

Student Details

Name: Kislaya AgarwalCollege: NIET (Noida Institute of Engineering and Technology)Program: B.TechCourse: Python Programming / Object-Oriented Programming

Project Title

Console-Based Library Management System in Python

Objective

To develop a console-based Library Management System using Python that adheres to object-oriented programming (OOP) principles. The system allows users to manage books and library users, and to track book borrowing and returning activities with data persistence through JSON files.

Features Implemented

Add and remove books

Register and deregister users

Borrow and return books

Search for books by title, author, or ISBN

Display all books (optionally only available ones)

Display all registered users

Display books borrowed by a particular user

Save and load data persistently using JSON files

Robust error handling for invalid operations

Tools & Technologies

Language: Python 3.x

Data Storage: JSON file system

Libraries used: json, typing

OOP Concepts Used

Class Design: Book, User, and Library classes represent core components

Encapsulation: Attributes are prefixed with _ and accessed via properties

Constructors: __init__ method used for initializing object state

Instance Methods: For specific behaviors like borrow, return, etc.

Object Relationships: Library aggregates Book and User objects

Magic Methods: __str__ for clean string representation

Error Handling: try-except blocks used for runtime safety

Project Structure

LibraryManagementProject/
│
├── books.json               # Auto-generated, holds all book records
├── users.json               # Auto-generated, holds all user records
├── library_management.py    # Main application file
└── README.md                # Project instructions and usage

Sample JSON Files

books.json

[
  {
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "is_borrowed": false
  }
]

users.json

[
  {
    "name": "Kislaya",
    "user_id": "U101",
    "borrowed_books_isbns": []
  }
]

How to Run the Project

Make sure Python is installed (python --version).

Save the code in a file named library_management.py.

Open a terminal and navigate to the project directory.

Run the application:

python library_management.py

Interact using the numbered menu options.

Conclusion

This Library Management System project is a successful demonstration of how core OOP principles can be applied to create a functional, interactive, and persistent system in Python. The use of classes and file handling makes it scalable and maintainable.

Future Enhancements (Optional)

Introduce Student and Faculty subclasses with borrowing limits

Track due dates and calculate late fees

Generate summary reports (borrowed books, overdue returns)

Convert to GUI application using tkinter or a web app using Flask

Submitted by: Kislaya AgarwalDate: [Auto-generated or manually filled]


