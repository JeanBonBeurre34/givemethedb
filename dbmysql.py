import socket
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("fake_mysql_service.log"),
                        logging.StreamHandler()
                    ])

class FakeMySQLService:
    def __init__(self, client_socket, address):
        self.client_socket = client_socket
        self.address = address
        self.databases = {
            'sys': ['table1', 'table2'],
            'test': ['table3', 'table4'],
            'information_schema': ['SCHEMATA', 'TABLES', 'COLUMNS'],
            'mysql': ['user', 'db', 'host'],
            'performance_schema': ['events_statements_summary_by_digest', 'file_summary_by_event_name']
        }
        self.tables_data = {
            'table1': [{'id': 1, 'name': 'John Doe'}, {'id': 2, 'name': 'Jane Doe'}],
            'table2': [{'product_id': 101, 'product_name': 'Gadget X'}, {'product_id': 102, 'product_name': 'Gadget Y'}],
            # Add predefined rows for other tables if needed
        }
        self.current_database = None
        logging.info(f"New connection from {address}")

    def use_database(self, db_name):
        if db_name in self.databases:
            self.current_database = db_name
            response = f"Database changed to {db_name}\n"
        else:
            response = f"Database '{db_name}' does not exist.\n"
        self.client_socket.sendall(response.encode())
        logging.info(response.strip())

    def show_tables(self):
        if self.current_database:
            tables = '\n'.join(self.databases[self.current_database]) + '\n'
            self.client_socket.sendall(tables.encode())
        else:
            self.client_socket.sendall("No database selected.\n".encode())
        logging.info("Showed tables.")

    def show_databases(self):
        databases = '\n'.join(self.databases.keys()) + '\n'
        self.client_socket.sendall(databases.encode())
        logging.info("Showed databases.")

    def execute_select(self, command):
        command_parts = command.lower().split()
        if "from" in command_parts:
            from_index = command_parts.index("from")
            if len(command_parts) > from_index + 1:
                table_name = command_parts[from_index + 1].rstrip(';')
                if table_name in self.tables_data:
                    rows = self.tables_data[table_name]
                    response = "\n".join([str(row) for row in rows]) + '\n'
                    return response
                else:
                    return f"Table '{table_name}' does not exist or has no data.\n"
            else:
                return "Invalid SELECT command format.\n"
        return "Invalid SELECT command format.\n"

    def connect(self):
        welcome_message = "Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.\n" \
                          "Type 'help;' or '\\h' for help. Type '\\c' to clear the current input statement.\n"
        self.client_socket.sendall(welcome_message.encode())
        logging.info("Sent welcome message to client.")

    def handle_client(self):
        self.connect()
        while True:
            try:
                self.client_socket.sendall("mysql> ".encode())
                command = self.client_socket.recv(1024).decode().strip()
                logging.info(f"Received command: {command} from {self.address}")
                if command.lower() == 'exit':
                    self.client_socket.sendall("Exiting MySQL service.\n".encode())
                    break
                elif command.startswith('use ') and command.endswith(';'):
                    db_name = command[4:-1]
                    self.use_database(db_name)
                elif command.lower().startswith('select ') and command.lower().endswith(';'):
                    response = self.execute_select(command)
                    self.client_socket.sendall(response.encode())
                elif command == 'show tables;':
                    self.show_tables()
                elif command == 'show databases;':
                    self.show_databases()
                else:
                    self.client_socket.sendall("Command not recognized.\n".encode())
            except Exception as e:
                logging.error(f"Error handling client {self.address}: {e}")
                break
        self.client_socket.close()
        logging.info(f"Connection closed for {self.address}")

def client_thread(client_socket, address):
    service = FakeMySQLService(client_socket, address)
    service.handle_client()

def main():
    host = '0.0.0.0'
    port = 3306
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()

    logging.info(f"Fake MySQL Service is listening on port {port}")

    try:
        while True:
            client_socket, address = server_socket.accept()
            logging.info(f"Accepted connection from {address}")
            thread = threading.Thread(target=client_thread, args=(client_socket, address))
            thread.start()
    except KeyboardInterrupt:
        logging.info("Server shutdown requested by user. Shutting down...")
    finally:
        server_socket.close()
        logging.info("Server has been successfully shut down.")

if __name__ == '__main__':
    main()
