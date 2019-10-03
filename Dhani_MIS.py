
#### OUTPUT EMAIL AND EXCEL BOTH

import pandas as pd
import numpy as np
from datetime import date, timedelta

# libraries to be imported 
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from datetime import date, timedelta


#s = pd.Series([1, 2], index=["a", "b"])
#deep = s.copy()
#shallow = s.copy(deep=False)

#print (s)
#print (deep)
#print(shallow)

#### Disabling SettingwithCopyWarning 
pd.set_option('mode.chained_assignment', None)

data_frame = pd.read_excel('mod_Daily App Flyer data with City and Way2Online.xlsx', sheet_name='FINAL_DAILY')

spends_df = pd.read_excel('Morning MIS.xlsx', sheet_name='Master Sheet')

spends_df.reset_index(inplace=True)

#print ("============== sPENDS dF =========================")

#print (spends_df.columns)

today = date.today()
report_date = today.strftime("%d-%b-%y")
print("report_date=", report_date)
yest_date = date.today() - timedelta(days=1)
yesterday_date = yest_date.strftime("%d-%b-%y")
print("yesterday date =", yesterday_date)



#yesterday_date = '01-Aug-19'
day = today.strftime("%a")
print (day)

#day = 'Mon'

#df = df.loc[(df['Loan_Type'] != 'BL') & (df['Created date'] == yesterday_date),:]
if (day != 'Mon'):
	df_mod = data_frame[(data_frame['Loan_Type'] != 'BL') & (data_frame['Created date'] == yesterday_date)]
	num_of_days = 1
	dd_date = (date.today() - timedelta(days=1)).strftime("%d-%b-%y")
	yesterday_day = (date.today() - timedelta(days=1)).strftime("%a")


else:
	last_friday_date = (date.today() - timedelta(days=3)).strftime("%d-%b-%y")
	#print (last_friday_date)
	data_frame = data_frame[(data_frame['Loan_Type'] != 'BL') & (data_frame['Created date'] >= last_friday_date)]
	fri_date = date.today() - timedelta(days=3)
	num_of_days = (today - fri_date)
	#print ("num_of_days = ",num_of_days.days)
	num_of_days = num_of_days.days


#print(data_frame.shape)

#dates = (data_frame['Created date'].unique())
#print (dates)

#df.set_index("Created date", inplace=True)

counter = num_of_days
index = 0
html_str =''
df_html=pd.DataFrame()



while (counter > 0):

	dd_date = (date.today() - timedelta(days=counter)).strftime("%d-%b-%y")
	print (dd_date)
	df_mod = data_frame[(data_frame['Loan_Type'] != 'BL') & (data_frame['Created date'] == dd_date)]
	#print df_mod

	yesterday_day = (date.today() - timedelta(days=counter)).strftime("%a")


	print("########## Application sum ORGANIC ######################")

	df_mod["Media_cost"].fillna("Organic", inplace = True) 

	df1 = df_mod.loc[df_mod['Partner'] != 'inmobiagen',:]

	app_sum_org_1 = pd.pivot_table(df_mod, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='count_dis_Allstage', aggfunc='sum')
	app_sum_org_1.reset_index(inplace=True)
	#print(app_sum_org_1)

	"""
	for i in app_sum_org_1:
		#i = i.strftime("%d-%b-%y")
		print ("i type =",type(i))
	"""


	app_sum_org_2 = pd.pivot_table(df1, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='count_dis_Allstage', aggfunc='sum')
	app_sum_org_2.reset_index(inplace=True)
	#print app_sum_org_2


	app_web = list(app_sum_org_1.loc[app_sum_org_1["Media_cost"] == 'WEB','Total'])

	if(app_web == []):
		app_web.append(0)


	app_blanks = list(app_sum_org_2.loc[app_sum_org_2["Media_cost"] == 'Organic','Total'])
	if(app_blanks == []):
		app_blanks.append(0)

	app_organic = app_web[0] + app_blanks[0]
	#print (app_organic)


	print("########## Disbursal Count ORGANIC ######################")

	disbursal_sum_org_1 = pd.pivot_table(df_mod, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='disb_cust', aggfunc='sum')
	disbursal_sum_org_1.reset_index(inplace=True)

	disbursal_sum_org_2 = pd.pivot_table(df1, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='disb_cust', aggfunc='sum')
	disbursal_sum_org_2.reset_index(inplace=True)

	disbursal_web = list(disbursal_sum_org_1.loc[disbursal_sum_org_1["Media_cost"] == 'WEB','Total'])
	
	if(disbursal_web ==[]):
		disbursal_web.append(0)

	#print(app_sum_org_2.columns)
	disbursal_blanks = list(disbursal_sum_org_2.loc[disbursal_sum_org_2["Media_cost"] == 'Organic','Total'])

	if(disbursal_blanks ==[]):
		disbursal_blanks.append(0)

	disbursal_organic = disbursal_web[0] + disbursal_blanks[0]
	#print (disbursal_organic)


	print("########## Disbursal AMOUNT ORGANIC ######################")

	disbursal_amount_org_1 = pd.pivot_table(df_mod, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='disb_amount', aggfunc='sum')
	disbursal_amount_org_1.reset_index(inplace=True)

	disbursal_amount_org_2 = pd.pivot_table(df1, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='disb_amount', aggfunc='sum')
	disbursal_amount_org_2.reset_index(inplace=True)

	disbursal_amt_web = list(disbursal_amount_org_1.loc[disbursal_amount_org_1["Media_cost"] == 'WEB','Total'])

	if(disbursal_amt_web == []):
		disbursal_amt_web.append(0)


	disbursal_amt_blanks = list(disbursal_amount_org_2.loc[disbursal_amount_org_2["Media_cost"] == 'Organic','Total'])
	
	if(disbursal_amt_blanks == []):
		disbursal_amt_blanks.append(0)

	disbursal_amt_organic = disbursal_amt_web[0] + disbursal_amt_blanks[0]
	#print (disbursal_amt_organic)


	print("########## Application sum INORGANIC ######################")

	list_include = ['Adcanpus','adcountymedia_int','admitad1_int','admobly_int','Adsplay','advolt_int','Affle','apogeemobi_int','appfloodaff_int','appmontizemedia_int','Appnext','appnext_int_Retargetting','appsamurai_int','Buddy Loan','bytedanceglobal_int','capslockdigitalsolutions','CD-worldcup-1106','claymotion_int','click2commission_int','Digital','doubleclick_int','doubleclick_int_Retargett','Facebook','FacebookAds_Retargetting','FB_Group_S','glispacpa_int','Google UAC','HA-Aug-SMS','HA-LandingPage','HardApproved-worldcup-11','HA-SegD2,D3-0907','iavatarzaffise_int','Icubewires','InMobi','inmobi_int_Retargetting','LeadBolt','massmediaent_int','mediamath_int','mobidiscover_int','mobisummer_int','mobvista_int','mobwonder_int','netcore_int','None','omobiads_int','Optimise','PA-0108','PA-NDND-0708','PA-P3-0708','PA-P4-09-08-19','PA-Responders-SMS2','Pocket','pointific_int','Pre-Approved - LP','Pre-Approved-0307','revx_int','Saral to Dhani','Seg F-1608','SegD-SMS-107','SegJ-1308','SegK-Mobileregistered','Sense','seventyninemobi_int','shishamdigital_int','silverpush_int','silverpushaffiliate_int','simplemagic_int','snapchat_int','svgmedia_int','themobilyarabia_int','TopUp-Crosssell-1006','TopUpEMI_SMS106','TopUpHindi_SMS2305','TopUp-LandingPage-2506','TopUpLoan_NewDatabase250','Top-Up-RegSMS-090819','Top-Up-SMS-090819','TP-noti-2106','TP-SegallD-2406','TP-SegD-2106','TP-SegDregional-2506','TP-SMS-1207','TP-worldcup-1006','Twitter','tyroo_int','uchuichuan_int','ValueLeaf','Valueleaf API  SMS','vcommission_int','vertozaff_int','VoiceBlast-TopUp','vserv_reg_int','Way 2 Online','Way 2 SMS (27.08.2018)','WEB 3DOT14','WEB Ad2click','WEB Adcanopus','Web apoxy','Web dbm','Web Facebook','WEB Flytext','Web Google','WEB INTELLECT','WEB Mogae','WEB Netcore','WEB Opicle','WEB Optimize','WEB Pback','WEB Tunica','Web ValueLeaf','WEB VODAFONE','WEB2ONLINE','xaprio_int','xyads_int','yahoogemini_int','yoadsmedia_int','Youtube','YT-Pre-Approved','mobpower2_int','P.1-SMS-0709','adapptmobi_int','SMS-HA-0309','Intellectads','mobireckon_int','SMS-Topup-0309','Yaarii2Dhani','SEGJ1-SMS-2706','Way2Online - Salary']

	#df2 = df_mod.loc[df_mod['Media_cost'].isin(list_exclude) == False]

	df11 = df_mod.loc[df_mod['Partner'] == 'inmobiagen',:]

	df3 = df_mod.loc[df_mod['Media_cost'].isin(list_include) == True]

	app_sum_inorg_1 = pd.pivot_table(df3, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='count_dis_Allstage', aggfunc='sum')
	app_sum_inorg_1.reset_index(inplace=True)

	app_sum_inorg_1.to_csv("app_sum_inorg_1.csv")

	

	print ("################### NEW MEDIA COST LIST ################################33333")

	approved_list = ['Organic','Adcanpus','adcountymedia_int','admitad1_int','admobly_int','Adsplay','advolt_int','Affle','apogeemobi_int','appfloodaff_int','appmontizemedia_int','Appnext','appnext_int_Retargetting','appsamurai_int','Biz Interested Customers','Buddy Loan','bytedanceglobal_int','capslockdigitalsolutions','CD-worldcup-1106','claymotion_int','click2commission_int','Connector','Credit Mantri','Dhani Biz Landing Page','Dhani Biz Organic','Dhani Biz SMS (24.05,201','Dhani Club Emailer','Dhani Club Notification','Dhani Club Referral - Ne','Digital','doubleclick_int','doubleclick_int_Retargett','DSAPartnerApp','Existing Customers','Facebook','FacebookAds_Retargetting','FB_Group_S','glispacpa_int','Google UAC','Group Website','HA-Aug-SMS','HA-LandingPage','HardApproved-worldcup-11','HA-SegD2,D3-0907','iavatarzaffise_int','IBHFL Preapproved SMS','Icubewires','Individual','InMobi','inmobi_int_Retargetting','InternalDataBase3','Internal-Database-SMS','Internal-Database-SMS(1)','LeadBolt','massmediaent_int','mediamath_int','mobidiscover_int','MobileRegisteredDatabase','mobisummer_int','mobvista_int','mobwonder_int','moneycontrol_branding','netcore_int','None','omobiads_int','Optimise','ORM','PA-0108','Paisabazaar','Paisabazaar SMS','Paisabazaar SMS Nov','PA-NDND-0708','PA-P3-0708','PA-P4-09-08-19','PA-Responders-SMS2','Pocket','pointific_int','Pre-Approved','Pre-Approved - LP','Pre-Approved (New)','Pre-Approved-0307','revx_int','Saral to Dhani','Seg F-1608','SegD-SMS-107','SegJ-1308','SegK-Mobileregistered','Sense','seventyninemobi_int','shishamdigital_int','silverpush_int','silverpushaffiliate_int','simplemagic_int','SMS','snapchat_int','Social Organic','svgmedia_int','Techno Ruez','themobilyarabia_int','Topup','TopUp-Crosssell-1006','TopUpEMI_SMS106','TopUpHindi_SMS2305','TopUp-LandingPage-2506','TopUpLoan_NewDatabase250','Top-Up-RegSMS-090819','Top-Up-SMS-090819','TP-noti-2106','TP-SegallD-2406','TP-SegD-2106','TP-SegDregional-2506','TP-SMS-1207','TP-worldcup-1006','Trusting Social','TVF','Twitter','tyroo_int','uchuichuan_int','UR Indian Consumer','ValueLeaf','Valueleaf API  SMS','vcommission_int','vertozaff_int','VoiceBlast-TopUp','vserv_reg_int','Way 2 Online','Way 2 SMS (27.08.2018)','WEB','WEB 3DOT14','WEB Ad2click','WEB Adcanopus','Web apoxy','Web dbm','Web Facebook','WEB Flytext','Web Google','WEB INTELLECT','WEB Mogae','WEB Netcore','WEB Opicle','WEB Optimize','WEB Pback','WEB Tunica','Web ValueLeaf','WEB VODAFONE','WEB2ONLINE','xaprio_int','xyads_int','Yaari','yahoogemini_int','yoadsmedia_int','Youtube','YT-Pre-Approved','P.1-SMS-0709','mobpower2_int','adapptmobi_int','SMS-HA-0309','Intellectads','mobireckon_int','SMS-Topup-0309','Yaarii2Dhani','SEGJ1-SMS-2706','Way2Online - Salary','Dhani Biz SMS']

	for x in app_sum_org_1['Media_cost']:
		if str(x) not in approved_list:
			print x

	print ("################### NEW MEDIA COST LIST ENDS ################################33333")

	app_inorganic = list(app_sum_inorg_1.loc[app_sum_inorg_1["Media_cost"] == 'Total','Total'])
	
	if(app_inorganic ==[]):
		app_inorganic.append(0)
	

	if (df11.empty == False):
		app_sum_inorg_2 = pd.pivot_table(df11, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='count_dis_Allstage', aggfunc='sum')
		app_sum_inorg_2.reset_index(inplace=True)
		#app_sum_inorg_2.to_csv("app_sum_inorg_2.csv")

		app_inorganic_blank = list(app_sum_inorg_2.loc[app_sum_inorg_2["Media_cost"] == 'Organic','Total'])

		if(app_inorganic_blank ==[]):
			app_inorganic_blank.append(0)
	else:
		app_inorganic_blank=[]
		app_inorganic_blank.append(0)

	#print (app_inorganic_blank)

	app_inorg = app_inorganic[0] + app_inorganic_blank[0]
	#print (app_inorg)



	print("########## Disbursal count INORGANIC ######################")

	disbursal_sum_inorg_1 = pd.pivot_table(df3, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='disb_cust', aggfunc='sum')
	disbursal_sum_inorg_1.reset_index(inplace=True)

	disbursal_inorganic = list(disbursal_sum_inorg_1.loc[disbursal_sum_inorg_1["Media_cost"] == 'Total','Total'])
	
	if(disbursal_inorganic == []):
		disbursal_inorganic.append(0)

	if (df11.empty == False):
		disbursal_sum_inorg_2 = pd.pivot_table(df11, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='disb_cust', aggfunc='sum')
		disbursal_sum_inorg_2.reset_index(inplace=True)

		disbursal_inorganic_blank = list(disbursal_sum_inorg_2.loc[disbursal_sum_inorg_2["Media_cost"] == 'Organic','Total'])
		#print (disbursal_inorganic_blank)

		if(disbursal_inorganic_blank !=[]):
			disbursal_inorganic_blank = [x for x in disbursal_inorganic_blank if ~np.isnan(x)]
			disbursal_inorganic_blank.append(0)
		else:
			disbursal_inorganic_blank.append(0)
	else:
		disbursal_inorganic_blank=[]
		disbursal_inorganic_blank.append(0)


	#print (disbursal_inorganic_blank)


	disbursal_inorg = disbursal_inorganic[0] + disbursal_inorganic_blank[0]

	#print (disbursal_inorg)


	print("########## Disbursal AMOUNT INORGANIC ######################")

	disbursal_amt_inorg_1 = pd.pivot_table(df3, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='disb_amount', aggfunc='sum')
	disbursal_amt_inorg_1.reset_index(inplace=True)

	disbursal_amt_inorganic = list(disbursal_amt_inorg_1.loc[disbursal_amt_inorg_1["Media_cost"] == 'Total','Total'])

	if(disbursal_amt_inorganic ==[]):
		disbursal_amt_inorganic.append(0)
	

	if (df11.empty == False):
		disbursal_amt_inorg_2 = pd.pivot_table(df11, index = 'Media_cost', columns='Created date',  margins=True, margins_name='Total', values='disb_amount', aggfunc='sum')
		disbursal_amt_inorg_2.reset_index(inplace=True)

		disbursal_amt_inorganic_blank = list(disbursal_amt_inorg_2.loc[disbursal_amt_inorg_2["Media_cost"] == 'Organic','Total'])

		if(disbursal_amt_inorganic_blank !=[]):
			disbursal_amt_inorganic_blank = [x for x in disbursal_amt_inorganic_blank if ~np.isnan(x)]
			disbursal_amt_inorganic_blank.append(0)
		else:
			disbursal_amt_inorganic_blank.append(0)
	else:
		disbursal_amt_inorganic_blank=[]
		disbursal_amt_inorganic_blank.append(0)

	#print (disbursal_amt_inorganic_blank)

	disbursal_amt_inorg = disbursal_amt_inorganic[0] + disbursal_amt_inorganic_blank[0]
	print("########## MIS TOTAL (ORGANIC + INORGANIC) ######################")

	total_app = app_organic + app_inorg
	total_disbursal = disbursal_organic + disbursal_inorg
	total_disbursal_amount = disbursal_amt_organic + disbursal_amt_inorg

	yest_spends = list(spends_df.loc[spends_df['Types'] == 'Dhani Marketing Total',dd_date])
	print (yest_spends)

	if (yest_spends !=[]):
		total_spends = round(yest_spends[0],0)
	else:
		total_spends = 0


	try:
		ATS = round((total_disbursal_amount*10000000)/total_disbursal,0)
	except:
		ATS = 0
	
	try:
		CPA = round(total_spends/total_app,0)
	except:
		CPA = 0
	
	try:
		CPD = round(total_spends/total_disbursal,0)
	except:
		CPD = 0
	
	try:
		A_D_percnt = round((total_disbursal/total_app)*100,0)
	except:
		A_D_percnt = 0
	
	try:
		COA = round((total_spends/(total_disbursal_amount*10000000))*100,0)
	except:
		COA = 0
	
	 
	######### Email part

	fromaddr = "tejinder.singh@dhanipay.in"
	toaddr = ['tejinder.singh@dhanipay.in']
	   
	# instance of MIMEMultipart 
	msg = MIMEMultipart() 
	  
	# storing the senders email address   
	msg['From'] = fromaddr 
	  
	# storing the receivers email address  
	msg['To'] = ", ".join(toaddr)
	#print msg['To']
	  
	# storing the subject  
	msg['Subject'] = "Daily MIS = " + ((date.today() - timedelta(days=1))).strftime("%B %d, %Y")
	  
	# string to store the body of the mail 
		# string to store the body of the mail 
		#body = ""

	html = """\
		<html>
			<table border='5'>
			<thead>
			<tr>
			<th style="text-align: center;" bgcolor="Yellow"><strong>Type</strong></th>
			<th style="text-align: center;" bgcolor="Yellow"><strong>Date</strong></th>
			<th style="text-align: center;" bgcolor="Yellow"><strong>Day</strong></th>
			<th style="text-align: center;" bgcolor="Yellow"><strong>Spends</strong></th>
			<th style="text-align: center;" bgcolor="Yellow"><strong>Applications</strong></th>
			<th style="text-align: center;" bgcolor="Yellow"><strong>Disbursals</strong></th>
			<th style="text-align: center;" bgcolor="Yellow"><strong>Disbursals (Cr.)</strong></th>
			<th style="text-align: center;" bgcolor="silver"><strong>ATS</strong></th>
			<th style="text-align: center;" bgcolor="silver"><strong>CPA</strong></th>
			<th style="text-align: center;" bgcolor="silver"><strong>CPD</strong></th>
			<th style="text-align: center;" bgcolor="silver"><strong>A-D%</strong></th>
			<th style="text-align: center;" bgcolor="silver"><strong>COA</strong></th>
			</tr>
			</thead>
			<tbody>
			<tr>
			<td>Organic</td>
			<td>{}</td>
			<td>{}</td>
			<td style="text-align: right;">&nbsp;</td>
			<td style="text-align: right;">{:,}</td>
			<td style="text-align: right;">{:,}</td>
			<td style="text-align: right;">{:,}</td>
			<td>&nbsp;</td>
			<td>&nbsp;</td>
			<td>&nbsp;</td>
			<td>&nbsp;</td>
			<td>&nbsp;</td>
			</tr>
			<tr>
			<td>Inorganic</td>
			<td>{}</td>
			<td>{}</td>
			<td style="text-align: right;">&nbsp;</td>
			<td style="text-align: right;">{:,}</td>
			<td style="text-align: right;">{:,}</td>
			<td style="text-align: right;">{:,}</td>
			<td>&nbsp;</td>
			<td>&nbsp;</td>
			<td>&nbsp;</td>
			<td>&nbsp;</td>
			<td>&nbsp;</td>
			</tr>
			<tr>
			<td><strong>Total</strong></td>
			<td><strong>{}</strong></td>
			<td><strong>{}</strong></td>
			<td style="text-align: right;"><strong>{:,}</strong></td>
			<td style="text-align: right;"><strong>{:,}</strong></td>
			<td style="text-align: right;"><strong>{:,}</strong></td>
			<td style="text-align: right;"><strong>{}</strong></td>
			<td style="text-align: center;"><strong>{:,}</strong></td>
			<td style="text-align: center;"><strong>{}</strong></td>
			<td style="text-align: center;"><strong>{}</strong></td>
			<td style="text-align: center;"><strong>{}%</strong></td>
			<td style="text-align: center;"><strong>{}%</strong></td>
			</tr>
			</tbody>
			</table>
			<br/>
			<br/>
		</html>
	""".format(dd_date,yesterday_day,app_organic,disbursal_organic,disbursal_amt_organic,dd_date,yesterday_day,app_inorg,disbursal_inorg,disbursal_amt_inorg,dd_date,yesterday_day,total_spends,total_app,total_disbursal,total_disbursal_amount,ATS,CPA,CPD,A_D_percnt,COA)
			  
	html_str = html_str + html

	# attach the body with the msg instance 
	msg.attach(MIMEText(html_str, 'html')) 


	# creates SMTP session 
	s = smtplib.SMTP('smtp.gmail.com', 587)

	# start TLS for security 
	s.starttls() 

	# Authentication 
	s.login(fromaddr, "Mumbai@82") 

	# Converts the Multipart msg into a string 
	text = msg.as_string()

	#print (text)
	html_to_df = pd.read_html(html_str)[index]
	df_html = df_html.append(html_to_df)

	counter =  counter - 1
	index = index + 1


#from IPython.display import display_html
#tab.to_excel('output1.xlsx',sheet_name='Sheet_name_1', index=False)

writer = pd.ExcelWriter("mis_data_1.xlsx", engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df_html.to_excel(writer, sheet_name='Sheet1', index=False)

workbook  = writer.book
worksheet = writer.sheets['Sheet1']

"""
cell_format_3 = workbook.add_format()
cell_format_3.set_border(1)
cell_format_3.set_bold()
cell_format_3.set_bg_color('yellow')

worksheet.set_row(3, 12, cell_format_3)
worksheet.set_row(6, 12, cell_format_3)
worksheet.set_row(9, 12, cell_format_3)
"""
header_format = workbook.add_format({
    'bold': True,
    'text_wrap': True,
    'valign': 'top',
    'bg_color': 'yellow',
    'border': 1})

format1 = workbook.add_format({'num_format': '#,##0'})
format1.set_border(1)


cell_format_1 = workbook.add_format()
cell_format_1.set_border(1)
cell_format_1.set_bold()
cell_format_1.set_align('center')

# Add some cell formats.
cell_format_2 = workbook.add_format()
cell_format_2.set_border(1)

worksheet.set_column('A:C', 12, cell_format_1)
worksheet.set_column('D:F', 12, format1)
worksheet.set_column('G:G', 16, cell_format_2)
worksheet.set_column('H:J', 12, format1)
worksheet.set_column('K:L', 12, cell_format_2)

#### Light yellow

cell_format_3 = workbook.add_format()
cell_format_3.set_border(2)
cell_format_3.set_bold()
cell_format_3.set_bg_color('#FFFF66')

#### Gold color
cell_format_4 = workbook.add_format()
cell_format_4.set_border(2)
cell_format_4.set_bold()
cell_format_4.set_bg_color('#FFD700')

#### Silver  color
cell_format_5 = workbook.add_format()
cell_format_5.set_border(2)
cell_format_5.set_bold()
cell_format_5.set_bg_color('#C0C0C0')

#### Light Grey color
cell_format_6 = workbook.add_format()
cell_format_6.set_border(2)
cell_format_6.set_bold()
cell_format_6.set_bg_color('#D3D3D3')


if (day != 'Mon'):
	worksheet.conditional_format('A1:G1', {'type': 'no_blanks', 'format': cell_format_4})
	worksheet.conditional_format('H1:L1', {'type': 'no_blanks', 'format': cell_format_5})
	worksheet.conditional_format('A4:G4', {'type': 'no_blanks', 'format': cell_format_3})
	worksheet.conditional_format('H4:L4', {'type': 'no_blanks', 'format': cell_format_6})

else:
	worksheet.conditional_format('A1:G1', {'type': 'no_blanks', 'format': cell_format_4})
	worksheet.conditional_format('H1:L1', {'type': 'no_blanks', 'format': cell_format_5})
	worksheet.conditional_format('A4:G4', {'type': 'no_blanks', 'format': cell_format_3})
	worksheet.conditional_format('H4:L4', {'type': 'no_blanks', 'format': cell_format_6})
	worksheet.conditional_format('A7:G7', {'type': 'no_blanks', 'format': cell_format_3})
	worksheet.conditional_format('H7:L7', {'type': 'no_blanks', 'format': cell_format_6})
	worksheet.conditional_format('A10:G10', {'type': 'no_blanks', 'format': cell_format_3})
	worksheet.conditional_format('H10:L10', {'type': 'no_blanks', 'format': cell_format_6})

writer.save()

# sending the mail 
#s.sendmail(fromaddr, toaddr, text) 

# terminating the session 
s.quit()

