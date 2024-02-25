import socket
import threading

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
        self.current_database = None

    def use_database(self, db_name):
        if db_name in self.databases:
            self.current_database = db_name
            return f"Database changed to {db_name}"
        else:
            return f"Database '{db_name}' does not exist."

    def show_tables(self):
        if self.current_database:
            tables = '\n'.join(self.databases[self.current_database])
            return tables
        else:
            return "No database selected."

    def show_databases(self):
        return '\n'.join(self.databases.keys())

    def connect(self):
        welcome_message = "Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.\n" \
                          "Type 'help;' or '\\h' for help. Type '\\c' to clear the current input statement.\n"
        self.client_socket.sendall(welcome_message.encode())

    def handle_client(self):
        self.connect()
        while True:
            try:
                # Send the mysql prompt to the client.
                self.client_socket.sendall("mysql> ".encode())

                command = self.client_socket.recv(1024).decode().strip()
                if command == 'exit':
                    self.client_socket.sendall("Exiting MySQL service.\n".encode())
                    break
                elif command.startswith('use ') and command.endswith(';'):
                    db_name = command[:-1].split()[-1]
                    response = self.use_database(db_name)
                elif command == 'show tables;':
                    response = self.show_tables()
                elif command == 'show databases;':
                    response = self.show_databases()
                else:
                    response = "Command not recognized."
                self.client_socket.sendall((response + "\n").encode())
            except Exception as e:
                print(f"Error: {e}")
                break
        self.client_socket.close()

def client_thread(client_socket, address):
    service = FakeMySQLService(client_socket, address)
    service.handle_client()

def main():
    host = '0.0.0.0'  # Listen on all network interfaces
    port = 3306
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Fake MySQL Service is listening on port {port}")

    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address} has been established.")
            threading.Thread(target=client_thread, args=(client_socket, address)).start()
    except KeyboardInterrupt:
        print("\nShutting down the server.")
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()
