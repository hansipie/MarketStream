## MarketStream
This project is a Python application that uses websockets, multithreading and queues to fetch and process real-time market data.

## Description
The `app.py` file contains the main code of the application. It starts by creating a queue and a StreamMarket object that uses this queue to communicate market data. A daemon thread is launched to run the getMarket method of the StreamMarket object in the background.

Next, the application enters a main loop where it checks if the thread is still alive and if the queue is not empty. If so, it retrieves the data from the queue, adds it to a pandas DataFrame, and displays the DataFrame.

If a keyboard interrupt is detected (for example, if the user presses Ctrl+C), the application terminates gracefully.

## Installation
To install this project, you need to have Python installed on your machine. You can then clone this repository and install the necessary dependencies with pip:

```bash	
git clone <repository url>
cd <repository name>
pip install -r requirements.txt
```

## Usage
To run the application, navigate to the project directory in your terminal and run the app.py file with Python:

```bash	
python app.py
```

## Contribution
Contributions to this project are welcome. If you wish to contribute, please fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under MIT license. For more information, please see the LICENSE file in the main project directory.
