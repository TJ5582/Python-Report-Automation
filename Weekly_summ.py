from __future__ import unicode_literals

from datetime import datetime, timedelta
from pymongo import MongoClient
import pandas as pd
import MySQLdb
import html


from sshtunnel import SSHTunnelForwarder


# Note: 1) Return False anytime in case you want to discard the event
#         2) Or fill up the 'Return data' carefully
	
def db_connect():
	with SSHTunnelForwarder(('124.153.92.179', 22), ssh_password='ED%$3sdfD&', ssh_username='tejinders', remote_bind_address=('127.0.0.3', 3306)) as server:
		conn = MySQLdb.connect(host='127.0.0.1', port=server.local_bind_port, user='tejinders', passwd='T3j1nde$091')
		cursor = conn.cursor()


#	conn = MySQLdb.connect("192.168.100.116","campaign","Cm()$Um#%082","udio_wallet")
#	conn = MySQLdb.connect('udio_wallet', user='campaign', password='Cm()$Um#%082')
#	cursor = conn.cursor()

#def disbursed_sum():

	# ------------------------Main logic------------------------
   
		from datetime import date, timedelta

		today = date.today()

		report_date = today.strftime("%B %d, %Y")
		print("report_date=", report_date)
		loan_date = date.today() - timedelta(days=1)
		loan_date = loan_date.strftime("%B %d, %Y")
		print("loan_date =", loan_date)

		rupee_symbol = u"\u20B9"
		rupee_symbol = rupee_symbol.encode(encoding='UTF-8',errors='strict')
		#print rupee_symbol

		loan_customers = pd.read_sql('''
			SELECT
			count(b.mobile_number) as 'Total Users', sum(a.amount) as 'Total Amount' from udio_wallet.dw_transaction a
			JOIN udio_wallet.dw_wallet_transaction wt on wt.txn_code = a.txn_code and a.consumer_id=wt.consumer_id
			JOIN udio_wallet.dw_user_wallet uw on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user b
			ON a.consumer_id = b.consumer_id
			and a.transaction_status='success'
			and a.txn_type_code = 'mcd'
			and a.txn_mode = 'cr'
			and a.merchant_id = 40006939
			and uw.wallet_type_id = 12
			and a.amount >=1000
			AND a.txn_refnum like ('%TP%')
			and a.transaction_date >= "2019-05-01 00:00:00" and a.transaction_date < CURDATE();
			''',con = conn)

		total_loan_customers = int(loan_customers["Total Users"])
		total_loan_amount = int(loan_customers["Total Amount"])

		print ("Query 1 = Total Loan customers executed")

		loan_trans_summry = pd.read_sql('''
			SELECT 
			c.name as "Transaction Type",
			a.txn_type_code,
			sum(a.amount) as "Amount",
			COUNT(DISTINCT a.consumer_id) as "No. of Unique Customer",
			count(a.txn_type_code) as "No. of transactions"
			from udio_wallet.dw_transaction a
			JOIN udio_wallet.dw_wallet_transaction wt on wt.txn_code = a.txn_code and a.consumer_id=wt.consumer_id
			JOIN udio_wallet.dw_user_wallet uw on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user b
			ON a.consumer_id = b.consumer_id
			INNER JOIN udio_wallet.dw_transaction_type c
			ON a.txn_type_code = c.code
			where b.mobile_number in (
			SELECT
			b.mobile_number from udio_wallet.dw_transaction a
			JOIN udio_wallet.dw_wallet_transaction wt on wt.txn_code = a.txn_code and a.consumer_id=wt.consumer_id
			JOIN udio_wallet.dw_user_wallet uw on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user b
			ON a.consumer_id = b.consumer_id
			and a.transaction_status='success'
			and a.txn_type_code = 'mcd'
			and a.txn_mode = 'cr'
			and a.merchant_id = 40006939
			and uw.wallet_type_id = 12
			and a.amount >=1000
			AND a.txn_refnum like ('%TP%')
			and a.transaction_date >= "2019-05-01 00:00:00" and a.transaction_date < CURDATE()
			)
			and a.transaction_status='success'
			and wt.status='success'
			AND a.txn_mode='dr'
			and a.product_id=2
			and uw.wallet_type_id = 12
			group by a.txn_type_code;
			''',con = conn)
		
		print ("Query 2 = Loan Trans executed")
		

		#### User Loan Wallet Balance
		loan_wal_bal = pd.read_sql('''
			select count(a.consumer_id) as "Count",
			sum(a.balance) as "Wal_Balance"
			from udio_wallet.dw_user_wallet a
			INNER JOIN udio_wallet.b2c_user b
			ON a.consumer_id = b.consumer_id
			where b.mobile_number in (
			SELECT
			b.mobile_number from udio_wallet.dw_transaction a
			JOIN udio_wallet.dw_wallet_transaction wt on wt.txn_code = a.txn_code and a.consumer_id=wt.consumer_id
			JOIN udio_wallet.dw_user_wallet uw on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user b
			ON a.consumer_id = b.consumer_id
			and a.transaction_status='success'
			and a.txn_type_code = 'mcd'
			and a.txn_mode = 'cr'
			and a.merchant_id = 40006939
			and uw.wallet_type_id = 12
			and a.amount >=1000
			AND a.txn_refnum like ('%TP%')
			and a.transaction_date >= "2019-05-01 00:00:00" and a.transaction_date < CURDATE()
			)
			and a.wallet_type_id='12'
			and a.product_id='2'
			and a.status='active';
			''',con = conn)

		#print loan_wal_bal
		print ("Query 3 = Wallet Balance executed")
		### Adding Balance Data to the data frame
		#num = loan_trans_summry.last_valid_index()
		#print(num + 1)
		#loan_trans_summry.iloc[num + 1] = ["Balance","BAL",loan_wal_bal["Wal_Balance"][0],loan_wal_bal["Count"][0],0] 

		summ = pd.DataFrame({'Transaction Type':'Balance',
			'txn_type_code':'BAL',
			'Amount':loan_wal_bal["Wal_Balance"][0],
			'No. of Unique Customer':total_loan_customers,
			'No. of transactions':0}, index=[0])

		loan_trans_summry = loan_trans_summry.append(summ)

		#### Card Transaction Description
		card_trans_desc = pd.read_sql('''
			SELECT 
			a.narration as "Merchant Name",
			sum(a.transaction_amount) as "Amount",
			count(a.txn_code) as "No. of Transactions",
			a.txn_type as "Transaction Type",
			count(DISTINCT a.consumer_id) "Distinct Users"
			from udio_wallet.dw_card_transaction a
			INNER JOIN udio_wallet.dw_transaction b on a.txn_code = b.txn_code and a.consumer_id=b.consumer_id
			INNER JOIN udio_wallet.dw_wallet_transaction wt on b.txn_code = wt.txn_code and b.consumer_id=wt.consumer_id
			INNER JOIN udio_wallet.dw_user_wallet uw on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user c on a.consumer_id=c.consumer_id
			where b.txn_type_code='CT'
			AND a.status='success'
			AND b.transaction_status='success'
			AND b.txn_mode='dr'
			AND b.product_id='2'
			AND c.mobile_number in (
			SELECT
			b.mobile_number from udio_wallet.dw_transaction a
			JOIN udio_wallet.dw_wallet_transaction wt on wt.txn_code = a.txn_code and a.consumer_id=wt.consumer_id
			JOIN udio_wallet.dw_user_wallet uw on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user b
			ON a.consumer_id = b.consumer_id
			and a.transaction_status='success'
			and a.txn_type_code = 'mcd'
			and a.txn_mode = 'cr'
			and a.merchant_id = 40006939
			and uw.wallet_type_id = 12
			and a.amount >=1000
			AND a.txn_refnum like ('%TP%')
			and a.transaction_date >= "2019-05-01 00:00:00" and a.transaction_date < CURDATE()
			)
			and uw.wallet_type_id = 12
			group by 1
			order by 2 DESC;
			''',con = conn)

		print ("Query 4 = Card Transaction executed")

		card_merchant_count = card_trans_desc.groupby('Transaction Type')["Merchant Name"].count()
		###### Online & Offline
		card_type_sum = card_trans_desc.groupby('Transaction Type').sum()

		#print card_type_sum
		on_card_amount = round(card_type_sum.loc['CARDECOM']['Amount'],0)
		on_card_trans = card_type_sum.loc['CARDECOM']['No. of Transactions']

		off_card_amount = round(card_type_sum.loc['POSPURCH']['Amount'],0)
		off_card_trans = card_type_sum.loc['POSPURCH']['No. of Transactions']

		total_card_amt = on_card_amount + off_card_amount
		total_card_trans = on_card_trans + off_card_trans

		card_share_on = round(((on_card_amount / total_card_amt) * 100),0)
		card_share_off = round(((off_card_amount / total_card_amt) * 100),0)
		total_card_share = round(card_share_on + card_share_off,0)

		print ("Share == ",card_share_on,card_share_off,total_card_share)

		card_on_trans_desc = card_trans_desc.loc[card_trans_desc["Transaction Type"] == 'CARDECOM',].sort_values(by=['Amount'], ascending=False)
		card_off_trans_desc = card_trans_desc.loc[card_trans_desc["Transaction Type"] == 'POSPURCH',].sort_values(by=['Amount'], ascending=False)

				
		on = pd.DataFrame({'Merchant Name':'ONLINE TOTAL',
			'Amount':on_card_amount,
			'No. of Transactions':on_card_trans,
			'Transaction Type':"CARDECOM",
			'Distinct Users':""}, columns=['Merchant Name', 'Amount', 'No. of Transactions','Transaction Type','Distinct Users'], index=[0])

		card_on_trans_desc = card_on_trans_desc.append(on)

		off = pd.DataFrame({'Merchant Name':'OFFLINE TOTAL',
			'Amount':off_card_amount,
			'No. of Transactions':off_card_trans,
			'Transaction Type':"POSPURCH",
			'Distinct Users':""}, columns=['Merchant Name', 'Amount', 'No. of Transactions','Transaction Type','Distinct Users'], index=[0])

		card_off_trans_desc = card_off_trans_desc.append(off)

		card_on_trans_desc = card_on_trans_desc[['Merchant Name', 'Amount', 'No. of Transactions','Transaction Type']]
		card_off_trans_desc = card_off_trans_desc[['Merchant Name', 'Amount', 'No. of Transactions','Transaction Type']]

		#### Writing it to csv file
		card_on_trans_desc.to_csv("D:\Work\Online_Credit-Card-Transaction.csv", index=False)
		card_off_trans_desc.to_csv("D:\Work\Offline_Credit-Card-Transaction.csv", index=False)



		#### Card Transaction amount to find unique on/offline customers
		card_unique = pd.read_sql('''
			SELECT 
			a.txn_type  "Transaction Type",
			count(DISTINCT a.consumer_id) AS "Distinct Users",
			SUM(a.transaction_amount) as "Amount"
			from udio_wallet.dw_card_transaction a
			INNER JOIN udio_wallet.dw_transaction b on a.txn_code = b.txn_code and a.consumer_id=b.consumer_id
			INNER JOIN udio_wallet.dw_wallet_transaction wt on b.txn_code = wt.txn_code and b.consumer_id=wt.consumer_id
			INNER JOIN udio_wallet.dw_user_wallet uw on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user c on a.consumer_id=c.consumer_id
			where b.txn_type_code='CT'
			AND a.status='success'
			AND b.transaction_status='success'
			AND b.txn_mode='dr'
			AND b.product_id='2'
			AND c.mobile_number in (
			SELECT
			b.mobile_number from udio_wallet.dw_transaction a
			JOIN udio_wallet.dw_wallet_transaction wt on wt.txn_code = a.txn_code and a.consumer_id=wt.consumer_id
			JOIN udio_wallet.dw_user_wallet uw on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user b
			ON a.consumer_id = b.consumer_id
			and a.transaction_status='success'
			and a.txn_type_code = 'mcd'
			and a.txn_mode = 'cr'
			and a.merchant_id = 40006939
			and uw.wallet_type_id = 12
			and a.amount >=1000
			AND a.txn_refnum like ('%TP%')
			and a.transaction_date >= "2019-05-01 00:00:00" and a.transaction_date < CURDATE()
			)
			and uw.wallet_type_id = 12
			GROUP by a.txn_type;		
				''',con = conn)

		print ("Query 5 = Card Unique Users executed")		
		##### Online and Offline Card Distinct users
		on_distinct_users = (card_unique.loc[card_unique['Transaction Type'] == 'CARDECOM' , 'Distinct Users']).tolist()
		off_distinct_users =  (card_unique.loc[card_unique['Transaction Type'] == 'POSPURCH' , 'Distinct Users']).tolist()

		tot_card_distinct_users = on_distinct_users[0] + off_distinct_users[0]  

		##### Online and Offline Avergare Transaction calculation
		avg_tot_card_trans = round(total_card_trans/tot_card_distinct_users,2)  
		avg_on_card_trans = round(on_card_trans/on_distinct_users,2) 
		avg_off_card_trans = round(off_card_trans/off_distinct_users,2) 
		
		#print ("Total = ",total_card_amt,total_card_trans)
		#print ("Average =",avg_tot_card_trans,avg_on_card_trans,avg_off_card_trans)

		
		############## Card Total
		total_card_amount = round(card_trans_desc["Amount"].sum(),0)
		total_card_trans = card_trans_desc["No. of Transactions"].sum()
		total_vol_avg = round(total_card_amount / total_card_trans,2)
		#print ("Total Card Amount",total_card_amount)
		#print ("Total Card trans",total_card_trans)

		loan_trans_summry.loc[loan_trans_summry['Transaction Type'] == 'Card Transaction','Amount'] = total_card_amount
		loan_trans_summry.loc[loan_trans_summry['Transaction Type'] == 'Card Transaction','No. of transactions'] = total_card_trans

		
		#### Recharge Transaction Description
		recharge_trans_desc = pd.read_sql('''
			SELECT a.operator_type as "Operator Type",
			a.recharge_type as "Recharge Type",
			a.operator as "Operator",
			a.transaction_status as "Transaction Status",
			sum(a.amount) as "Amount",
			count(a.txn_code) as "No. of Transactions"
			from udio_wallet.dw_recharge_transaction a
			INNER JOIN udio_wallet.dw_transaction b
			ON a.consumer_id=b.consumer_id and a.txn_code = b.txn_code
			JOIN udio_wallet.dw_wallet_transaction wt
			on wt.txn_code = a.txn_code and a.consumer_id=wt.consumer_id
			JOIN udio_wallet.dw_user_wallet uw
			on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user c
			ON a.consumer_id = c.consumer_id
			where c.mobile_number in (
			SELECT
			b.mobile_number from udio_wallet.dw_transaction a
			JOIN udio_wallet.dw_wallet_transaction wt on wt.txn_code = a.txn_code and a.consumer_id=wt.consumer_id
			JOIN udio_wallet.dw_user_wallet uw on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user b
			ON a.consumer_id = b.consumer_id
			and a.transaction_status='success'
			and a.txn_type_code = 'mcd'
			and a.txn_mode = 'cr'
			and a.merchant_id = 40006939
			and uw.wallet_type_id = 12
			and a.amount >=1000
			AND a.txn_refnum like ('%TP%')
			and a.transaction_date >= "2019-05-01 00:00:00" and a.transaction_date < CURDATE()
			)
			and a.transaction_status='success'
			and b.transaction_status='success'
			and b.product_id=2
			and uw.wallet_type_id = 12
			group by a.operator;
			''',con = conn)

		print ("Query 6 = Recharge executed")		
		#### Writing it to csv file

		total_recharge_amount = round(recharge_trans_desc["Amount"].sum(),0)
		total_recharge_trans = round(recharge_trans_desc["No. of Transactions"].sum(),0)
		#print ("Recharge Total =",total_recharge_amount)

		rec_tot = pd.DataFrame({'Operator Type' : '',
			'Recharge Type' : '',
			'Operator' : '',
			'Transaction Status' : 'RECHARGE TOTAL',
			'Amount' : total_recharge_amount,
			'No. of Transactions' : total_recharge_trans
			}, index=[0])

		recharge_trans_desc = recharge_trans_desc.append(rec_tot)

		recharge_trans_desc = recharge_trans_desc[['Operator Type', 'Recharge Type', 'Operator','Transaction Status','Amount','No. of Transactions']]

		#### Writing it to csv file
		recharge_trans_desc.to_csv(r"D:\Work\Recharge_Transaction_Details.csv", index=False)


		#print recharge_trans_desc

		#### Bill Payment Transaction Description
		billpay_trans_desc = pd.read_sql('''
			SELECT a.provider as 'Provider',
			a.provider_type  as 'Provider Type',
			sum(a.amount) as 'Amount',
			count(a.txn_code) as 'No. of Transactions'
			from udio_wallet.dw_bill_payment_transaction a
			INNER JOIN udio_wallet.dw_transaction b
			ON a.consumer_id=b.consumer_id and a.txn_code = b.txn_code
			JOIN udio_wallet.dw_wallet_transaction wt on wt.txn_code = a.txn_code and a.consumer_id=wt.consumer_id
			JOIN udio_wallet.dw_user_wallet uw on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user c
			ON a.consumer_id = c.consumer_id
			where c.mobile_number in (
			SELECT
			b.mobile_number from udio_wallet.dw_transaction a
			JOIN udio_wallet.dw_wallet_transaction wt on wt.txn_code = a.txn_code and a.consumer_id=wt.consumer_id
			JOIN udio_wallet.dw_user_wallet uw on uw.id = wt.user_wallet_id
			INNER JOIN udio_wallet.b2c_user b
			ON a.consumer_id = b.consumer_id
			and a.transaction_status='success'
			and a.txn_type_code = 'mcd'
			and a.txn_mode = 'cr'
			and a.merchant_id = 40006939
			and uw.wallet_type_id = 12
			and a.amount >=1000
			AND a.txn_refnum like ('%TP%')
			and a.transaction_date >= "2019-05-01 00:00:00" and a.transaction_date < CURDATE()
			)
			and b.transaction_status='success'
			and a.transaction_status='success'
			and b.product_id=2
			and uw.wallet_type_id = 12
			group by 1;
			''',con = conn)
		
		print ("Query 7 = Bill pay executed")		

		total_billpay_amount = round(billpay_trans_desc["Amount"].sum(),0)
		total_billpay_trans = round(billpay_trans_desc["No. of Transactions"].sum(),0)

		bill_tot = pd.DataFrame({'Provider' : '',
			'Provider Type' : 'BILL-PAY TOTAL',
			'Amount' : total_billpay_amount,
			'No. of Transactions' : total_billpay_trans
			}, index=[0])

		billpay_trans_desc = billpay_trans_desc.append(bill_tot)

		billpay_trans_desc = billpay_trans_desc[['Provider', 'Provider Type', 'Amount','No. of Transactions']]



		#### Writing it to csv file
		billpay_trans_desc.to_csv(r"D:\Work\Bill-Pay_Transaction_Details.csv", index=False)
		#print billpay_trans_desc

		total_billpay_amount = round(billpay_trans_desc["Amount"].sum(),0)
		#print ("Billing Total =",total_billpay_amount)
		

		#### Rounding Amount column values to 0 digit
		loan_trans_summry["Amount"] = loan_trans_summry["Amount"].map(lambda x: round(x, 0))

		#### sum of Amount column
		total_amount = round(loan_trans_summry['Amount'].sum(),0)
		#print(total_amount)
				
		#### Calculating  Avg. No. of transaction per user
		loan_trans_summry["Avg. No. of transaction per user"] = loan_trans_summry["No. of transactions"] / loan_trans_summry["No. of Unique Customer"]
		#### Rounding Avg. No. of transaction per user column values to 2 digit
		loan_trans_summry["Avg. No. of transaction per user"] = loan_trans_summry["Avg. No. of transaction per user"].map(lambda x: round(x, 2))
		
		#### Calculating Share % of each Transaction Type
		loan_trans_summry["Share %"] = ((loan_trans_summry["Amount"] / total_amount) * 100)
		
		#### Rounding Share % column values to 2 digit
		loan_trans_summry["Share %"] = loan_trans_summry["Share %"].map(lambda x: round(x, 2))
		share_sum = round(loan_trans_summry['Share %'].sum(),2)
		loan_trans_summry['Share %'] = loan_trans_summry['Share %'].astype(str) + '%'

		loan_trans_summry = loan_trans_summry.sort_values(by=['Amount'], ascending=False)

		loan_trans_summry.loc[loan_trans_summry["Transaction Type"] == "Balance","No. of transactions"] = "NA"
		loan_trans_summry.loc[loan_trans_summry["Transaction Type"] == "Balance","Avg. No. of transaction per user"] = "NA"

		loan_trans_summry.loc[loan_trans_summry["Transaction Type"] == "Card Transaction","No. of Unique Customer"] = tot_card_distinct_users
		loan_trans_summry.loc[loan_trans_summry["Transaction Type"] == "Card Transaction","Avg. No. of transaction per user"] = avg_tot_card_trans

		#print loan_trans_summry
		#print(loan_wal_bal["Count"][0])
		#print(loan_wal_bal["Wal_Balance"][0])


		#print ("Total Transaction Amount =",loan_trans_summry['Amount'].sum())
		total_trans_sum = loan_trans_summry['Amount'].sum()
		
				
		summ2 = pd.DataFrame({'Transaction Type':'Total',
			'txn_type_code':'TOT',
			'Amount':total_amount,
			'No. of Unique Customer':'',
			'No. of transactions':'',
			'Avg. No. of transaction per user':'',
			'Share %':str(share_sum)+'%'}, columns=['Transaction Type', 'txn_type_code', 'Amount','No. of Unique Customer','No. of transactions','Avg. No. of transaction per user','Share %'], index=[0])

		loan_trans_summry = loan_trans_summry.append(summ2)
		
		
		#loan_trans_summry.iloc[loan_trans_summry.last_valid_index()] = ["Total","TOT",total_trans_sum,'','','',share_sum]

		loan_trans_summry = loan_trans_summry[['Transaction Type', 'txn_type_code', 'Amount','Share %','No. of Unique Customer','No. of transactions','Avg. No. of transaction per user']]
		loan_trans_summry = loan_trans_summry.drop(columns=['txn_type_code'])
		
		#### Writing it to csv file
		loan_trans_summry.to_csv("D:\Work\Top-Up-Loan_Transaction_Details.csv", index=False)

		#loan_trans_summry.set_index(["Transaction Type"], inplace = True, append = True, drop = True) 
		pd.options.display.float_format = '{:,}'.format

		loan_summ_html = loan_trans_summry.to_html(border='3', justify='center', col_space='10%', index=False)
		loan_summ_html = loan_summ_html.replace('<tr>','<tr style="text-align: center;">')
		loan_summ_html = loan_summ_html.replace('<th style="min-width: 10%;">','<th bgcolor="khaki" style="min-width: 10%;">')
		loan_summ_html = loan_summ_html.replace('<td>Total</td>','<td bgcolor="yellow"><b>Total</b></td>')
			

		conn.close()

#def email_send():
# Python code to illustrate Sending mail with attachments 
# from your Gmail account  
  
	# libraries to be imported 
		import smtplib 
		from email.mime.multipart import MIMEMultipart 
		from email.mime.text import MIMEText 
		from email.mime.base import MIMEBase 
		from email import encoders
		from datetime import date, timedelta
		   
		fromaddr = "tejinder.singh@dhanipay.in"
		toaddr = "tejinder.singh@dhanipay.in"
		   
		# instance of MIMEMultipart 
		msg = MIMEMultipart() 
		  
		# storing the senders email address   
		msg['From'] = fromaddr 
		  
		# storing the receivers email address  
		msg['To'] = toaddr 
		  
		# storing the subject  
		msg['Subject'] = "Spend Summary of Top-Up Loan Users = " + (date.today().strftime("%B %d, %Y"))
		  
		# string to store the body of the mail 
		body = ""

		html = """\
			<html>
	  			<head align='center'><h2><center><u>TOP-UP LOAN CUSTOMER SPEND SUMMARY</u></center></h2></head>
	  			<body>
	  			<br/>
	  			<table  border="3">
				<tbody>
				<tr>
				<td><span style="color: #000080;">Total No. Users</span></td>
				<td>{}</td>
				</tr>
				<tr>
				<td><span style="color: #800000;">Total Loan Disbursed</span></td>
				<td><span style="color: #800000;">{:,}</span></td>
				</tr>
				<tr>
				<td><span style="color: #008000;">Loan Disbursed Date till</span></td>
				<td><span style="color: #008000;">{}</span></td>
				</tr>
				</tbody>
				</table>
				<br/>
				<br/>
	  			{}
	  			<br/>
	  			<br/>
	  			<table  border="3" width='70%'>
				<tbody>
				<tr>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				</tr>
				<tr>
				<td colspan="5" align="center" bgcolor="mistyrose"><span style="color: #000080;"><strong>CARD TRANSACTION SUMMARY</strong></span></td>
				</tr>
				<tr>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				</tr>
				<tr>
				<td colspan="2" align="center" bgcolor="powderblue"><span style="color: #0000ff;"><strong>TOTAL SPEND</strong></span></td>
				<td>&nbsp;</td>
				<td colspan="2" align="center" bgcolor="lightsalmon"><span style="color: #800000;"><strong>ONLINE</strong></span></td>
				</tr>
				<tr>
				<td><span style="color: #0000ff;">Unique Card customers</span></td>
				<td>{}</td>
				<td>&nbsp;</td>
				<td><span style="color: #800000;">Unique Online Card Users</span></td>
				<td><span style="color: #800000;">{}</span></td>
				</tr>
				<tr>
				<td><span style="color: #0000ff;">&nbsp;</span></td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td><span style="color: #800000;">Total Spend Volume</span></td>
				<td><span style="color: #800000;">{:,}</span></td>
				</tr>
				<tr>
				<td><span style="color: #0000ff;">Total no. of merchants</span></td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td><span style="color: #800000;">Total no. of merchants</span></td>
				<td><span style="color: #800000;">&nbsp;</span></td>
				</tr>
				<tr>
				<td><span style="color: #0000ff;">&nbsp;</span></td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td><span style="color: #800000;">Total no. of transactions</span></td>
				<td><span style="color: #800000;">{}</span></td>
				</tr>
				<tr>
				<td><span style="color: #0000ff;">Total no. of transactions</span></td>
				<td>{}</td>
				<td>&nbsp;</td>
				<td><span style="color: #800000;">Avg. No. of Card transactions</span></td>
				<td><span style="color: #800000;">{}</span></td>
				</tr>
				<tr>
				<td><span style="color: #0000ff;">&nbsp;</span></td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td><span style="color: #800000;">% Online Volume Share</span></td>
				<td><span style="color: #800000;">{}%</span></td>
				</tr>
				<tr>
				<td><span style="color: #0000ff;">Total Spend Volume</span></td>
				<td>{:,}</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				</tr>
				<tr>
				<td><span style="color: #0000ff;">&nbsp;</span></td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td colspan="2" align="center" bgcolor="aquamarine"><span style="color: #008000;"><strong>OFFLINE</strong></span></td>
				</tr>
				<tr>
				<td><span style="color: #0000ff;">Total Volume Avg.</span></td>
				<td>{}</td>
				<td>&nbsp;</td>
				<td><span style="color: #008000;">Unique Offline Card Users</span></td>
				<td><span style="color: #008000;">{}</span></td>
				</tr>
				<tr>
				<td><span style="color: #0000ff;">&nbsp;</span></td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td><span style="color: #008000;">Total Spend Volume</span></td>
				<td><span style="color: #008000;">{:,}</span></td>
				</tr>
				<tr>
				<td><span style="color: #0000ff;">Avg. No. of Card transactions</span></td>
				<td>{}</td>
				<td>&nbsp;</td>
				<td><span style="color: #008000;">Total no. of merchants</span></td>
				<td><span style="color: #008000;">&nbsp;</span></td>
				</tr>
				<tr>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td><span style="color: #008000;">Total no. of transactions</span></td>
				<td><span style="color: #008000;">{}</span></td>
				</tr>
				<tr>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td><span style="color: #008000;">Avg. No. of Card transactions</span></td>
				<td><span style="color: #008000;">{}</span></td>
				</tr>
				<tr>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td><span style="color: #008000;">% Offline Volume Share</span></td>
				<td><span style="color: #008000;">{}%</span></td>
				</tr>
				<tr>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				</tr>
				</tbody>
				</table>
				</body>
			</html>
		""".format(total_loan_customers,total_loan_amount,loan_date,loan_summ_html,tot_card_distinct_users,on_distinct_users[0],on_card_amount,on_card_trans,total_card_trans,avg_on_card_trans,card_share_on,total_card_amount,total_vol_avg,off_distinct_users[0],off_card_amount,avg_tot_card_trans,off_card_trans,avg_off_card_trans,card_share_off)
		  
		# attach the body with the msg instance 
		msg.attach(MIMEText(body, 'plain'))
		msg.attach(MIMEText(html, 'html'))  
		  
		# open the file to be sent  
		filename = "Online_Credit-Card-Transaction.csv"
		attachment = open("D:\\Work\\Online_Credit-Card-Transaction.csv", "rb") 
		filename2 = "Recharge_Transaction_Details.csv"
		attachment2 = open("D:\\Work\\Recharge_Transaction_Details.csv", "rb") 
		filename3 = "Bill-Pay_Transaction_Details.csv"
		attachment3 = open("D:\\Work\\Bill-Pay_Transaction_Details.csv", "rb") 
		filename4 = "Offline_Credit-Card-Transaction.csv"
		attachment4 = open("D:\\Work\\Offline_Credit-Card-Transaction.csv", "rb") 
		  
		###### File 1 ===============================
		# instance of MIMEBase and named as p 
		p = MIMEBase('application', 'octet-stream') 
		  
		# To change the payload into encoded form 
		p.set_payload((attachment).read()) 
		  
		# encode into base64 
		encoders.encode_base64(p) 
		   
		p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
		  
		# attach the instance 'p' to instance 'msg' 
		msg.attach(p) 
		
		###### File 2 ===============================
		p2 = MIMEBase('application', 'octet-stream') 
		  
		# To change the payload into encoded form 
		p2.set_payload((attachment2).read()) 
		  
		# encode into base64 
		encoders.encode_base64(p2) 
		   
		p2.add_header('Content-Disposition', "attachment2; filename= %s" % filename2) 
		  
		# attach the instance 'p' to instance 'msg' 
		msg.attach(p2) 

		###### File 3 ===============================
		p3 = MIMEBase('application', 'octet-stream') 
		  
		# To change the payload into encoded form 
		p3.set_payload((attachment3).read()) 
		  
		# encode into base64 
		encoders.encode_base64(p3) 
		   
		p3.add_header('Content-Disposition', "attachment3; filename= %s" % filename3) 
		  
		# attach the instance 'p' to instance 'msg' 
		msg.attach(p3) 

		###### File 4 ===============================
		p4 = MIMEBase('application', 'octet-stream') 
		  
		# To change the payload into encoded form 
		p4.set_payload((attachment4).read()) 
		  
		# encode into base64 
		encoders.encode_base64(p4) 
		   
		p4.add_header('Content-Disposition', "attachment4; filename= %s" % filename4) 
		  
		# attach the instance 'p' to instance 'msg' 
		msg.attach(p4) 

		# creates SMTP session 
		s = smtplib.SMTP('smtp.gmail.com', 587) 
		  
		# start TLS for security 
		s.starttls() 
		  
		# Authentication 
		s.login(fromaddr, "XXXXX") 
		  
		# Converts the Multipart msg into a string 
		text = msg.as_string() 
		  
		# sending the mail 
		s.sendmail(fromaddr, toaddr, text) 
		  
		# terminating the session 
		s.quit() 

if __name__ == "__main__":
	db_connect()
#	email_send()
#	disbursed_sum()
