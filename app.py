from flask import Flask, render_template, request, redirect, session
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'secret_key'

users = {
    'Amal': {'max_loan_amount': 10000, 'current_loan_amount': 1000, 'pending_loans': {}},
    'Nimal': {'max_loan_amount': 10000, 'current_loan_amount': 500, 'pending_loans': {}},
    'Kamal': {'max_loan_amount': 10000, 'current_loan_amount': 2000, 'pending_loans': {}},
}

votes = defaultdict(list)

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        if name in users:
            session['name'] = name
            return redirect('/dashboard')
        else:
            return 'Invalid username'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    username = session['name']
    user = users[username]
    max_loan_amount = user['max_loan_amount']
    current_loan_amount = user['current_loan_amount']
    pending_loans = user['pending_loans']
    return render_template('dashboard.html', username=username, max_loan_amount=max_loan_amount, 
                           current_loan_amount=current_loan_amount, pending_loans=pending_loans)

@app.route('/request_loan', methods=['POST'])
def request_loan():
    username = session['name']
    user = users[username]
    max_loan_amount = user['max_loan_amount']
    current_loan_amount = user['current_loan_amount']
    loan_amount = request.form.get('loan_amount')
    if loan_amount is None:
        return 'Invalid loan amount'
    loan_amount = int(loan_amount)
    if loan_amount <= 0:
        return 'Invalid loan amount'
    if loan_amount > max_loan_amount - current_loan_amount:
        return 'Loan amount exceeds maximum loan amount'
    user['pending_loans'][len(user['pending_loans'])+1] = loan_amount
    return redirect('/dashboard')


@app.route('/approve_loan/<int:loan_id>', methods=['GET', 'POST'])
def approve_loan(loan_id):
    username = session['name']
    user = users[username]
    max_loan_amount = user['max_loan_amount']
    current_loan_amount = user['current_loan_amount']
    if loan_id in user['pending_loans']:
        if request.method == 'POST':
            vote = request.form['vote']
            if vote not in ['approve', 'reject']:
                return 'Invalid vote'
            votes[loan_id].append(vote)
            if len(votes[loan_id]) == 3:
                num_approvals = sum([1 for v in votes[loan_id] if v == 'approve'])
                if num_approvals >= 2:
                    loan_amount = user['pending_loans'][loan_id]
                    user['current_loan_amount'] += loan_amount
                    del user['pending_loans'][loan_id]
                    return redirect('/dashboard')
                else:
                    del user['pending_loans'][loan_id]
                    return redirect('/dashboard')
        elif loan_id not in votes or username not in votes[loan_id]:
            return render_template('approve_loan.html', loan_id=loan_id)
        else:
            return f'You have already voted on loan request {loan_id}'
    else:
        return f'Loan request {loan_id} does not exist or has already been approved/rejected'

if __name__ == '__main__':
    app.run(debug=True)
