from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import random
import io
import base64

app = Flask(__name__)

# Load the data
def load_data():
    try:
        return pd.read_csv("sweets.csv")
    except:
        return pd.DataFrame(columns=["Name", "Cost", "Quantity", "Ingredient"])

# Save the data
def save_data(df):
    df.to_csv("sweets.csv", index=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/sweets', methods=['GET'])
def get_sweets():
    df = load_data()
    return jsonify(df.to_dict('records'))

@app.route('/api/sweets/add', methods=['POST'])
def add_sweet():
    data = request.json
    df = load_data()
    
    new_sweet = {
        'Name': data['name'],
        'Cost': int(data['cost']),
        'Quantity': float(data['quantity']),
        'Ingredient': data['ingredient']
    }
    
    df = df.append(new_sweet, ignore_index=True)
    save_data(df)
    return jsonify({'message': 'Sweet added successfully'})

@app.route('/api/sweets/search/<int:code>', methods=['GET'])
def search_sweet(code):
    df = load_data()
    if code in df.index:
        return jsonify(df.loc[code].to_dict())
    return jsonify({'error': 'Sweet not found'}), 404

@app.route('/api/sweets/update/<int:code>', methods=['PUT'])
def update_sweet(code):
    df = load_data()
    data = request.json
    
    if code in df.index:
        df.loc[code] = [
            data['name'],
            int(data['cost']),
            float(data['quantity']),
            data['ingredient']
        ]
        save_data(df)
        return jsonify({'message': 'Sweet updated successfully'})
    return jsonify({'error': 'Sweet not found'}), 404

@app.route('/api/sweets/delete/<int:code>', methods=['DELETE'])
def delete_sweet(code):
    df = load_data()
    if code in df.index:
        df.drop(code, inplace=True)
        save_data(df)
        return jsonify({'message': 'Sweet deleted successfully'})
    return jsonify({'error': 'Sweet not found'}), 404

@app.route('/api/bills/create', methods=['POST'])
def create_bill():
    data = request.json
    df = load_data()
    
    if data['sweet_code'] in df.index:
        sweet = df.loc[data['sweet_code']]
        amount = int(data['quantity']) * sweet['Cost']
        
        bf = pd.read_csv("customer.csv", index_col="billid")
        bf.loc[random.randint(1000,9999)] = [
            data['customer_name'],
            data['date'],
            amount,
            sweet['Name']
        ]
        bf.to_csv("customer.csv")
        
        return jsonify({
            'amount': amount,
            'message': 'Bill created successfully'
        })
    return jsonify({'error': 'Sweet not found'}), 404

@app.route('/api/charts/sweets')
def get_sweets_chart():
    df = load_data()
    plt.figure(figsize=(10,6))
    plt.bar(df["Name"], df["Cost"], color="navy")
    plt.title("Rate List of Sweets")
    
    # Save plot to a temporary buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image = base64.b64encode(buf.getvalue()).decode()
    buf.close()
    
    return jsonify({'chart': f'data:image/png;base64,{image}'})

if __name__ == '__main__':
    app.run(debug=True)
