"""
    Filename:          textView.py
    Purpose:           The user interface to display the chat logs
"""
import sys
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Log
from queue import Queue
from lib import gen_word_packet



class InputApp(App):

    CSS = """                                                                                    
    Input.-valid {                                                                               
        border: tall $success 60%;                                                               
    }                                                                                            
    Input.-valid:focus {                                                                         
        border: tall $success;                                                                   
    }                                                                                            
    Input {                                                                                      
        margin: 1 1;                                                                             
    }                                                                                            
    Label {                                                                                      
        margin: 1 2;                                                                             
    }                                                                                            
    Pretty {                                                                                     
        margin: 1 2;                                                                             
    }                                                                                            
    Log{                                                                                         
                                                                                                 
     padding: 1 2 0 2;                                                                           
    }                                                                                            
                                                                                                 
                                                                                                 
    """

    """
        Function Name:  __init__
        Description:    Initializes an instance of the InputApp class.
        Parameters:     sock - The socket object.
        Returns:        None
    """

    def __init__(self, sock):
        super().__init__()
        self.messages = Queue()
        self.socket = sock

    """
        Function Name:  display_messages
        Description:    Displays messages in the application log.
        Parameters:     new_message - Boolean indicating whether it's a new message.
                        a_message - The message to be displayed.
        Returns:        None
    """

    def display_messages(self, new_message=False, a_message="") -> None:
        try:
            log = self.query_one(Log)
            if new_message:
                log.write_line(a_message)
            else:
                while not self.messages.empty:
                    log.write_line(self.messages.get_nowait())
        except Exception as e:
            print(f"An error occurred: {e}")

    """
        Function Name:  append_message
        Description:    Appends a message to the messages list and displays it.
        Parameters:     a_message - The message to be appended and displayed.
        Returns:        None
    """

    def append_message(self, a_message) -> None:
        name, message = a_message
        self.messages.put_nowait((name, message))
        self.display_messages(True, f"{name}: {message}")

    """
        Function Name:  push_message
        Description:    Sends a message over the socket.
        Parameters:     message - The message to be sent.
        Returns:        None
    """

    def push_message(self, message) -> None:
        if message:
            data = {'message': message}
            word = gen_word_packet(data)  # Use the imported function
            self.socket.sendall(word)
            self.display_messages(True, "You: "+message)

    """
        Function Name:  open_log
        Description:    Opens the log file for writing.
        Parameters:     None
        Returns:        None
    """
    def open_log():
        try:
            with open("logs.txt", "w") as file:
                sys.stdout = file
        except Exception as e:
            print(f"An error occurred: {e}")

    """
        Function Name:  compose
        Description:    Composes the user interface elements.
        Parameters:     None
        Returns:        ComposeResult
    """

    def compose(self) -> ComposeResult:
        yield Label("CHAT APP")
        yield Log()
        yield Label("Enter Message")
        yield Input(placeholder="HELLO FROM CHAT APP",
                    type="text",
                    )

    """
        Function Name:  show_invalid_reasons
        Description:    Handles the submission event, updating UI for validation failures.
        Parameters:     event - The Input.Submitted event.
        Returns:        None
    """
    @on(Input.Submitted)
    def submit(self, event: Input.Submitted) -> None:
        log = self.query_one(Log)
        self.push_message(event.value)
        input_widget = self.query_one(Input)
        input_widget.value = ""


if __name__ == "__main__":
    try:
        app = InputApp()
        app.run()
    except Exception as e:
        print(f"An error occurred: {e}")
