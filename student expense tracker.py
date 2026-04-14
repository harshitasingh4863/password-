import os
import csv
from datetime import datetime

file_name = "expenses.csv"

def initialize_file():
    if not os.path.exists(file_name):
        with open(file_name, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Amount", "Description"])

def add_expense():
    date = input("Enter date (YYYY-MM-DD): ")
    category = input("Enter category: ")
    amount = input("Enter amount: ")
    description = input("Enter description: ")

    with open(file_name, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date, category, amount, description])

    print("Expense added successfully")

def view_expenses():
    with open(file_name, mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)

def total_expense():
    total = 0
    with open(file_name, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            total += float(row["Amount"])
    print("Total Expense:", total)

def category_wise():
    data = {}
    with open(file_name, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = row["Category"]
            amount = float(row["Amount"])
            if category in data:
                data[category] += amount
            else:
                data[category] = amount

    for key, value in data.items():
        print(key, ":", value)

def monthly_expense():
    data = {}
    with open(file_name, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            month = row["Date"][:7]
            amount = float(row["Amount"])
            if month in data:
                data[month] += amount
            else:
                data[month] = amount

    for key, value in data.items():
        print(key, ":", value)

def delete_expense():
    rows = []
    with open(file_name, mode="r") as file:
        reader = list(csv.reader(file))
        for i, row in enumerate(reader):
            print(i, row)

    index = int(input("Enter index to delete: "))

    with open(file_name, mode="r") as file:
        reader = list(csv.reader(file))
        rows = [row for i, row in enumerate(reader) if i != index]

    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print("Deleted successfully")

def search_expense():
    keyword = input("Enter keyword: ").lower()
    with open(file_name, mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            if any(keyword in item.lower() for item in row):
                print(row)

def menu():
    print("\n1. Add Expense")
    print("2. View Expenses")
    print("3. Total Expense")
    print("4. Category Wise Expense")
    print("5. Monthly Expense")
    print("6. Delete Expense")
    print("7. Search Expense")
    print("8. Exit")

def main():
    initialize_file()
    while True:
        menu()
        choice = input("Enter choice: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            total_expense()
        elif choice == "4":
            category_wise()
        elif choice == "5":
            monthly_expense()
        elif choice == "6":
            delete_expense()
        elif choice == "7":
            search_expense()
        elif choice == "8":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()