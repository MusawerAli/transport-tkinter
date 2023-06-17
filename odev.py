import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import filedialog
import csv
import mysql.connector


# Create a MySQL connection
cnx = mysql.connector.connect(
    host='localhost',
    user='phpmyadmin',
    password='Root!123',
    database='test2'
)

class BankAccount:
    def __init__(self,id,name,account_number,pin,total_vehicles,is_admin=False,):
        self.id = id
        self.name = name
        self.account_number = account_number
        self.pin = pin
        self.total_vehicles = total_vehicles
        self.is_admin = is_admin
        self.transaction_history = []

    def check_total_vehicles(self):
        return self.total_vehicles

    def exist_vehicle(self, plate_number, hours,fare,id):
        cursor = cnx.cursor()
        select_query = "SELECT * FROM vehicles WHERE plate_no = %s AND is_exists=%s"
        cursor.execute(select_query, (plate_number,True,))
        record = cursor.fetchone()
        
        if record is not None:
            update_query = "UPDATE vehicles SET hours = %s,fare = %s,is_exists=%s WHERE plate_no = %s"
            update_values = (hours,fare,False,plate_number)
            cursor.execute(update_query, update_values)
            cnx.commit()
            cursor.close()
            return True
        return False
    
    def deposit(self, model,plate_number,id):
        self.total_vehicles += 1
        cursor = cnx.cursor()
        query = "INSERT INTO vehicles (model,plate_no,user_id) VALUES (%s, %s, %s)"
        data = (model, plate_number, id)
        cursor.execute(query, data)
        # select_query = "SELECT * FROM users WHERE id = %s"
        # cursor.execute(select_query, (id,))
        # record = cursor.fetchone()
        # if record is not None:
        #     total_vehicles = record[5]
        #     total_vehicles = total_vehicles + amount
        #     update_query = "UPDATE users SET total_vehicles = %s WHERE id = %s"
        #     update_values = (total_vehicles, id)
        #     cursor.execute(update_query, update_values)
        cnx.commit()
        cursor.close()
        # self.transaction_history.append(f"Deposit: ${amount}")
        return True

    def get_transaction_history(self):
        cursor = cnx.cursor()
        select_query = "SELECT * FROM vehicles WHERE user_id = %s"
        cursor.execute(select_query, (self.id,))
        record = cursor.fetchall()
        if record is not None:
            result_list = []
            column_names = cursor.column_names
            for row in record:
                result_dict = {}
                for i, column_value in enumerate(row):
                    result_dict[column_names[i]] = column_value
                result_list.append(result_dict)
            return result_list
        return None
    
    @staticmethod
    def get_users(id_number, pin):
        cursor = cnx.cursor()
        query = "SELECT * FROM users WHERE id_number = %s AND pin = %s"
        cursor.execute(query, (id_number, pin))
        result = cursor.fetchone()
        cursor.close()

        if result:
            id=result[0]
            name=result[1]
            account_number=result[2] 
            pin=result[3]
            is_admin=result[4]
            total_vehicles=result[5]
            return BankAccount(id,name,account_number, pin,total_vehicles,is_admin)
        else:
            return None
        
        
        

class ATMGUI:
    def __init__(self):
        # self.accounts = []
        # self.accounts.append(BankAccount("admin", "admin123", 0, is_admin=True))  # Admin hesabı
        # self.accounts.append(BankAccount("123456789", "1234", 5000))  # Standart hesap
        self.current_user = None

        self.root = tk.Tk()
        self.root.title("Transport")

        self.intro_label = tk.Label(self.root, text="Welcome to the Transport")
        self.intro_label.pack(pady=20)

        self.account_frame = tk.Frame(self.root)

        self.account_number_label = tk.Label(self.account_frame, text="Id Number:")
        self.account_number_label.grid(row=0, column=0)
        self.account_number_entry = tk.Entry(self.account_frame)
        self.account_number_entry.grid(row=0, column=1)

        self.name_label = tk.Label(self.account_frame, text="Name:")
        self.name_label.grid(row=1, column=0)
        self.name_entry = tk.Entry(self.account_frame, show="*")
        self.name_entry.grid(row=1, column=1)

        self.pin_label = tk.Label(self.account_frame, text="PIN:")
        self.pin_label.grid(row=1, column=0)
        self.pin_entry = tk.Entry(self.account_frame, show="*")
        self.pin_entry.grid(row=1, column=1)

        self.login_button = tk.Button(self.account_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.balance_label = tk.Label(self.root, text="")
        self.withdraw_button = tk.Button(self.root, text="Exit Vehciles", command=self.open_withdraw_popup)
        self.deposit_button = tk.Button(self.root, text="Entry Vehicles", command=self.open_add_vehicles_popup)
        self.logout_button = tk.Button(self.root, text="Logout", command=self.logout)

        self.account_frame.pack()

        self.root.mainloop()

    def login(self):
        id_number = self.account_number_entry.get()
        pin = self.pin_entry.get()
        account = BankAccount.get_users(id_number, pin)
        if account:
            self.current_user = account
            self.show_main_menu()
        else:
            messagebox.showerror("Error", "Invalid id number or PIN!")
        # for account in self.accounts:
        #     if account.account_number == account_number and account.pin == pin:
        #         self.current_user = account
        #         self.show_main_menu()
        #         return
        # messagebox.showerror("Error", "Invalid account number or PIN!")

    def show_main_menu(self):
        self.intro_label.pack_forget()
        self.account_frame.pack_forget()

        # self.balance_label.config(text="Balance: $%.2f" % self.current_user.check_total_vehicles())
        self.balance_label.pack(pady=10)
        self.withdraw_button.pack(pady=5)
        self.deposit_button.pack(pady=5)
        self.logout_button.pack(pady=10)

        if self.current_user.is_admin:
            self.add_user_button = tk.Button(self.root, text="Add User", command=self.open_add_user_popup)
            self.add_user_button.pack(pady=5)

            self.transaction_history_button = tk.Button(self.root, text="Transaction History",
                                                        command=self.open_transaction_history_popup)
            self.transaction_history_button.pack(pady=5)

    def open_withdraw_popup(self):
        withdraw_window = tk.Toplevel(self.root)
        withdraw_window.title("Vehicle Exist")


        plate_number_label = tk.Label(withdraw_window, text="Plate Number:", font=("Helvetica", 12))
        plate_number_label.pack()
        plate_number_entry = tk.Entry(withdraw_window, font=("Helvetica", 12))
        plate_number_entry.pack()
        
        hours_label = tk.Label(withdraw_window, text="Hours:", font=("Helvetica", 12))
        hours_label.pack()
        hours_entry = tk.Entry(withdraw_window, font=("Helvetica", 12))
        hours_entry.pack()
        
        fare_label = tk.Label(withdraw_window, text="Fare:", font=("Helvetica", 12))
        fare_label.pack()
        fare_entry = tk.Entry(withdraw_window, font=("Helvetica", 12))
        fare_entry.pack()

        withdraw_button = tk.Button(withdraw_window, text="Exit",
                                    command=lambda: self.exist_vehicle(plate_number_entry.get(),hours_entry.get(),fare_entry.get(),withdraw_window))
        withdraw_button.pack(pady=5)

    def exist_vehicle(self, plate_number, hours,fare,withdraw_window):
        plate_number = str(plate_number)
        hours = float(hours)
        fare = float(fare)
        
        if self.current_user.exist_vehicle(plate_number, hours,fare,self.current_user.id):
            messagebox.showinfo("Success", "Exist successful!")
            self.balance_label.config(text="Balance: $%.2f" % self.current_user.check_total_vehicles())
        else:
            messagebox.showerror("Error", "Wrong Plate No!")
        withdraw_window.destroy()

    def open_add_vehicles_popup(self):
        deposit_window = tk.Toplevel(self.root)
        deposit_window.title("Deposit")

        deposit_label = tk.Label(deposit_window, text="Enter vehicles details:", font=("Helvetica", 12))
        deposit_label.pack(pady=10)

        model_label = tk.Label(deposit_window, text="Model:", font=("Helvetica", 12))
        model_label.pack()
        model_entry = tk.Entry(deposit_window, font=("Helvetica", 12))
        model_entry.pack()

        plate_number_label = tk.Label(deposit_window, text="Plate Number:", font=("Helvetica", 12))
        plate_number_label.pack()
        plate_number_entry = tk.Entry(deposit_window, font=("Helvetica", 12))
        plate_number_entry.pack()


        deposit_button = tk.Button(deposit_window, text="Deposit",
                                   command=lambda: self.entryVehicle(model_entry.get(),plate_number_entry.get(),deposit_window))
        deposit_button.pack(pady=5)

    def entryVehicle(self, model,plate_number,deposit_window):
        model = str(model)
        self.current_user.deposit(model,plate_number,self.current_user.id)
        messagebox.showinfo("Success", "Vehicle Added successful!")
        self.balance_label.config(text="Total:"% self.current_user.check_total_vehicles())
        deposit_window.destroy()

    def logout(self):
        self.current_user = None

        self.balance_label.pack_forget()
        self.withdraw_button.pack_forget()
        self.deposit_button.pack_forget()
        self.logout_button.pack_forget()

        if hasattr(self, 'add_user_button'):
            self.add_user_button.pack_forget()

        if hasattr(self, 'transaction_history_button'):
            self.transaction_history_button.pack_forget()

        self.intro_label.pack()
        self.account_frame.pack()

    def open_add_user_popup(self):
        add_user_window = tk.Toplevel(self.root)
        add_user_window.title("Add User")

        account_number_entry = tk.Entry(add_user_window)
        account_number_entry.pack()

        name_label = tk.Label(add_user_window, text="Name:")
        name_label.pack()

        name_entry = tk.Entry(add_user_window)
        name_entry.pack()
        
        id_number_label = tk.Label(add_user_window, text="Id Number:")
        id_number_label.pack()

        id_number_entry = tk.Entry(add_user_window)
        id_number_entry.pack()

        pin_label = tk.Label(add_user_window, text="PIN:")
        pin_label.pack()

        pin_entry = tk.Entry(add_user_window, show="*")
        pin_entry.pack()

        add_user_button = tk.Button(add_user_window, text="Add User",
                                    command=lambda: self.add_user(name_entry.get(), pin_entry.get(),
                                                                  id_number_entry.get(),add_user_window))
        add_user_button.pack(pady=10)

    def add_user(self,name, pin,id_number_entry, add_user_window):
        is_admin = False
        name = name
        id_number_entry=id_number_entry
        cursor = cnx.cursor()
        query = "INSERT INTO users (name,id_number, pin,is_admin,total_vehicles) VALUES (%s, %s, %s, %s, %s)"
        data = (name, id_number_entry,pin,is_admin,0)
        cursor.execute(query, data)
        cnx.commit()
        cursor.close()
        # self.accounts.append(BankAccount(name,account_number, pin, balance, is_admin))
        messagebox.showinfo("Success", "User added successfully!")
        add_user_window.destroy()

    def open_transaction_history_popup(self):
        transaction_history_window = tk.Toplevel(self.root)
        transaction_history_window.title("Vehicles History")

        transaction_history_label = tk.Label(transaction_history_window, text="Vehicles History")
        transaction_history_label.pack(pady=10)

        treeview = ttk.Treeview(transaction_history_window)
        treeview["columns"] = ("id",'model','plate_no','hours','fare')

        treeview.column("id", width=50, minwidth=50, stretch=tk.NO)
        treeview.column("model", width=80, minwidth=80, stretch=tk.NO)
        treeview.column("plate_no", width=100, minwidth=100, stretch=tk.NO)   
        treeview.column("hours", width=80, minwidth=80, stretch=tk.NO)
        treeview.column("fare", width=100, minwidth=100, stretch=tk.NO)        

        treeview.heading("id", text="id.", anchor=tk.W)
        treeview.heading("model", text="model", anchor=tk.W)
        treeview.heading("plate_no", text="plate_no", anchor=tk.W)
        treeview.heading("hours", text="hours", anchor=tk.W)
        treeview.heading("fare", text="fare", anchor=tk.W)
        

        for index, transaction in enumerate(self.current_user.get_transaction_history()):
            treeview.insert(parent="", index=index, iid=index, values=(transaction['id'], transaction['model'],transaction['plate_no'],transaction['hours'],transaction['fare']))

        treeview.pack()

        export_button = tk.Button(transaction_history_window, text="Export as CSV",
                                  command=lambda: self.export_transaction_history_csv(transaction_history_window))
        export_button.pack(pady=10)

    def export_transaction_history_csv(self, transaction_history_window):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["No.", "Transaction"])
                for index, transaction in enumerate(self.current_user.get_transaction_history()):
                    writer.writerow([index + 1, transaction])
            messagebox.showinfo("Success", "Transaction history exported as CSV successfully!")
        transaction_history_window.destroy()


# Programı başlat
app = ATMGUI()
