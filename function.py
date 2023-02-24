import sys
from datetime import datetime, timedelta
import csv
import os
from os.path import exists
from rich.table import Table
from rich.console import Console
from tabulate import tabulate
from rich import print
import json
import matplotlib.pyplot as plt
import pandas

# Set date with now and string type now.
now = datetime.now()
strnow = now.strftime("%Y-%m-%d")

# Make a general path
date_path = os.path.join(sys.path[0], 'date.txt')
csv_bought_file = os.path.join(sys.path[0], 'bought.csv')
csv_sold_file = os.path.join(sys.path[0], 'sold.csv')

# If files do not exist, create files (bought_csv, sold_csv)
if not os.path.exists(csv_bought_file):
    with open(csv_bought_file, 'w', newline='') as f:
        header = ['id', 'product_name', 'buy_date', 'amount', 'buy_price', 'expiration_date']
        writer = csv.DictWriter(f, delimiter=',', fieldnames = header)
        writer.writeheader()

if not os.path.exists(csv_sold_file):
    with open(csv_sold_file, 'w', newline='') as f: 
        header = ['id', 'product_name', 'sell_date', 'amount', 'sell_price', 'bought_id']
        writer = csv.DictWriter(f, delimiter=',', fieldnames = header)
        writer.writeheader()

 # Create a date file if it doesn't exist, today is the day if there was no previous date set
def get_date():
    if not os.path.exists(date_path):
        with open(date_path, 'w') as file:
            file.write(strnow) 
        set_date = strnow  
    
    else:
        with open(date_path, 'r') as f:
            set_date = f.readline()
    return set_date

# Create date file with format YYYY-MM-DD with advance_date(d_days)
def advance_date(d_days):
    advance_date = datetime.strftime(now + timedelta(days=int(d_days)), '%Y-%m-%d')
    if not os.path.exists(date_path):
        with open(date_path, 'w') as file:
            file.write(advance_date)

    print(f"[blue]The current date is changed with {advance_date} in this program by advanced {d_days} days.[/blue]")

# Add a new buy item to bought file
def buy_item(buy_csv_file, product_name, amount, buy_price, expiration_date):
    buy_date = get_date()

    with open(buy_csv_file, 'r+', newline='') as f:
        reader = csv.DictReader(f)
        last_buy_id = 0
        for row in reader:
            last_buy_id = row['id']
        new_row = [int(last_buy_id)+1, product_name, buy_date, amount, buy_price, expiration_date]
        writer = csv.writer(f)
        writer.writerow(new_row)

    print(f"[blue]Added new product {product_name} to bought.csv[/blue]")

# Add a new sold item to sold file if a new item is at stock.
def sell_item(sell_csv_file, product_name, amount, price):
    sell_date = get_date()

    with open(sell_csv_file, 'r+', newline='') as f:
        reader = csv.DictReader(f)
        last_sold_id = 0
        for row in reader:
            last_sold_id = row['id']

    prod_available = False
    for item in create_inventory(csv_bought_file, csv_sold_file):
        if product_name == item['product_name']:
            if item['stock'] == 0:
                continue
            elif item['expired'] == 1:
                continue
            elif amount > int(item['stock']):
                with open (sell_csv_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    new_row = [int(last_sold_id)+1, product_name, sell_date, int(item['stock']), price, item['id']]
                    writer.writerow(new_row)
                    last_sold_id = int(last_sold_id)+1
                    prod_available = True
                    amount = amount - int(item['stock'])
                continue
            elif amount <= int(item['stock']):
                with open (sell_csv_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    new_row = [int(last_sold_id)+1, product_name, sell_date, amount, price, item['id']]
                    writer.writerow(new_row)
                    prod_available = True
                    amount = 0
                break
            else:
                with open (sell_csv_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    new_row = [int(last_sold_id)+1, product_name, sell_date, amount, price, item['id']]
                    writer.writerow(new_row)
                    prod_available = True
                    amnt = 0
                break
        else:
            continue

    if amount != 0 or prod_available == False:
        print(f'item {product_name} is not enough in stock.')


# Create inventory item list which is not sold and not expired, firstly check the set date.
def create_inventory(csv_bought_file, csv_sold_file):
    if exists(date_path):
        with open(date_path, 'r') as f:
            advance_date = f.readline()
        advance_date = datetime.strptime(advance_date, '%Y-%m-%d')
    else:
        advance_date = now

    selected_stock = []    
    with open(csv_bought_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['stock'] = row['amount']
            if datetime.strptime(row['expiration_date'], '%Y-%m-%d') > datetime.strptime(get_date(), '%Y-%m-%d'):
                row['expired'] = 0
            else:
                row['expired'] = 1
            selected_stock.append(row)

    sold_item_list = []
    with open(csv_sold_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sold_item_list.append(row)

    for item in sold_item_list:
        sold_product_name = item['product_name']
        sold_amount = int(item['amount'])
        bought_id = item['bought_id']
        for item in selected_stock:
            if sold_product_name == item['product_name'] and bought_id == item['id']:
                stock = int(item['stock'])
                if stock == 0:
                    continue
                elif stock > sold_amount:
                    item['stock'] = stock - sold_amount
                    break
                else :
                    item['stock'] = 0
                    break
            else:
                continue
    return selected_stock
#Create inventory table by rich.table
def create_inventory_table():
    table = Table(title="Inventory", show_header=True, header_style="yellow", border_style="magenta")
    table.add_column("id", no_wrap=True)
    table.add_column("product_name", no_wrap=True)
    table.add_column("amount", justify="center", no_wrap=True,)
    table.add_column("buy_price", justify="center", no_wrap=True)
    table.add_column("buy_date", justify="center", no_wrap=True)
    table.add_column("expiration_date", justify="center", no_wrap=True)

    for item in create_inventory(csv_bought_file, csv_sold_file):
        if item['stock'] != 0 and item['expired']!=1:
            table.add_row(item['id'], item['product_name'], str(item['stock']), item['buy_price'], item['buy_date'], item['expiration_date'])
    console = Console()
    print('')
    console.print(table)

# Create revenue for each item with a given date
def create_revenue_table(check_date):
    sold_item_list = []
    with open(csv_sold_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sold_item_list.append(row)

    revenue = 0
    for item in sold_item_list:
        sell_price = float(item['sell_price'])
        sell_amount = float(item['amount'])
        if item['sell_date'] == check_date:
            revenue = revenue + (sell_price*sell_amount)
            item['revenue'] = revenue
 
    table = Table(title= f"Revenue on {check_date}", show_header=True, header_style="yellow")
    table.add_column("product_name", no_wrap=True, style="green", width=12)
    table.add_column("revenue", width=12, no_wrap=True, justify="center", style="yellow")
   
    for item in sold_item_list:
        table.add_row( item['product_name'], str(item['revenue']))
    console = Console()
    print('')
    console.print(table)

#Calculate cost for a certain date
def cost(check_date):
    bought_item_list = []
    with open(csv_bought_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bought_item_list.append(row)

    cost = 0
    for item in bought_item_list:
        buy_price = float(item['buy_price'])
        buy_amount = float(item['amount'])
        if item['buy_date'] == check_date:
            cost = cost + (buy_price*buy_amount)

    print(f"[green]{check_date}'s cost is {cost} euros[/green]")

#Calculate profit with a certain date
def profit(check_date):   
    sold_list = []
    bought_list = []
    with open(csv_sold_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sold_list.append(row)
    
    with open(csv_bought_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bought_list.append(row)

    new_sold_list = []
    for sold_item in sold_list:
        if sold_item['sell_date'] == str(check_date):
            new_key = dict()
            new_key['product_name'] = sold_item['product_name']
            sold_price_total = float(sold_item['sell_price']) * float(sold_item['amount'])
            for bought_item in bought_list:
                if bought_item['id'] == sold_item['bought_id']:
                    bought_price_total = float(sold_item['amount']) * float(bought_item['buy_price'])
                    new_key['profit'] = sold_price_total - bought_price_total
                    new_sold_list.append(new_key)
                    break    
    
    profit_list = []
    for new_product in new_sold_list:
        product_is_known = False
        for product in profit_list:
            if new_product["product_name"] == product["product_name"]:
                product_is_known = True
                product["profit"] += new_product["profit"]
        if not product_is_known:
            profit_list.append(new_product)
        product_is_known = False
    
    table = Table(title=f"Profit on {check_date}", show_header=True, header_style="yellow")
    table.add_column("product_name", no_wrap=True)
    table.add_column("profit", no_wrap=True)

    for item in profit_list:
        table.add_row(item['product_name'], str(item['profit']))
    console = Console()
    print('')
    console.print(table)      

# Visualize as a graph about revenue per day


# Make a path for json file first. Then export inventory data to json file
json_file = os.path.join(f'inventory-{strnow}.json')

def export_inventory_json(csv_bought_file, json_file):
    json_array = []
    with open(csv_bought_file, encoding='utf-8') as f: 
        reader = csv.DictReader(f) 
        for row in reader: 
            json_array.append(row)
    
    with open(json_file, 'w+', encoding='utf-8') as f: 
        f.write(json.dumps(json_array, indent=4))
    
    csv_bought_file = r'data.csv'
    json_file = r'data.json'
    
    print(f' Data exported to inventory export [magenta]{strnow}[/magenta] .json')

# Delete all the items on the files(bought file and sold file) up to set_date(advance_date)
def reset_date():
    with open(date_path, 'w') as file:
        file.write(strnow) 
    
    with open(csv_bought_file, 'r') as inp, open(csv_bought_file, 'w', newline='') as outp:
        reader = csv.DictReader(inp)
        headers = ['id', 'product_name', 'buy_date', 'amount', 'buy_price', 'expiration_date']
        writer = csv.DictWriter(outp, delimiter=',', fieldnames = headers)
        writer.writeheader()
        for row in reader:
            buy_date = datetime.strptime(row['buy_date'], '%Y-%m-%d')
            if buy_date <= now:
                writer.writerow(row)
    
    with open(csv_sold_file, 'r') as inp, open(csv_sold_file, 'w', newline='') as outp:
        reader = csv.DictReader(inp)
        headers = ['id', 'product_name', 'sell_date', 'amount', 'sell_price', 'bought_id']
        writer = csv.DictWriter(outp, delimiter=',', fieldnames = headers)
        writer.writeheader()
        for row in reader:
            sell_date = datetime.strptime(row['sell_date'], '%Y-%m-%d')
            if sell_date <= now:
                writer.writerow(row)

    print(f'[red]All the items in files are removed from the set date {strnow}[/red]')