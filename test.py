import tkinter as tk

# Import other necessary modules
from data import DatabaseHandler, FoodItem, Order

class RestaurantManagementSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Restaurant Management System")
        self.root.geometry("800x600")

        # Create components
        self.create_widgets()

        # Start the main event loop
        self.root.mainloop()

    def create_widgets(self):
        # Restaurant name label and entry field
        restaurant_label = tk.Label(self.root, text="Restaurant Name:")
        restaurant_label.pack(pady=20)
        self.restaurant_name_entry = tk.Entry(self.root)
        self.restaurant_name_entry.pack(pady=10)

        # Save button
        save_button = tk.Button(self.root, text="Save Restaurant", command=self.save_restaurant)
        save_button.pack(pady=10)

    def save_restaurant(self):
        restaurant_name = self.restaurant_name_entry.get()
        # Here you can add code to save the restaurant name to a database or file

# if __name__ == "__main__":
#     app = RestaurantManagementSystem()







# data.py

# main.py
from tkinter import tk
import data

def main():
    app = RestaurantManagementSystem()

if __name__ == "__main__":
    main()

### Step 4: Implement Data Access and Business Logic






# if __name__ == "__main__":
#     app = RestaurantManagementSystem()