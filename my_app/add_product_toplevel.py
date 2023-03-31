import string
import random
import tkinter as tk
from tkinter import ttk
from .app import App
from .database import get_conn

class AddProduct(tk.Toplevel):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.root = root
        self.geometry('200x250+900+400')
        self.title('Add Product')
        self.resizable(0, 0)
        self.submit_button = tk.Button()
        self.product_name_var = tk.StringVar()
        self.product_price_var = tk.StringVar()
        self.current_value = tk.StringVar(value=5)
        self.configure(bg='azure4')
        self.grab_set()
        self.product_name_var.trace("w", self.validate)
        self.product_price_var.trace("w", self.validate)
        self.current_value.trace("w", self.validate)
        self.product_form()

    def product_form(self):
        form_frame = tk.Frame(self, relief=tk.FLAT, bg='azure4')
        form_frame.place(relx=0.13, rely=0.03)

        product_name_frame = tk.LabelFrame(form_frame, text='Product Name:', font='Arial 10 bold', relief=tk.FLAT, fg='white', bg='azure4')
        product_name_frame.grid(row=0, column=0)
        
        product_name_entry = tk.Entry(product_name_frame, font='Arial 10', bd=1, width=20, textvariable=self.product_name_var)
        product_name_entry.grid(row=0, column=0, pady=5)
        self.product_name_var.trace("w", lambda *args: self.entry_char_limit(self.product_name_var))

        max_length_label = tk.Label(product_name_frame, text='Max Length: 20', font='Arial 8 bold', fg='white', bg='azure4')
        max_length_label.grid(row=1, column=0)

        product_price_frame = tk.LabelFrame(form_frame, text='Product Price:', font='Arial 10 bold', relief=tk.FLAT, fg='white', bg='azure4')
        product_price_frame.grid(row=1, column=0, pady=5)

        vcmd = self.register(self.callback)
        product_price_entry = tk.Entry(product_price_frame, font='Arial 10', bd=1, width=20, textvariable=self.product_price_var, validate='all', validatecommand=(vcmd, '%P'))
        product_price_entry.grid(row=0, column=0, pady=5)
        self.product_price_var.trace("w", lambda *args: self.entry_int_limit(self.product_price_var))

        product_stock_frame = tk.LabelFrame(form_frame, text='Stock:', font='Arial 10 bold', relief=tk.FLAT, fg='white', bg='azure4')
        product_stock_frame.grid(row=2, column=0)

        product_stock_entry = ttk.Spinbox(product_stock_frame, from_=5, to=40, font='Arial 10', textvariable=self.current_value, width=18, wrap=True, state='readonly')
        product_stock_entry.grid(row=0, column=0, pady=5)

        buttons_frame = tk.Frame(form_frame, relief=tk.FLAT, bg='azure4')
        buttons_frame.grid(row=3, column=0)

        self.submit_button = tk.Button(buttons_frame, text='Submit', font='Arial 10', width=7, state='disabled',command=lambda:self.get_product_data(product_name_entry, product_price_entry, product_stock_entry))
        self.submit_button.grid(row=0, column=0, pady=5)

        cancel_button = tk.Button(buttons_frame, text='Cancel', font='Arial 10', width=7, command=self.close_windows)
        cancel_button.grid(row=0, column=1, padx=5)

    def entry_char_limit(self, entry_text):
        if len(entry_text.get()) > 0:
            entry_text.set(entry_text.get()[:20])

    def entry_int_limit(self, entry_int):
        if len(entry_int.get()) > 0:
            entry_int.set(entry_int.get()[:3])

    def validate(self, *args):

        if self.product_name_var.get() and self.product_price_var.get() and self.current_value.get():
            self.submit_button.config(state='normal')
        else:
            self.submit_button.config(state='disabled')

    def get_product_data(self, *args):
        conn = get_conn()
        cursor = conn.cursor()

        name, price, stock = args
        code = f'{random.randint(10, 50)}{random.choice(string.ascii_lowercase)}{random.randint(0, 9)}'

        query = '''INSERT INTO products(code, name, price, stock) VALUES (%s, %s, %s, %s)'''
        cursor.execute(query, (code, name.get(), price.get(), stock.get()))
        conn.commit()
        conn.close()

        # Refresh list
        App.display_products(self.root)

        self.destroy()

    def close_windows(self):
        self.destroy()

    def callback(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False


