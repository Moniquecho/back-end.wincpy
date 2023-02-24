# Imports
import argparse
import csv
from datetime import date
from function import*

# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"


# Your code below this line.



def parser():
    # Add a parser for commandline input
    parser = argparse.ArgumentParser(prog="SuperPy",
                                    description="Supermarket inventory management tool through command line")
    subparsers = parser.add_subparsers(dest="command")

    # Create a Buy Sub-parser
    buy_parser = subparsers.add_parser("buy", help="Register buy_product")
    buy_parser.add_argument("-pro","--product_name", required=True, help="Name of buy product", type=str)
    buy_parser.add_argument("-amount", required=True, help="Insert the amount of buy product", type=int)
    buy_parser.add_argument("-pri", "--price", required=True, help="Insert buy price", type=float)
    buy_parser.add_argument("-exp", "--expiration_date", required=True, help="Insert expiration date as YYYY-MM-DD")

    # Create a Sell Sub-parser
    sell_parser = subparsers.add_parser("sell", help="Register buy_product")
    sell_parser.add_argument("-pro", "--product_name", required=True, help="Name of sell product", type=str)
    sell_parser.add_argument("-amount", required=True, help="Insert the amount of sell product", type=int)
    sell_parser.add_argument("-pri", "--price", required=True, help="Insert sell price", type=float)

    # Create a Report Sub-parser
    report_parser = subparsers.add_parser("report", help="Reporting inventory, revenue, cost and profit on a given date")
    report_parser.add_argument("mode", choices=["inventory", "revenue","cost","profit"])
    report_parser.add_argument("-check_date", help="Enter date in YYYY-MM-DD for 'report revenue' or 'report cost' or 'report profit'", type=str)
    
    graph_parser = subparsers.add_parser('visual', help="show expense graph")
    graph_parser.add_argument("mode", choices = ['graph', 'json'])

    # Create an Advance Date Sub-parser
    date_parser = subparsers.add_parser("advance_date",
                    help="Type a number of days you want to test in the future or reset back to today")
    date_parser.add_argument("mode", choices=["time_delta", "reset"])
    date_parser.add_argument("-d", "--d_days", help="Insert 'advance_date time_delta' to advance time by", type=int)
    
    return parser.parse_args() 

    # Create an Argument parser with if loops to check the input
def main():
    args = parser()

    if args.command == 'buy':
        buy_item(csv_bought_file, args.product_name, args.amount, args.price, args.expiration_date)

    if args.command == 'sell':
        sell_item(csv_sold_file, args.product_name, args.amount, args.price)

    if args.command == 'report':
        if args.mode == 'inventory':
            create_inventory_table()
        elif args.mode == 'revenue':
            create_revenue_table(args.check_date)   
        elif args.mode == 'cost':
            cost(args.check_date)    
        elif args.mode == 'profit':
            profit(args.check_date)

    if args.command == 'visual':
        
        if args.mode == 'json':
            export_inventory_json(csv_bought_file,  json_file)

    if args.command == 'advance_date':
        if args.mode == 'time_delta':
            advance_date(args.d_days)
        elif args.mode == 'reset':
            reset_date()

if __name__ == "__main__":
    main()    
