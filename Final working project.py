import pyodbc # to establish cinnection with sql server
from datetime import datetime, date # handling datetime column in database
from collections import deque # using queue as the appropriate data structure for our task.
from queue import Queue # optimising the code in the class connectionmanager
from threading import Lock # keeping the database connected.
import os # clearing the terminal to make it userfreindly.
import maskpass # covering the password.

# providing extra modularity by defining a class for connection with sql server.
class ConnectionManager:
    def __init__(self, min_connections, max_connections, **kwargs):
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.conn_queue = Queue(maxsize=max_connections)
        self.lock = Lock()
        self.conn_params = kwargs

        # Initialize connections
        for _ in range(min_connections):
            self._create_connection()

    def _create_connection(self):
        conn = pyodbc.connect(**self.conn_params)
        self.conn_queue.put(conn)

    def get_connection(self):
        # Ensure thread safety
        with self.lock:
            if self.conn_queue.empty() and len(self.conn_queue.queue) < self.max_connections:
                self._create_connection()
        return self.conn_queue.get()

    def release_connection(self, conn):
        self.conn_queue.put(conn)

    def close_all_connections(self):
        while not self.conn_queue.empty():
            conn = self.conn_queue.get()
            conn.close()

# this is a helper function for optimising the code.
def execute_sql_query(query, params=None, fetch_data=False):
    try:
        # Acquire a connection from the connection manager
        conn = conn_manager.get_connection()
        cursor = conn.cursor()
        
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)

        if fetch_data:
            return cursor.fetchall()
        else:
            return None
    except pyodbc.Error as e:
        print(f"Error executing SQL query: {e}")
        return None
    finally:
        # Release the connection back to the connection manager
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None:
            conn_manager.release_connection(conn)


# Define function to update data to SQL server
def update_data_to_sql(queue):
    try:
        # Acquire a connection from the connection manager
        conn = conn_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT MAX(ID) FROM Request;')
        id = cursor.fetchone()[0] + 1

        # Execute the SQL query with parameters
        cursor.execute("SELECT * FROM Servicename WHERE ServiceTypeID = ?", (int(queue[3][0])))

        # Fetch the requiered rows
        service = cursor.fetchall()[int(queue[3][1])-1][0]

        token_no, date_time, req_by, req_type = queue[0], queue[1], queue[2], service
        cursor.execute("INSERT INTO Request (ID, TokenNum, Date_Time, RaisedBy, ServiceID, Processed) VALUES (?, ?, ?, ?, ?, ?)",
                        (id, token_no, date_time, req_by, req_type, 0))

        # Commit the transaction
        conn.commit()

        # Release the connection back to the connection manager
        cursor.close()
        conn_manager.release_connection(conn)
        
        print("Data successfully updated to SQL server.")
    except pyodbc.Error as e:
        print(f"Error updating data to SQL server: {e}")

# checking if log in credentials match the database and returning the role.
def login_verify(username, password):
    try:
        # Execute SQL query to verify login credentials
        query = "SELECT RoleID FROM Users WHERE UserName = ? AND Passwords = ?"
        params = (username, password)
        result = execute_sql_query(query, params,fetch_data=True)
        if result:
            role = result[0][0]
            print("Logged in successfully.")
            return role
        print('Error invalid Username or password,')
    except Exception as e:
        print(f"Error verifying login credentials: {e}")
        return None

# for employes to update each request as prosesed in the database.
def processed_update(queue):
    try:
        # Execute SQL query to update processed status
        query = "SELECT * FROM Servicename WHERE ServiceTypeID = ?"
        params = (int(queue[3][0]),)
        service = execute_sql_query(query, params,fetch_data=True)[int(queue[3][1])-1][0]

        # Update the Processed column
        query = "UPDATE Request SET Processed = ? WHERE TokenNum = ? AND Date_Time = ? AND RaisedBy = ? AND ServiceID = ?"
        params = (1, queue[0], queue[1], queue[2], service)
        execute_sql_query(query, params)

        print("User request processed.")
    except pyodbc.Error as e:
        print(f"Error updating data to SQL server: {e}")

# 1st functionality for admin users
def admin_service_table_update(operation1, service_name1, service_number=-1):
    try:
        # Execute SQL query to update service table
        query = 'SELECT MAX(ID) FROM Servicename;'
        max_id = execute_sql_query(query,fetch_data=True)[0][0] + 1

        if int(operation1) == 1:
            query = "INSERT INTO Servicename (ID, ServiceTypeID, ServicesName) VALUES (?, ?, ?);"
            params = (max_id, service_number, service_name1)
        else:
            query = "DELETE FROM Servicename WHERE ServicesName = ?;"
            params = (service_name1,)
        
        execute_sql_query(query, params)
        print("Data successfully updated.")
    except pyodbc.Error as e:
        print(f"Error updating data to SQL server: {e}")

# 2nd functionality for admin users
def admin_service_type_update(operation1, service_name1):
    try:
        if operation1 == '2':
            query = "DELETE FROM ServiceType WHERE ServiceType = ?;"
            params = (service_name1,)
            execute_sql_query(query, params)
            print("Data successfully updated.")
            return

        query = 'SELECT MAX(ID) FROM ServiceType;'
        max_id = execute_sql_query(query,fetch_data=True)[0][0] + 1
        query = "INSERT INTO ServiceType (ID, ServiceType) VALUES (?, ?);"
        params = (max_id, service_name1)
        execute_sql_query(query, params)
        print("Data successfully updated.")
    except pyodbc.Error as e:
        print(f"Error updating data: {e}")

# 3rd functionality for admin users
def admin_request_view(type, date1=(0, 0)):
    try:
        # Acquire a connection from the connection manager
        conn = conn_manager.get_connection()
        cursor = conn.cursor()

        if type == '1':
            cursor.execute("SELECT * FROM Request WHERE Processed = '0';")
        elif type == '2':
            # Get today's date and format it as a string in the required date format
            today_date_str = date.today().strftime('%Y-%m-%d')

            # Execute the SQL query with the formatted date
            cursor.execute("SELECT * FROM Request WHERE CAST(Date_Time AS DATE) = ?;", (today_date_str,))
        else:
            cursor.execute("SELECT * FROM Request WHERE Date_Time BETWEEN ? AND ?;", date1)

        # Fetch all rows from the cursor
        rows = cursor.fetchall()

       # Define the header
        header = "{:<5} {:<10} {:<25} {:<30} {:<10} {:<10}".format("ID", "TokenNum", "Date_Time", "RaisedBy", "ServiceID", "Processed")

        # Print the header
        print("-" * len(header))
        print(header)
        print("-" * len(header))

        # Print each row of data
        for row in rows:
            # Format datetime value properly
            formatted_date_time = row[2].strftime('%Y-%m-%d %H:%M:%S')

            # Format the row string
            row_str = "{:<5} {:<10} {:<25} {:<30} {:<10} {:<10}".format(row[0], row[1], formatted_date_time, row[3], row[4], row[5])
            print(row_str)

        # Print the footer
        print("-" * len(header))
    except pyodbc.Error as e:
        print(f"Error updating data: {e}")

# Define function to print the main page
def mainpage_display():
    displayed_numbers = [1, 2]
    print("\nCustomer Service Request", "1 Login".rjust(70))
    print("\n" + "-"*100)
    print("\033[1m" + "Accounts Services".ljust(40) + "\033[0m" + "\033[1m" + "Deposit Services".ljust(40) + "\033[0m" + "\033[1m" + "Loan Services" + "\033[0m")
    max_length = max(len(type_structure['Accounts']), len(type_structure['Deposits']), len(type_structure['Loans']))
    for i in range(max_length):
        account = type_structure['Accounts'][i] if i < len(type_structure['Accounts']) else ''
        deposit = type_structure['Deposits'][i] if i < len(type_structure['Deposits']) else ''
        loan = type_structure['Loans'][i] if i < len(type_structure['Loans']) else ''
        account_str = f"{str(i + 11)} {account}".ljust(40) if account else ""
        deposit_str = f"{str(i + 21)} {deposit}".ljust(40) if deposit else ""
        loan_str = f"{str(i + 31)} {loan}" if loan else ""
        print(f"{account_str}{deposit_str}{loan_str}")
        if account_str:
            displayed_numbers.append(i + 11)
        if deposit_str:
            displayed_numbers.append(i + 21)
        if loan_str:
            displayed_numbers.append(i + 31)
    print("-"*100 + "\n")
    print("2 Exit".rjust(70))
    return displayed_numbers

# for formaitng the admin display page
def adminpage_display(user_name):
    print(f"\n\nUser Name:  {user_name}")
    print("Password: ***\n")
    print("-" * 30)  
    
    print("1\tManage Services")
    print("2\tManage Service Types")
    print("3\tView Service Requests")
    print("4\tLog out")
    print("-" * 30)  
    return [1,2,3,4] # returns a valid input list.

# for formating the manager display page.
def managerpage_display(user_name,queue):
    print(f"\n\nUser Name:  {user_name}")
    print("Password: ***\n")
    print("-" * 30)  # Separator after password
    
    print("1) View Queue")
    print("2) Accept Request")
    print("3) Log out")
    print("-" * 30)  # Separator at the end
    return [1,2,3] # returns a valid input list.

# Define function to validate user input
def user_input_validity(number, num_list):
    while True:
        try:
            if int(number) in num_list:
                return number
            else:
                print("Invalid input. Please enter a different number.")
                print(num_list)
                number = input("Enter a number from the ablove list: ")
        except ValueError:
            print("Invalid input. Please enter a valid integer from this list.")
            print(num_list)
            number = input("Enter a number from the ablove list: ")

# for formating the queue history, used by employes.
def check_queue_history(machine_queue):
    """Checks and prints the queue history for a given machine."""
    print("Queue History:")
    header = "{:<20} {:<20} {:<20}".format("Date_Time", "RaisedBy", "ServiceID")
    print(header)
    for idx, item in enumerate(machine_queue, start=1):
        if len(item) == 4:  # Check if the item has all 4 values
            date_time, raised_by, service_id = item[1:]  # Exclude the first value
            date_time_str = date_time.strftime('%Y-%m-%d %H:%M:%S')  # Format datetime as string
            print("{:<20} {:<20} {:<20}".format(date_time_str, raised_by, service_id))
        else:
            print("Incomplete data in queue item:", item)

# checking if ServicesName exist in database
def check_db_service_name(service_name):
    try:
        # Acquire a connection from the connection manager
        conn = conn_manager.get_connection()
        cursor = conn.cursor()

        # Execute a query to check if the service name exists in the Servicename table
        cursor.execute("SELECT ServicesName FROM Servicename WHERE ServicesName = ?;", (service_name,))
        existing_service = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        conn_manager.release_connection(conn)

        # Return True if the service name exists, False otherwise
        return existing_service is not None
    except pyodbc.Error as e:
        print(f"Error checking service name existence: {e}")
        return False

# checking if service types exist in database
def check_db_service_type(service_name):
    try:
        # Acquire a connection from the connection manager
        conn = conn_manager.get_connection()
        cursor = conn.cursor()

        # Execute a query to check if the service name exists in the Servicename table
        cursor.execute("SELECT ServiceType FROM ServiceType WHERE ServiceType = ?;", (service_name,))
        existing_service = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        conn_manager.release_connection(conn)

        # Return True if the service name exists, False otherwise
        return existing_service is not None
    except pyodbc.Error as e:
        print(f"Error checking service name existence: {e}")
        return False

# this is for making sure token number is updated on daily bases not on exiting the app.
def initialise_token():
    # Get a connection from ConnectionManager
    conn = conn_manager.get_connection()
    cursor = conn.cursor()

    # Check if date of today is equal to the last date in the Request table
    cursor.execute("SELECT TOP 1 TokenNum, Date_Time FROM Request ORDER BY Date_Time DESC")
    last_entry = cursor.fetchone()

    if last_entry:
        last_entry_date = last_entry.Date_Time.date()
        today = date.today()
        if today == last_entry_date:
            token = last_entry.TokenNum + 1
        else:
            token = 1
    else:
        token = 1

    # Close cursor and release connection
    cursor.close()
    conn_manager.release_connection(conn)
    return token

# Define dictionary for efficency in formating
type_structure = {
    'Accounts': ['Open new account', 'Cheque Deposit', 'Cash Deposit', 'Withdraw', 'Request Passbook Update', 'Request Cheque Book', 'Close Account'],
    'Deposits': ['Open FD', 'Open RD', 'Deposit', 'Close FD', 'Close RD'],
    'Loans': ['Apply for new loan', 'EMI Payment', 'Close Loan', 'Foreign exchange transactions']
}

# Define your database connection parameters, for easy modification.
db_params = {
    'DRIVER': '{SQL Server}',
    'SERVER': 'JEWEL',
    'DATABASE': 'Bank_Db',
    'Trusted_Connection': 'yes'
}

# Initialize a connection manager
conn_manager = ConnectionManager(min_connections=1, max_connections=10, **db_params)

# Define 3 queues each for Accounts, deposite and loans.
machine_queues = [deque() for _ in range(3)]

# if there is no other request in the table then returns 1 else returns the max token number + 1
token = initialise_token()

# Main loop
while True:
    os.system('cls') # for cearing hte screen
    print("\n\nWelcome to the Bank xyz.")
    valid_inputs_list = mainpage_display() # for displaying the mainpage with formating.

    choice = input("Enter the request you want to raise: ")  
    choice = user_input_validity(choice, valid_inputs_list)  # checks if the userinput is valid.

    if int(choice) == 2: # exit
        print("Exiting the Bank. Thank you!")
        break
    elif int(choice) == 1:  # login
        user_input_username = input("Enter your username: ")
        user_input_pass = maskpass.askpass(prompt="Enter your password: :", mask="*")
        role = login_verify(user_input_username,user_input_pass) # if user exists, get the role of the user
        input('press Enter to continue...')  # for providing breaks befor clearing the screen
        if role == 1: # admin department
            while True:
                os.system('cls')
                valid_user_choice_list = adminpage_display(user_input_username)
                user_input_choice = input('Enter the choice: ')
                user_input_choice = user_input_validity(user_input_choice, valid_user_choice_list)
                if user_input_choice =='4': # log out
                    print('Logging out')
                    break
                elif user_input_choice =='1':  # Manage Services
                    user_input_operation = input('Do you wanna 1. add or 2. remove values from the table: ') 
                    user_input_operation = user_input_validity(user_input_operation,[1,2])

                    if user_input_operation == '1':
                        user_input_name = input('Enter the name of the service you wish to add: ')
                        user_input_number = input('Select which Service type number you wanna update: ')
                        user_input_number = user_input_validity(user_input_number,[1,2,3])
                        admin_service_table_update(user_input_operation,user_input_name,user_input_number)
                        input('press Enter to continue...')  # for providing breaks befor clearing the screen
                        continue
                    user_input_name = input('Enter the name of the service you wish to update: ')
                    if check_db_service_name(user_input_name): # checks if the name exists in the database column
                        admin_service_table_update(user_input_operation,user_input_name)
                    else:
                        print("Service name does not exist in the database.")
                elif user_input_choice =='2': # Manage Service Types
                    user_input_operation = input('Do you wanna 1. add or 2. remove values from the table: ') 
                    user_input_operation = user_input_validity(user_input_operation,[1,2])
                    user_input_name = input('Enter the name of the service you wish to update: ')
                    if check_db_service_type(user_input_name):  # checks if the name exists in the database column
                        admin_service_table_update(user_input_operation,user_input_name)
                    else:
                        print("Service name does not exist in the database.")
                    admin_service_type_update(user_input_operation,user_input_name)
                elif user_input_choice =='3': # View Service Requests
                    user_input_type = input('Select which type do you want:\n1. Display all pending queues\n'
                                  '2. Show all requests raised today\n3. Select a request between two dates: ')
                    user_input_type = user_input_validity(user_input_type,[1,2,3])
                    if user_input_type == '3':
                        user_input_date1 = input('Select the starting date (YYYY-MM-DD): ')
                        user_input_date2 = input('Select the ending date (YYYY-MM-DD): ')
                        date1 = (user_input_date1,user_input_date2)
                        # Convert user input strings to date objects
                        try:
                            admin_request_view(user_input_type,date1)
                        except ValueError:
                            print("Invalid date format. Please enter dates in YYYY-MM-DD format.")
                            # Handle the error or exit gracefully
                        input('press Enter to continue...') # for providing breaks befor clearing the screen
                        continue
                    admin_request_view(user_input_type)
                input('press Enter to continue...') # for providing breaks befor clearing the screen
            input('press Enter to continue...') # for providing breaks befor clearing the screen
        elif role in [2,3,4]:   # employ department
            while True:
                os.system('cls') # clear screen
                valid_user_choice_list = managerpage_display(user_input_username,machine_queues[int(role)-2])
                user_input_choice = input('Enter the choice: ')
                user_input_choice = user_input_validity(user_input_choice, valid_user_choice_list)
                if user_input_choice == '1': # View Queue
                    check_queue_history(machine_queues[int(role)-2])
                elif user_input_choice == '2': # Accept Request
                    try:
                        processed_update(machine_queues[int(role)-2][0])
                        machine_queues[int(role)-2].popleft()
                    except IndexError:
                        print("Queue is empty.") 
                else: # Log out
                    print('Logging out')
                    break
                input('press Enter to continue...') # for providing breaks befor clearing the screen
            input('press Enter to continue...') # for providing breaks befor clearing the screen
    else:  # user department
        user_name = input("Enter your name: ")
        machine_queues[int(choice[0])-1].append((token,datetime.now(), user_name, choice))
        update_data_to_sql(machine_queues[int(choice[0])-1][-1])
        print(f"The Token for Request '{choice}'is: ",end='')

        # Display token after user input
        print(token)
        token += 1
        input('press Enter to continue...') # for providing breaks befor clearing the screen