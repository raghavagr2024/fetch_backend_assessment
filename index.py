from flask import Flask, request, jsonify
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)


# Dictionary to store balances based on transaction date for ease of computations
balances = {}


# Default route to check if the server is running
@app.route('/')
def index():
    return 'Hello, World!'

# Route to add transactions
@app.route('/add', methods=['POST'])
def add():
    try:
        # Retrieve JSON data from the request
        data = request.get_json()

        # Extract payer and timestamp from the JSON data
        payer = data['payer']
        timestamp = data['timestamp']

        # Define the expected date format
        date_format = "%Y-%m-%dT%H:%M:%S"

        # Convert the timestamp to a datetime object
        timestamp = datetime.strptime(timestamp[:-1], date_format)

        # Add the transaction to the balances dictionary
        balances[timestamp] = {"points": data['points'], "payer": payer}

        # Return a 200 OK status on successful addition
        return "", 200
    except Exception as e:
        return jsonify({"msg": str(e)})
    
@app.route('/spend', methods=['POST'])
def spend():
    try:
        # Retrieve JSON data from the request
        data = request.get_json()
        points = data['points'] #Points to spend

        totalAmount = 0
        
        # Calculate total points available across all transactions
        for value in balances.values():
            totalAmount += value['points']

        # Check if sufficient funds
        if totalAmount < points:
            return jsonify({"msg": "Insufficient funds"}), 400
        else:
            # Sort transactions by timestamp (earliest first)
            sortedKeys = sorted(balances.keys())
            transactions = {}


            # Process each transaction in order of oldest to newest
            for key in sortedKeys:
                # If the current transaction has more points than needed, subtract points
                if balances[key]['points'] > points:
                    balances[key]['points'] -= points
                    if (balances[key]['payer'] in transactions):
                        transactions[balances[key]['payer']] -= points
                    else:
                        transactions[balances[key]['payer']] = -points
                    points = 0
                    break
                # If the current transaction has fewer or equal points, deduct them fully
                else:
                    points -= balances[key]['points']
                    if (balances[key]['payer'] in transactions):
                        transactions[balances[key]['payer']] -= balances[key]['points']
                    else:
                        transactions[balances[key]['payer']] = -balances[key]['points']
                    balances[key]['points'] = 0
            # Prepare the return statement to show points spent per payer
            returnStatement = []
            for key in transactions:
                returnStatement.append({"payer": key, "points": transactions[key]})
            
            # Return the transaction details as JSON with a 200 OK status
            return jsonify(returnStatement), 200
    except Exception as e:
        
        return jsonify({"msg": str(e)})


# Route to retrieve the current balance for a user
@app.route('/balance', methods=['GET'])
def balance():
    try:
        # Prepare a dictionary to hold the balance of each payer
        returnStatement = {}

        # Get the remaining points for each payer 
        for value in balances.values():

            # Add the points to the payer if they have transactions across multiple dates
            if value['payer'] in returnStatement:
                returnStatement[value['payer']] += value['points']
            # Add the points to the payer if they only have transactions in a single date
            else:
                returnStatement[value['payer']] = value['points']

        # Return the payer balances as JSON with a 200 OK status
        return returnStatement, 200
    except Exception as e:
        
        return jsonify({"msg": str(e)})

# Run the Flask app on port 8000
if __name__ == '__main__':
    app.run(port=8000)