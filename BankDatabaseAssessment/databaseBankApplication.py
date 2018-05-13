# function for data entry and all related details
def dataEntry():
    # Informs the user of there selection
    print("You have selected '1', Account Details")
    # loops the function until told to stop, if the user inputs invalid information during the selection they will be informed of what went wrong and asked to inpur the correct data again
    dataLoop = True
    while dataLoop:
        # Prints blank line, purely aesthetic
        print("  ")

        # prints instructions to the user in a clear multi-line format
        print("If you would like to create a new account, please press '1'")
        print("If you would like to make a deposit, please press '2'")
        print("If you would like to make a withdrawal, please press '3'")
        print("If you would like to cancel transaction, please press '4'")

        # takes input for the user relating to the prervious instructions
        dataChoice = input("")

        # group of if statements determining which action the user requested to be performed
        if dataChoice == "1":
            # If an action is successfully chosen the input check loop will cancel
            dataLoop = False
            # name of the selected function
            newAccount()

        elif dataChoice == "2":
            dataLoop = False
            deposit()

        elif dataChoice == "3":
            dataLoop = False
            withdraw()
        #option for the user to cancel out without completing the program
        elif dataChoice == "4":
            dataLoop = False
            #Informs user of their choice and return the user to the main menu
            print("Selection cancelled")
        else:
            #informs the user their input was not accepted and return to the begining of the loop to allow the user to reenter the data
            print("Selection invalid, please try again")

#function for creating a new account
def newAccount():
    #informs the user of their choice and which menu they have accessed
    print("You have selected '1', create new account")
    #collects information from the user that will be used to open the account
    holderName = input("Please enter name of the account holder")
    holderAddress = input("Please enter the account holders address")

    #sets up a loop rejecting invalid account types
    typeLoop = True
    while typeLoop:
        accountType = input("Please enter type of account requires. s - savings, c - current")
        accountType = accountType.lower()
        if accountType != "s" and accountType != "c":
            print("account type invalid")
        else:
            typeLoop = False
    #set up the loop rejecting invalid gender types
    genderLoop = True
    while genderLoop:
        holderGender = input("Please enter gender of account holder. m - male, f - female")
        holderGender = holderGender.lower()
        if holderGender != "m" and holderGender != "f":
            print("Please select 'm' or 'f' for gender")
        else:
            genderLoop = False

    #Once all check are complete and data is deemed acceptable the sql database is accessed
    qaBank = sql.connect("localhost", "root", "", "qabank")
    #cursor set up to interact with the table
    curs = qaBank.cursor()
    #slightly different queries depending on account types
    if accountType == "s":
        curs.execute("select AccountNo from accounts where AccountNo like 's%' order by (right(rtrim(AccountNo),3)) desc")
    else:
        curs.execute("select AccountNo from accounts where AccountNo like 'c%' order by (right(rtrim(AccountNo),3)) desc")
    # getting the numerical part of the account number
    existingNum = curs.fetchone()
    for R in existingNum:
        if curs.rowcount > 0:
            AccountNum = (R[3:5])
            intAccountNum = int(AccountNum)
            #assigning new account number as one above previous
            newNumber = (intAccountNum + 1)
        else:
            #setting first account number if none are available
            newNumber = 1
    #Completes the new account number string by combining account type digit, gender digit and sequential increased numerical marker
    newAccountNumber = accountType+holderGender+str(f'{newNumber:03}')

    #inserts the new account into0 the table as a new record
    curs.execute("insert into accounts values(%s,%s,%s)",(newAccountNumber, holderName, holderAddress))
    qaBank.commit()
    qaBank.close()
    #confirms the account was added, commits the changes and closes the database
    print("Account added successfully")



#function called to deposit
def deposit():
    #informs the user of there selection and which menu they are currently in
    print("You have selected '2', Make Deposit")

    #Accesses the database and sets up cursors for each table being used
    qaBank = sql.connect("localhost", "root", "", "qabank")
    curs = qaBank.cursor()
    cursDep = qaBank.cursor()
    cursWith = qaBank.cursor()

    #sets up a loop to return to if user input is considered invalid
    depLoop = True
    while depLoop:
        #gets the number of the account you wish to deposit into, must be exact
        accountNumber = input("Please input the account number you wish to deposit into")
        #fetches all account numbers for comparison
        curs.execute("select AccountNo from accounts")
        allNumbers = curs.fetchall()

        #compares input number will existing numbers looking for match
        for R in allNumbers:
            if accountNumber == R[0]:
                #if account number matches an existing number then it is accepted and the loop is exited as all data is acceptable
                print("Account number accepted")
                depLoop = False
        #if the account was not accepted and the loop is still active inform the user and return them to the beginning of the loop to input correct data
        if depLoop:
            print("Account number incorrect or invalid, please try again")
        else:
            #if data was accepted gets the account information from the accounts table
            curs.execute("select * from accounts where AccountNo = %s",accountNumber)
            thisAccount = curs.fetchall()
            sumTotalDep = 0
            sumTotalWith = 0
            for R in thisAccount:
                #for this account get both past deposits and withraws and compare the total difference to get current balance on the account.
                #seporate cursors are used for each table to keep things clean
                cursDep.execute("select amount from deposits where AccountNo = %s",accountNumber)
                depFullValues = cursDep.fetchall()
                if cursDep.rowcount>0:
                    for S in depFullValues:
                        #calculates deposit total
                        sumTotalDep = sumTotalDep + S[0]
                else:
                    #if no values set to 0
                    sumTotalDep=0

                cursWith.execute("select amount from withdraws where AccountNo = %s",accountNumber)
                withFullValues = cursWith.fetchall()
                if cursWith.rowcount>0:
                    for T in withFullValues:
                        #calculates withdraw total
                        sumTotalWith = sumTotalWith + T[0]
                else:
                    #if no values set to 0
                    sumTotalWith=0
                #calculate total balance
                balance = sumTotalDep - sumTotalWith

                #print account details
                print(R[0], ' - ', R[1], ' - ', R[2], ' - ', balance)


            #get amount to deposit
            depositAmount = int(input("How much would you like to deposit? (integer)"))
            #get the deposit date
            date = input("Please input current date")
            #creates a record of the deposit in the deposits table
            curs.execute("insert into deposits values(%s,%s,%s)",(accountNumber, depositAmount, date))
            #closes the database
            qaBank.commit()
            qaBank.close()

#function for withdrawing
def withdraw():
    #informs the user of their choice and what menu they have accessed
    print("You have selected '3', Make Withdraw")

    #gains access to the database and creates cursors for each table
    qaBank = sql.connect("localhost", "root", "", "qabank")
    curs = qaBank.cursor()
    cursDep = qaBank.cursor()
    cursWith = qaBank.cursor()

    #sets up data checking loops
    withLoop = True
    while withLoop:
        #gets the account the user wishes to withdraw from
        accountNumber = input("Please input the account number of the account you wish withdraw from")

        #gets all account numbers to compare the user input number
        curs.execute("select AccountNo from accounts")
        allNumbers = curs.fetchall()

        #checks if account number is a match
        for R in allNumbers:
            if accountNumber == R[0]:
                print("Account number accepted")
                #canceles loop if data is accepted
                withLoop = False
        #If loop still active inform the user their input was invalid and return to top of the loop to try again
        if withLoop:
            print("Account number incorrect or invalid, please try again")
        else:
            # if account found and accepted begins to calculate current balance in the account from prievious transactions
            curs.execute("select * from accounts where AccountNo = %s", accountNumber)
            thisAccount = curs.fetchall()
            sumTotalDep = 0
            sumTotalWith = 0
            #gets all previous deposits to this account from the deposits table
            for R in thisAccount:
                cursDep.execute("select amount from deposits where AccountNo = %s", accountNumber)
                depFullValues = cursDep.fetchall()
                if cursDep.rowcount > 0:
                    for S in depFullValues:
                        #calculates sum of all previous deposits
                        sumTotalDep = sumTotalDep + S[0]
                else:
                    #if no deposits set total to 0
                    sumTotalDep = 0

                #same as deposits above but with the withdraws table to calculate toial withdrawn
                cursWith.execute("select amount from withdraws where AccountNo = %s", accountNumber)
                withFullValues = cursWith.fetchall()
                if cursWith.rowcount > 0:
                    for T in withFullValues:
                        sumTotalWith = sumTotalWith + T[0]
                else:
                    sumTotalWith = 0
                #calculates current balance from total deposits and total withdrawn
                balance = sumTotalDep - sumTotalWith

                #displays the account information and current balance
                print(R[0], ' - ', R[1], ' - ', R[2], ' - ', balance)

            #loop to check withdraw amount is valid
            checkValidWithdrawLoop = True
            while checkValidWithdrawLoop:
                withdrawAmount = int(input("How much would you like to withdraw? (integer)"))
                #checks withdraw amount cannot be larger than current balance
                if withdrawAmount >= balance:
                    #return to check loop if withdraw amount invalid
                    print("Amount unavailable, account balance too low")
                else:
                    #cancels out of loop if amount accepted
                    print("Withdraw Amount Accepted")
                    checkValidWithdrawLoop = False

            #user input for date
            date = input("Please input current date")

            #inputs the record of the withdrawal
            curs.execute("insert into withdraws values(%s,%s,%s)", (accountNumber, withdrawAmount, date))

            #closes the database
            qaBank.commit()
            qaBank.close()

#menu for selecting what kinds of reports to display
def reportsOptions():

    #data check loop initialisation
    printReportsLoop = True
    print("You have selected '2', display reports")
    #data check loop
    while printReportsLoop:
        #presents user with options for data input and then waits for user to make a selection
        print("Please select types of accounts to view")
        print("'1' - View all Accounts")
        print("'2' - View all Current Accounts")
        print("'3' - View all Savings Accounts")
        print("'4' - View accounts belonging to Male clients")
        print("'5' - View accounts belonging to Female clients")
        print("'6' - Done viewing account reports")

        reportChoice = input("")
        #checks user selection for matches to options, if no match found return to top of loop
        # and allow user to re enter selection
        if reportChoice == "1":
            allAccounts()
        elif reportChoice == "2":
            allCurrentAccounts()
        elif reportChoice == "3":
            allSavingsAccounts()
        elif reportChoice == "4":
            allMaleAccounts()
        elif reportChoice == "5":
            allFemaleAccounts()
        elif reportChoice == "6":
            print("Done searching reports")
            printReportsLoop = False
        else:
            print("Input invalid, please try again")
###THE FOLLOWING FUNCTIONS ALL SHARE THE SAME STRUCTURE SO COMMENTS ARE ALSO SHARED, SEE THIS ONE FOR DETAILS###
#function to display reports of a specific type chosen by the user
def allAccounts():

    #displayes information telling the user what type of accounts they selected to see
    print("All Accounts")

    #access the database and set up appropriate cursor
    qaBank = sql.connect("localhost", "root", "", "qabank")
    curs = qaBank.cursor()

    #selects chosen reports from the database, sql query changes slightly with restrictions
    #depending on the users selection
    curs.execute("select * from accounts")
    accounts = curs.fetchall()
    #displayes all selected accounts details in turn
    for R in accounts:
        print(R[0], " - ", R[1], " - ",R[2])

def allCurrentAccounts():
    print("All Current Accounts")

    qaBank = sql.connect("localhost", "root", "", "qabank")
    curs = qaBank.cursor()

    curs.execute("select * from accounts where AccountNo like 'c%'")
    accounts = curs.fetchall()

    for R in accounts:
        print(R[0], " - ", R[1], " - ", R[2])
def allSavingsAccounts():
    print("All Savings Accounts")

    qaBank = sql.connect("localhost", "root", "", "qabank")
    curs = qaBank.cursor()

    curs.execute("select * from accounts where AccountNo like 's%'")
    accounts = curs.fetchall()

    for R in accounts:
        print(R[0], " - ", R[1], " - ", R[2])

def allMaleAccounts():
    print("All Accounts owned by Males")

    qaBank = sql.connect("localhost", "root", "", "qabank")
    curs = qaBank.cursor()

    curs.execute("select * from accounts where AccountNo like 'sm%' or AccountNo like 'cm%'")
    accounts = curs.fetchall()

    for R in accounts:
        print(R[0], " - ", R[1], " - ", R[2])
def allFemaleAccounts():
    print("All Accounts owned by Females")

    qaBank = sql.connect("localhost", "root", "", "qabank")
    curs = qaBank.cursor()

    curs.execute("select * from accounts where AccountNo like 'sf%' or AccountNo like 'cf%'")
    accounts = curs.fetchall()

    for R in accounts:
        print(R[0], " - ", R[1], " - ", R[2])


#inport the "mysql" package for python
import pymysql as sql

#general greeting to the user from the application
print("Hello, welcome to QA bank.")

#sets up menu loop so invalid inputs can be cyled out and user can re enter them without exiting program
menuLoop = True
while menuLoop:

    #prints opetions for the user in turn
    print("If you would like to open a new account, or make a deposit or withdrawal to an existing account please press '1'")
    print("If you would like an account report please press '2'")
    print("If you would like to cancel Press '3'")

    #blank input waits for the user to make a selection from the previous options
    menuChoice = input("")

    #checks the users input for acceptable responses
    #If user input matches an accepted input then that if wil run and take the user to the appropriate menu
    if menuChoice == "1":
        menuLoop = False
        dataEntry()
        #after the user is finished with the data entry function they are offered the choice to end the program or
        # return to the main menu to continue using other features
        continueOption = input("Press '1' to quit program, press '2' to return to main menu")
        if continueOption == "2":
                menuLoop = True
        else:
            print("Quitting application")

    elif menuChoice == "2":
        menuLoop = False
        reportsOptions()

    elif menuChoice == "3":
        print("Selection cancelled, thank you for using QA bank")
        menuLoop = False

    #if user input does not match any accepted answer then the loop restarts and the
    # user is prompted to re enter the data
    else:
        print("Invalid selection, please try again")

