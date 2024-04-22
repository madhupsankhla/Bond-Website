from flask import Flask, redirect, url_for, request, Response, render_template ,jsonify
from flask_mysqldb import MySQL


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'madhup@1207'
app.config['MYSQL_DB'] = 'DCCDATA'

mysql = MySQL(app)  


# Q1
@app.route('/')
def index():

    cursor = mysql.connection.cursor()
    query1 = "SELECT DISTINCT `Name of the Purchaser` FROM Purchase_Details"
    cursor.execute(query1)
    companies = cursor.fetchall()

    query2= "SELECT DISTINCT `Name of the Political Party` FROM Redemption_Details"
    cursor.execute(query2)
    party = cursor.fetchall()
    cursor.close()

    return render_template('index.html', party=party, companies=companies)


@app.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == 'POST':
        search_query = request.form['search_query']
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM Purchase_Details WHERE `Bond Number` = %s"
        cursor.execute(query, (search_query,))
        
        data = cursor.fetchall()
        cursor.close()
        return render_template('Q1Ans.html', data=data)
    return render_template('Q1Ans.html')



# Q2
@app.route('/company_bonds', methods=['POST'])
def company_bonds():
    company_name = request.form.get('company_name')
    cursor = mysql.connection.cursor()
    query = "SELECT `Journal Date`,`Denominations` FROM purchase_details WHERE `Name of the Purchaser` = %s"
    cursor.execute(query, (str(company_name),))
    data = cursor.fetchall()
    
    cursor.close()   
    data2 = {"2019": 0 ,"2020":0,"2021":0,"2022":0,"2023":0,"2024":0}
    years = ["2019","2020","2021","2022","2023","2024"]  
    for row in data:
        
        if "2019" in row[0]:
            data2["2019"] += row[1]
        elif "2020" in row[0]:
            data2["2020"] += row[1]
        elif "2021" in row[0]:
            data2["2021"] += row[1]
        elif "2022" in row[0]:
            data2["2022"] += row[1]
        elif "2023" in row[0]:
            data2["2023"] += row[1]
        elif "2024" in row[0]:
            data2["2024"] += row[1]

    
    data2=list(data2.values())
    return render_template('Q2Ans.html', companies=company_name, data2=data2,years=years)



# Q3
@app.route('/party_bonds', methods=['POST'])
def party_bonds():
    party_name = request.form.get('party_name')
    cursor = mysql.connection.cursor()
    query = "SELECT `Date of Encashment`,`Denominations` FROM redemption_details WHERE `Name of the Political Party` = %s"
    cursor.execute(query, (str(party_name),))
    data = cursor.fetchall()
    
    cursor.close()  
    years = ['2019', '2020', '2021', '2022', '2023', '2024']
    yearly_sum = {year: 0 for year in years}
    yearly_count = {year: 0 for year in years}

    for date_str, amount_str in data:
        year = date_str.split('/')[-1]
        amount = int(amount_str.replace(',', ''))
        yearly_sum[year] += amount
        yearly_count[year] += 1

    yearly_sum_values = [yearly_sum[year] for year in years]
    yearly_count_values = [yearly_count[year] for year in years]

    return render_template('Q3Ans.html', yearly_sum=yearly_sum_values, yearly_count=yearly_count_values, years=years)


#Q4
@app.route('/get_donation_data', methods=['POST'])
def get_donation_data():
    
    political_party_name = request.form.get("party_name")

    
    cursor = mysql.connection.cursor()
    query = """
        SELECT 
            pd.`Name of the Purchaser`,
            pd.`Denominations`,
            pd.`Bond Number`
        FROM 
            Purchase_Details pd
        JOIN 
            Redemption_Details rd ON pd.`Prefix` = rd.`Prefix` AND pd.`Bond Number` = rd.`Bond Number`
        WHERE 
            rd.`Name of the Political Party` = %s
    """
    cursor.execute(query, (political_party_name,))
    data = cursor.fetchall()
    cursor.close()
    
    response_data = []
    total_sum = 0
    for row in data:
        purchaser_name, denominations, bond_number = row
        total_sum += denominations
        response_data.append({
            'Name of the Purchaser': purchaser_name,
            'Denominations': denominations,
            'Bond Number': bond_number
        })

    return render_template('Q4Ans.html', donation_data=response_data, total_sum=total_sum)

    
    
#Q5
@app.route('/get_party_data', methods=['POST'])
def get_party_data():
    if request.method == 'POST':        
        company_name = request.form['company_name']       
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT 
                r.`Name of the Political Party`, 
                r.`Denominations`, 
                r.`Bond Number`
            FROM 
                Purchase_Details p
            JOIN 
                Redemption_Details r ON p.`Prefix` = r.`Prefix` AND p.`Bond Number` = r.`Bond Number`
            WHERE 
                p.`Name of the Purchaser` = %s
        """, (company_name,))
        
        
        party_data = cursor.fetchall()       
        cursor.close() 
        total_sum = sum(int(row[1].replace(',', '')) for row in party_data)
        return render_template('Q5Ans.html', party_data=party_data, total_sum=total_sum)



#Q6
@app.route('/get_pie', methods = ["POST", "GET"])
def get_pie():
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        cursor.execute("select `Name of the Political Party`, Denominations from redemption_details")
        data = cursor.fetchall()
        result = {}
        for key, value in data:
            if key in result:
                result[key] += round(int(value.replace(',', ''))/100000, 2)
            else:
                result[key] = round(int(value.replace(',', ''))/100000, 2)
        cursor.close()
        return render_template("Q6Ans.html", x_axis = list(result.keys()), y_axis = list(result.values()))
    
if __name__ == '__main__':
   app.run(host="0.0.0.0", port="80", debug=True)