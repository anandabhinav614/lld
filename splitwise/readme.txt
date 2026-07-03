so in splitwise service what we do:
    add user, .'. user_map req.
    create grp, .'. group_map req
    to settle everything, balance sheet is req
        sheet tracks who owes how much to whom across all users in the system. It's a two-level mapping:
            self.balance_sheet: dict[str, dict[str, float]]
            What it represents
            Outer key (dict[str, ...])	Inner key (dict[str, float])	Value
            Creditor user ID (the one who paid)	Debtor user ID (the one who owes)	Amount owed

    to store all expenses, expenses is req
        This keeps track of all expenses per group:
        self.expenses: dict[str, list[Expense]] = defaultdict(list)
        What it represents
        Key	              Value
        Group ID	List of all expenses created in that group


    its types:
        group_map->dict[groupid, Group obj]
        user_map->dict[user id, user obj]
        balance_sheet-> dict[userid, dict[str, float]]
        expenses -> dict[groupid, list[Expense]]


understanding settle algo:
    Step 1: Build Net Balance
        From\To	    user_a	user_b	user_c
        user_a	    0	    200	    200
        user_b	    -200	0	    100
        user_c	    -200	-100	0
        The algorithm first converts this to net balance per person:

        net_balance = defaultdict(float)

        for user, balances_with_other in self.balance_sheet.items():
            net_balance[user] = sum(balances_with_other.values())
        
        User	    Calculation	            Net Balance	    Meaning
        user_a	    0 + 200 + 200 =         400	+400	    Owed $400 total
        user_b	    -200 + 0 + 100 =        -100-100	    Owes $100 total
        user_c	    -200 + -100 + 0 =       -300-300	    Owes $300 total
        Check:  400 + (-100) + (-300) = 0 ✅ (money is conserved)

    Step 2: Separate into Debtors and Creditors
        debtors = []   # People who owe money (negative net balance)
        creditors = [] # People who are owed money (positive net balance)

        for user, balance in net_balance.items():
            if balance < -0.01:
                heapq.heappush(debtors, (balance, user))   # (-100, user_b), (-300, user_c)
            elif balance > 0.01:
                heapq.heappush(creditors, (-balance, user)) # (-400, user_a)

        debtors->	    [(-300, user_c), (-100, user_b)] ← biggest debtor first
        creditors->	    [(-400, user_a)] ← biggest creditor first

    Step 3: Greedy Settlement
        The idea: Match the biggest debtor with the biggest creditor and settle as much as possible.
        Iteration 1:
            Pop biggest debtor:  (-300, user_c)   → debt_val = 300
            Pop biggest creditor: (-400, user_a)  → cred_val = 400
            
            settle_amount = min(300, 400) = 300
            
            Print: "user_c must pay user_a 300.00"
            
            debt_val (300) - settle_amount (300) = 0  → user_c is fully settled ✅
            cred_val (400) - settle_amount (300) = 100 → user_a still owed 100
            
            Push user_a back: creditors = [(-100, user_a)]
        
        Iteration 2:
            Pop biggest debtor:  (-100, user_b)   → debt_val = 100
            Pop biggest creditor: (-100, user_a)  → cred_val = 100
            
            settle_amount = min(100, 100) = 100
            
            Print: "user_b must pay user_a 100.00"
            
            Both are fully settled 
            
        Code:    
        while debtors and creditors:
            debt_val, debtor_id = heapq.heappop(debtors)
            cred_val, creditor_id = heapq.heappop(creditors)
            debt_val, cred_val = abs(debt_val), abs(cred_val)
            settle_amount = min(cred_val,debt_val)

            debtor_name = self.user_map[debtor_id]._name
            creditor_name = self.user_map[creditor_id]._name
            print(f"{debtor_name} must pay {creditor_name} {settle_amount:.2f}")

            if debt_val > settle_amount: # If someone still owes or is owed money, push them back into the heap
                heapq.heappush(debtors, (-(debt_val - settle_amount), debtor_id))
            elif cred_val > settle_amount:
                heapq.heappush(creditors, (-(cred_val - settle_amount), creditor_id))