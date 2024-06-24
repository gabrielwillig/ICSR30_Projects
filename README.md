# Repository for the Computer Networks course projects  
## Project 1: File transfer using UDP  
To run: First, start the server and then the client, e.g., `python server.py`, `python client.py`  
To perform a GET request, the machine running the server must have a folder named "assets" containing text or image files.  
The file will be transferred to the client using the following command:  
`GET filename.extension`.  
If you want to corrupt the file, just add the word `CORRUPT` as the third argument.   
To exit, type `!q`.  
## Project 2: File transfer using TCP, with server chat
To setup: First, setup the environment, create a folder called assets on the server machine and insert files, on the client machine create a duplicate paste,
then setup the SERVER_IP and PORT.
To run: First, start the server and then the client, e.g., `python server.py`, `python client.py` 
To perform a GET request use the following command example:  
`GET filename.extension`.  
To exit the client, type `!q`. 
When a client is receiving a file, he cannot listen to server messages.