#encoding:utf-8
import database.mysql_operation
from pyecharts import Pie,Bar
mysql_conn = database.mysql_operation.MysqlConn("0.0.0.0","root","","drug_sys","utf8")

'''
该程序用于生成统计分析所需要的图标HTML页面
'''
def make_pie():
	drugs = []
	stocks = []

	res = mysql_conn.exec_readsql("select drug_name,stock from drug_info")

	for i in res:
		drugs.append(i[0])
		stocks.append(i[1])
	print drugs



	#pie = Pie("药品库存显示",title_pos='center',width=900)
	pie = Pie("药品库存显示         药品销量显示",title_pos = 'center',width=1000)
	pie.add("",drugs,stocks,center=[25,50],is_random=True,radius=[30,75],legend_orient="vertical",legend_pos="left")
	#pie.add("药品销量情况",drugs,stocks,center=[25,50],is_random=True,radius=[30,75],rosetype='radius')

	drugs = []
	sells = []

	res_2 = mysql_conn.exec_readsql("select drug_name,sum(drug_amount)\
	 	from transaction_list,drug_info where transaction_list.drug_id=drug_info.drug_id\
	 	group by transaction_list.drug_id")

	for i in res_2:
		drugs.append(str(i[0].encode('utf-8')))
		sells.append(str(i[1]))
	for i in drugs:
		print i

	pie.add("药品销量情况",drugs,sells,center=[65,50],is_random=True,radius=[30,75],legend_orient="vertical",legend_pos="right")


	pie.render('./templates/render_drug.html')

def make_pie_ii():
	desc = ['10-20岁','20-30岁','30-40岁','40-50岁','50岁以上']
	ages = [0,0,0,0,0]

	res = mysql_conn.exec_readsql("select custom_age from custom_info")
	for i in res:
		if int(i[0])<20:
			ages[0] += 1
		elif int(i[0])<30:
			ages[1] += 1
		elif int(i[0])<40:
			ages[2] += 1
		elif int(i[0])<50:
			ages[3] += 1
		else:
			ages[4]  += 1

	pie = Pie("购买者年龄结构         单次消费金额",title_pos = 'center',width=1000)
	pie.add("",desc,ages,center=[25,50],is_random=True,radius=[30,75],legend_orient="vertical",legend_pos="left")
	
	desc = ['50元以下','50-100元','100-200元','200-300元','300元以上']
	ages = [0,0,0,0,0]

	res = mysql_conn.exec_readsql("select drug_amount*single_price from transaction_list")
	for i in res:
		if int(i[0])<50:
			ages[0] += 1
		elif int(i[0])<100:
			ages[1] += 1
		elif int(i[0])<200:
			ages[2] += 1
		elif int(i[0])<300:
			ages[3] += 1
		else:
			ages[4]  += 1

	pie.add("",desc,ages,center=[65,50],is_random=True,radius=[30,75],legend_orient="vertical",legend_pos="right")


	pie.render('./templates/render_custom.html')

def make_bar():
	sql = "select DATE_FORMAT(transaction_time,'%Y%m') months,sum(drug_amount*single_price) \
		from transaction_list group by months order by months; "
	res = mysql_conn.exec_readsql(sql)
	months = []
	sells  = []

	for i in res:
		months.append(i[0])
		sells.append(str(i[1]))
	bar = Bar("药品销售")
	bar.add("药品销售额",months,sells,is_stack=True)
	bar.render('./templates/render_sell.html')

def make_bar_ii():
	sql = "select drug_name,max(single_price),min(single_price),avg(single_price)\
		from purchase_info,drug_info where purchase_info.drug_id=drug_info.drug_id\
		group by purchase_info.drug_id"
	res = mysql_conn.exec_readsql(sql)
	drugs,maxs,mins,avgs = [],[],[],[] 
	for i in res:
		drugs.append(i[0])
		maxs.append(str(i[1]))
		mins.append(str(i[2]))
		avgs.append(str(i[3]))
	print drugs

	bar = Bar("药品进价情况",width=1000)
	bar.add("最高进价",drugs,maxs,xaxis_interval=0,xaxis_rotate=10)
	bar.add("平均进价",drugs,avgs,xaxis_interval=0,xaxis_rotate=10)
	bar.add("最低进价",drugs,mins,xaxis_interval=0,xaxis_rotate=10)


	bar.render('./templates/render_purchase.html')

def make_top5():
	sql = "select custom_name,sum(drug_amount*single_price) profit \
	       from transaction_list,custom_info where custom_info.custom_id\
	       =transaction_list.customer_id group by customer_id order by profit desc limit 0,5"
	res = mysql_conn.exec_readsql(sql)
	name,profit=[],[]
	for i in res:
		name.append(i[0])
		profit.append(int(i[1]))
	bar = Bar("消费最多顾客",width=1000)
	bar.add("购买药品总额",name,profit)

	sql = "select sum(drug_amount) profit \
	       from transaction_list,custom_info where custom_info.custom_id\
	       =transaction_list.customer_id group by customer_id order by profit desc limit 0,5"
	res = mysql_conn.exec_readsql(sql)
	total = []
	for i in res:
		total.append(int(i[0]))
	bar.add("购买药品数量",name,total,is_convert=False)

	bar.render('./templates/render_top5.html')

if __name__ == "__main__":
	make_top5()
