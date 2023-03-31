import re
import random
import datetime
import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, font
from .database import get_conn

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Inventory and sales manager')
        self.geometry('1050x600+450+220')
        self.resizable(0, 0)
        self.list_headers = ['Product ID', 'Code', 'Name', 'Price', 'Stock']
        self.count = 0
        self.subtotal = 0
        self.back = 1.0
        self.inserts = 0
        self.ids = []
        self.name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.amount_var = tk.IntVar()
        self.search_var = tk.StringVar()
        self.products_frame()
        self.crud_buttons()
        self.recipe_frame()
        self.recipe_details_frame()
        self.display_products()
        self.name_var.trace('w', self.validate)
        self.last_name_var.trace('w', self.validate)
        self.amount_var.trace('w', self.validate)
        self.search_var.trace('w', self.highlight_searched)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def products_frame(self):
        global products_frame
        products_frame = tk.Frame(self, bd=2, relief=tk.FLAT, bg='azure4')
        products_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.50)
        products_frame.grid_rowconfigure(0, weight=1)
        products_frame.grid_columnconfigure(0, weight=1)

        products = tk.Label(products_frame, text='Products', font=('Arial', 15, 'bold'), bd=1, relief=tk.FLAT, fg='white', bg='azure4')
        products.grid(row=0, column=0)

        list_headers_frame = tk.Frame(products_frame, bd=2, relief=tk.FLAT, bg='white')
        list_headers_frame.grid(row=2, column=0, padx=48, sticky=tk.W)

        for i in self.list_headers:
            header = tk.Label(list_headers_frame, text=i, font=('Arial', 10, 'bold'), bd=1, relief=tk.FLAT, fg='black', bg='white')
            header.grid(row=0, column=self.count, padx=45)

            self.count += 1

        self.sale_button = tk.Button(products_frame, text='Add Product\nFor Sale', font=('Arial', 8, 'bold'), width=15, command=self.get_list_focus)
        self.sale_button.grid(row=3, column=1)


    def crud_buttons(self):
        global products_frame
        buttons_frame = tk.Frame(products_frame, bd=1, relief=tk.FLAT, bg='azure4')
        buttons_frame.grid(row=1, column=0, pady=15, sticky=tk.E)

        search_frame = tk.Frame(products_frame, bd=1, relief=tk.FLAT, bg='azure4')
        search_frame.grid(row=1, column=0, sticky=tk.W, padx=5)

        search_label = tk.Label(search_frame, text='Search by Code:',font=('Arial', 10), bd=1, bg='azure4')
        search_label.grid(row=1, column=0, sticky=tk.W)

        search_entry = tk.Entry(search_frame, width=12, font='Arial 10', textvariable=self.search_var)
        search_entry.grid(row=1, column=1, padx=5)

        add_button = tk.Button(buttons_frame, text='Add Product', font=('Arial', 10), command=self.add_product)
        add_button.grid(row=1, column=2, padx=20)

        update_button = tk.Button(buttons_frame, text='Update Product', font=('Arial', 10), command=self.update_product)
        update_button.grid(row=1, column=3, padx=20)

        delete_button = tk.Button(buttons_frame, text='Delete Product', font=('Arial', 10), command=self.delete_product)
        delete_button.grid(row=1, column=4, padx=20)

    def recipe_frame(self):
        recipe_frame = tk.LabelFrame(self, text='Recipe', font=('Arial', 10, 'bold'), relief=tk.FLAT, bg='azure4', fg='white')
        recipe_frame.place(relx=0.05, rely=0.57, relwidth=0.40, relheight=0.40)
        recipe_frame.grid_rowconfigure(0, weight=1)
        recipe_frame.grid_columnconfigure(0, weight=1)

        self.recipe_text = tk.Text(recipe_frame, font=('Arial', 10), width=100, height=20, state=tk.DISABLED)
        self.recipe_text.grid(row=0, column=0)

        recipe_buttons = tk.Frame(recipe_frame, relief=tk.FLAT, bg='azure4')
        recipe_buttons.grid(row=1, column=0)

        self.save_recipe_button = tk.Button(recipe_buttons, text='Save Recipe', font=('Arial', 10), width=20, state='disabled', command=self.save_recipe)
        self.save_recipe_button.grid(row=0, column=0, pady=5)

        self.restore_details_button = tk.Button(recipe_buttons, text='Restore', font='Arial 10', width=15, state='disabled', command=self.restore)
        self.restore_details_button.grid(row=0, column=1, padx=5)

    def recipe_details_frame(self):
        details_frame = tk.Frame(self, relief=tk.FLAT, bg='azure4')
        details_frame.place(relx=0.46, rely=0.57, relwidth=0.49, relheight=0.40)

        sale_summary = tk.LabelFrame(details_frame, text='Sale Summary', font=('Arial', 10, 'bold'), relief=tk.FLAT, fg='white', bg='azure4')
        sale_summary.grid(row=0, column=0)

        self.sale_summary_list = tk.Text(sale_summary, font=('Arial', 10), width=40, height=11, state=tk.DISABLED)
        self.sale_summary_list.grid(row=0, column=0)

        sale_summary_buttons = tk.Frame(sale_summary, relief=tk.FLAT, bg='azure4')
        sale_summary_buttons.grid(row=1, column=0)

        self.generate_recipe_button = tk.Button(sale_summary_buttons, text='Generate Recipe', font=('Arial', 10), state=tk.DISABLED, width=15, command=self.generate_recipe)
        self.generate_recipe_button.grid(row=0, column=0, pady=5)

        self.back_button = tk.Button(sale_summary_buttons, text='Back', font='Arial 10', width=10, command=self.back_sale, state='disabled')
        self.back_button.grid(row=0, column=1, padx=5)

        customer_details_frame = tk.Frame(details_frame, relief=tk.FLAT, bg='azure4')
        customer_details_frame.grid(row=0, column=1, sticky=tk.N, pady=10)
        
        customer_name_frame = tk.LabelFrame(customer_details_frame, text='Customer Name:', font=('Arial', 10, 'bold'), relief=tk.FLAT, fg='white', bg='azure4')
        customer_name_frame.grid(row=0, column=1, padx=10)

        self.customer_name_entry = tk.Entry(customer_name_frame, font=('Arial', 10), bd=1, width=20, textvariable=self.name_var)
        self.customer_name_entry.grid(row=0, column=0, padx=10)

        customer_lastname_frame = tk.LabelFrame(customer_details_frame, text='Customer Last Name:', font=('Arial', 10, 'bold'), relief=tk.FLAT, fg='white', bg='azure4')
        customer_lastname_frame.grid(row=1, column=1, padx=10, pady=7)

        self.customer_lastname_entry = tk.Entry(customer_lastname_frame, font=('Arial', 10), bd=1, width=20, textvariable=self.last_name_var)
        self.customer_lastname_entry.grid(row=0, column=0, padx=10)

        payment_method_frame = tk.LabelFrame(customer_details_frame, text='Payment Method:', font=('Arial', 10, 'bold'), relief=tk.FLAT, fg='white', bg='azure4')
        payment_method_frame.grid(row=2, column=1)

        self.payment_method_combobox = ttk.Combobox(payment_method_frame, width=20, values=['Cash', 'Debit Card'], state='readonly')
        self.payment_method_combobox.current(1-1)
        self.payment_method_combobox.grid(row=0, column=0)

        amount_frame = tk.LabelFrame(customer_details_frame, text='Amount:', font=('Arial', 10, 'bold'), relief=tk.FLAT, fg='white', bg='azure4')
        amount_frame.grid(row=3, column=1, pady=7)

        vcmd = (self.register(self.callback))
        self.amount_entry = tk.Entry(amount_frame, font='Arial 10', width=20, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.amount_var)
        self.amount_entry.grid(row=0, column=0)

        if int(self.amount_var.get()) < self.subtotal:
            messagebox.showerror('Error', 'Invalid amount')

        self.calculate_total_button = tk.Button(customer_details_frame, text='Calculate Total', font=('Arial', 10), width=15, state='disabled', command=lambda:self.calculate_total(self.payment_method_combobox))
        self.calculate_total_button.grid(row=4, column=1, pady=5)

    def on_closing(self):
        if not len(self.sale_summary_list.get('1.0', 'end-1c')) == 0:
            messagebox.showerror('Current sale error', 'You have a pending sale, cancel it with "Restore" button or cleaning the sale summary with "Back" button')
        else:
            self.destroy()

    def callback(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False
    
    def highlight_searched(self, *args):
        search = self.search_var.get()
        for i, item in enumerate(self.listbox.get(0, tk.END)):
            if search.lower() == item.split()[1].lower():
                self.listbox.selection_set(i)
                self.listbox.focus_set()
            else:
                self.listbox.selection_clear(i)
        if search == '':
            self.listbox.selection_clear(0, tk.END)

    def validate(self, *args):
        if self.name_var.get() and self.last_name_var.get() and self.amount_var.get():
            self.calculate_total_button.config(state='normal')
        else:
            self.calculate_total_button.config(state='disabled')

    def delete_product(self):
        try:
            conn = get_conn()
            cursor = conn.cursor()

            query = '''DELETE FROM products WHERE id = %s'''
            cursor.execute(query, (self.listbox.selection_get().split()[0],))

            conn.commit()
            cursor.close()

            self.display_products()
        except:
            messagebox.showerror('Invalid Product', 'Error: You have to select one product of the list')

    def add_product(self):
        from .add_product_toplevel import AddProduct

        AddProduct(self)

    def update_product(self):
        from .update_product_toplevel import UpdateProduct
        try:
            if self.listbox.focus_get() == self.listbox:
                UpdateProduct(self)
            else:
                messagebox.showerror('Invalid Product', 'Error: You have to select one product of the list')
        except:
            messagebox.showerror('Invalid Product', 'Error: You have to select one product of the list')

    def display_products(self):
        global products_frame

        conn = get_conn()
        cursor = conn.cursor()

        query = '''SELECT * FROM products'''
        cursor.execute(query)

        row = cursor.fetchall()

        self.listbox = tk.Listbox(products_frame, width=121, height=9, activestyle='none')
        self.listbox.grid(row=3, column=0)
        self.listbox.grid_rowconfigure(1, weight=1)
        self.listbox.grid_columnconfigure(1, weight=1)

        listFont = font.Font(font=self.listbox.cget('font'))
        product_name_list = [x[2] for x in row]
        price_list = [x[3] for x in row]

        spaceLenght = listFont.measure(" ")
        spacing = 27 * spaceLenght

        productsLengths = [listFont.measure(s) for s in product_name_list]
        longestLengthProducts = max(productsLengths)

        priceLengths = [listFont.measure(s) for s in price_list]
        longestLengthPrice = max(priceLengths)

        count=0

        for x in row:
            p_id, code, name, price, stock = x
            product_name_list.append(int(len(name)))
            neededSpacing1 = longestLengthProducts + spacing - productsLengths[count]
            neededSpacing2 = longestLengthPrice + spacing - priceLengths[count]
            spacesToAdd1 = int(round(neededSpacing1/spaceLenght))
            spacesToAdd2 = int(round(neededSpacing2/spaceLenght))
            count += 1
            self.listbox.insert(tk.END, f'{20*" "}{str(p_id)}{45*" "}{code}{spacesToAdd1*" "}{name}{(spacesToAdd2)*" "}{price}${30*" "}{stock}')

        conn.commit()
        conn.close()

    def get_list_focus(self):
        try:    
            if self.listbox.curselection():
                conn = get_conn()
                cursor = conn.cursor()

                p_id, code, *name_splitted, price, stock = self.listbox.selection_get().split()
                name = ' '.join(str(e) for e in name_splitted)
                price_int = ' '.join(str(e) for e in price.split('$'))

                if not int(stock) <= 0:
                    
                    self.subtotal += int(price_int)
                    self.amount_var.set(self.subtotal)

                    query = '''UPDATE products SET stock = %s WHERE id = %s'''
                    cursor.execute(query, (int(stock)-1, p_id))

                    self.sale_summary_list.config(state='normal')
                    self.sale_summary_list.insert(tk.END, f'Product: {name}, Price: {price_int}$\nSubtotal: {self.subtotal}$\n')
                    self.sale_summary_list.config(state='disabled')

                    self.inserts += 1

                    if self.inserts > 1:
                        self.back += 2
                        
                    conn.commit()
                    cursor.close()
                else:
                    messagebox.showerror('Error', 'Product out of stock, please update it in "Update Product" when available')
                    conn.rollback()
                
                if len(self.sale_summary_list.get('1.0', 'end-1c')) > 0:
                    self.back_button.config(state='normal')


                self.display_products()

            else:
                 messagebox.showerror('Invalid Product', 'Error: You have to select one product of the list')

        except:
            messagebox.showerror('Invalid Product', 'Error: You have to select one product of the list')

    def back_sale(self):
        conn = get_conn()
        cursor = conn.cursor()

        string = self.sale_summary_list.get(self.back, self.back+1)
        string_splitted = re.split(', | ', string)
        _, *name_splitted, _, price, _ = string_splitted
        name = ' '.join(str(e) for e in name_splitted)
        
        self.subtotal -= int(price)
        self.amount_var.set(self.subtotal)

        query_select = '''SELECT stock FROM products WHERE name = %s'''
        cursor.execute(query_select, (name,))

        stock = cursor.fetchone()

        conn.commit()

        query = '''UPDATE products SET stock = %s WHERE name = %s'''
        cursor.execute(query, (stock[0]+1, name))

        self.sale_summary_list.config(state='normal')
        self.sale_summary_list.delete(self.back, self.back+2)
        self.sale_summary_list.config(state='disabled')
        self.back -= 2

        if len(self.sale_summary_list.get('1.0', 'end-1c')) == 0:
            self.back_button.config(state='disabled')

        conn.commit()
        cursor.close()

        self.display_products()

    def calculate_total(self, payment):
        if len(self.sale_summary_list.get('1.0', 'end-1c')) > 0:
            taxes = self.subtotal * 0.07
            total = self.subtotal + taxes
            change = (int(self.amount_var.get()) + taxes) - total

            if self.amount_var.get() < self.subtotal:
                messagebox.showerror('Error', 'Insufficient amount')

            self.sale_summary_list.config(state='normal')
            self.sale_summary_list.insert(tk.END, f'\nSubtotal: {self.subtotal}$\nTaxes: {round(taxes, 2)}$\nTotal: {round(total, 2)}$\nChange: {round(change, 2)}$\nPayment Method: {payment.get()}')
            self.sale_summary_list.config(state='disabled')

            self.back_button.config(state='disabled')
            self.calculate_total_button.config(state='disabled')
            self.sale_button.config(state='disabled')
            self.generate_recipe_button.config(state='normal')
            self.customer_name_entry.config(state='disabled')
            self.customer_lastname_entry.config(state='disabled')
            self.payment_method_combobox.config(state='disabled')
            self.amount_entry.config(state='disabled')
            self.restore_details_button.config(state='normal')
        else:
            messagebox.showerror('Miscalculation', 'The sale summary list is empty')

    def generate_recipe(self):
        conn = get_conn()
        cursor = conn.cursor()

        recipe_number = f'N# - {random.randint(1000, 9999)}'
        date = datetime.datetime.now()
        recipe_date = f'{date.day}/{date.month}/{date.year} - {date.hour}:{date.minute}'
        product_names = []
        name_price_dicc = {}
        taxes = self.subtotal * 0.07
        total = self.subtotal + taxes

        self.recipe_text.config(state='normal')
        self.recipe_text.insert('end', f'Data: {recipe_number} - {recipe_date}\n')
        self.recipe_text.insert('end', f'Name: {self.name_var.get()}\tLastname: {self.last_name_var.get()}\n')
        self.recipe_text.insert('end', f'*' * 80 + '\n')
        self.recipe_text.insert('end', f'Quantity\t{" "*5}Price\t\tProduct\n')
        self.recipe_text.insert('end', f'*' * 80 + '\n')

        for e in re.split(', | ', self.sale_summary_list.get('1.0', 'end')):
            for i, item in enumerate(self.listbox.get(0, 'end')):
                if e == item.split()[2]:
                    query = '''SELECT name, price FROM products WHERE id = %s'''
                    cursor.execute(query, (item.split()[0],))

                    name, price = cursor.fetchone()

                    name_price_dicc[name] = price
                    product_names.append(name)

        for name, price in name_price_dicc.items():
            quantity = product_names.count(name)
            self.recipe_text.insert('end', f'{quantity}\t{" "*5}{price}$\t\t{name}\n')

        self.recipe_text.insert('end', f'\nSubtotal: {self.subtotal}$\nTaxes: {round(taxes, 2)}$\nTotal: {round(total, 2)}$')
        self.generate_recipe_button.config(state='disabled')
        self.recipe_text.config(state='disabled')
        self.save_recipe_button.config(state='normal')
        self.restore_details_button.config(state='disabled')

        conn.commit()
        cursor.close()

    def restore(self):
        conn = get_conn()
        cursor = conn.cursor()

        product_names = []
        name_stock_dicc = {}

        if len(self.sale_summary_list.get('1.0', 'end-1c')) > 0:
            for e in re.split(', | ', self.sale_summary_list.get('1.0', 'end')):
                for i, item in enumerate(self.listbox.get(0, 'end')):
                    if e == item.split()[2]:
                        query = '''SELECT name, stock FROM products WHERE id = %s'''
                        cursor.execute(query, (item.split()[0],))

                        name, stock = cursor.fetchone()

                        name_stock_dicc[name] = stock
                        product_names.append(name)

                        conn.commit()

            for name, stock in name_stock_dicc.items():
                quantity = product_names.count(name)

                query2 = '''UPDATE products SET stock = %s WHERE name = %s'''
                cursor.execute(query2, (stock+quantity, name))

                conn.commit()

            cursor.close()

            self.subtotal = 0
            self.inserts = 0
            self.back = 1.0

            self.amount_var.set(self.subtotal)

            self.recipe_text.config(state='normal')
            self.recipe_text.delete('1.0', 'end')
            self.recipe_text.config(state='disabled')

            self.sale_summary_list.config(state='normal')
            self.sale_summary_list.delete('1.0', 'end')
            self.sale_summary_list.config(state='disabled')

            self.sale_button.config(state='normal')
            self.customer_name_entry.config(state='normal')
            self.customer_name_entry.delete(0, 'end')
            self.customer_lastname_entry.config(state='normal')
            self.customer_lastname_entry.delete(0, 'end')
            self.payment_method_combobox.config(state='normal')
            self.amount_entry.config(state='normal')
            self.restore_details_button.config(state='disabled')
            self.save_recipe_button.config(state='disabled')
            self.generate_recipe_button.config(state='disabled')

            self.display_products()
        else:
            messagebox.showerror('Error', 'There\'s no item\'s to restore, the sale summary list is empty')

    def save_recipe(self):
        dir_path = Path(Path.home(), 'Desktop', 'Recipes')
        date = datetime.datetime.now()
        current_customer = f'{self.name_var.get()} {self.last_name_var.get()}'
        filename = f'Recipe - {current_customer}'
        recipe_info = self.recipe_text.get('1.0', 'end')

        if os.path.exists(dir_path):
            new_file = Path(dir_path, filename + '.txt')
        else:
            Path.mkdir(dir_path)
            new_file = Path(dir_path, filename + '.txt')
        Path.write_text(new_file, recipe_info)

        self.subtotal = 0
        self.inserts = 0
        self.back = 1.0

        self.amount_var.set(self.subtotal)

        self.recipe_text.config(state='normal')
        self.recipe_text.delete('1.0', 'end')
        self.recipe_text.config(state='disabled')

        self.sale_summary_list.config(state='normal')
        self.sale_summary_list.delete('1.0', 'end')
        self.sale_summary_list.config(state='disabled')

        self.sale_button.config(state='normal')
        self.customer_name_entry.config(state='normal')
        self.customer_name_entry.delete(0, 'end')
        self.customer_lastname_entry.config(state='normal')
        self.customer_lastname_entry.delete(0, 'end')
        self.payment_method_combobox.config(state='normal')
        self.amount_entry.config(state='normal')
        self.restore_details_button.config(state='disabled')
        self.save_recipe_button.config(state='disabled')
        self.generate_recipe_button.config(state='disabled')

        messagebox.showinfo('Saved', 'The recipe has been saved on your desktop')

    def get_product_from_id(self):
        conn = get_conn()
        cursor = conn.cursor()

        query = '''SELECT name, price, stock FROM products WHERE id = %s'''
        cursor.execute(query, (self.listbox.selection_get().split()[0],))

        item = cursor.fetchone()

        conn.commit()
        conn.close()

        return item
    
    def get_product_id(self):

        id = self.listbox.selection_get().split()[0]

        return id
        

        
