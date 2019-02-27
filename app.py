#encoding:utf-8
from flask import Flask, request, redirect, render_template, flash
import database.mysql_operation
import make_render
import os
#mysql_conn = database.mysql_operation.MysqlConn('10.245.146.146','root','315e2664db','drug_sys','utf8')
mysql_conn = database.mysql_operation.MysqlConn('0.0.0.0','root','','drug_sys','utf8')

app = Flask(__name__)

'''
-------------------------------------------------------
-------------------------------------------------------
登录界面
'''
level = 100

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('new_login.html')

@app.route('/signin', methods=['POST'])
def signin():
	import md5
	username = request.form['username']
	password = request.form['password']
	global level
	if username=='guest':		
		level = 1
	elif username=='employee':
		level = 10
	elif username=='boss':
		level = 100
	#根据不同的登录账户，决定当前系统的权限
	m = md5.new()
	m.update(password)
	password = m.hexdigest()
	sql = "select * from login where username='%s' and md5_pwd='%s'"%(username,password)
	#将用户的密码HASH值与数据库中的HASH值比对，若HASH相同则登陆成功
	res = mysql_conn.exec_readsql(sql)
	if res:
		return render_template('searchbox.html', level=level)
	return render_template('new_login.html', message='Bad username or password', username=username)

'''
-------------------------------------------------------
-------------------------------------------------------
'''


'''
-------------------------------------------------------
-------------------------------------------------------
添加新药品
'''
@app.route('/add_drug',methods=['GET'])
def add_drug_form():
	global level
	if level>2:
		return render_template('add_drug_form.html')
	else:
		return "您无权进行此操作"

@app.route('/add_drug',methods=['POST'])
def add_drug():
	drug_id     = request.form['drug_id']
	drug_name   = request.form['drug_name']
	drug_size   = request.form['drug_size']
	supplier_id = request.form['supplier_id']
	shelf_life  = request.form['shelf_life']
	sql = "insert into drug_info(drug_id,drug_name,drug_size,supplier_id,shelf_life)\
			values('%s','%s','%s','%s','%s');"%(drug_id,drug_name,drug_size,supplier_id,shelf_life)
	res = mysql_conn.exec_cudsql(sql)
	mysql_conn.commit()
	if res:
		return render_template('searchbox.html')
	else:
		return "操作失败，插入需满足国药准字唯一PRIMARY KEY 以及供应商编号FOREIGN KEY约束"
'''
-------------------------------------------------------
-------------------------------------------------------
'''

'''
-------------------------------------------------------
-------------------------------------------------------
修改药品
'''
@app.route('/update_drug',methods=['GET','POST'])
def udpate_drug_from():
	drug_id=request.args.get('drug_id')
	drug_name=request.args.get('drug_name')
	drug_size=request.args.get('drug_size')
	shelf_life=request.args.get('shelf_life')
	result=[drug_id,drug_name,drug_size,shelf_life]
	global level
	if level>2:
		return render_template('update_form.html',info=result,content="update_drug")
	else:
		return "您无权进行此操作"


@app.route('/update_drug_change',methods=['GET','POST'])
def update_drug():
	drug_id=request.form['drug_id']
	drug_name=request.form['drug_name']
	drug_size=request.form['drug_size']
	shelf_life=request.form['shelf_life']
	sql = "update drug_info set drug_name='%s',drug_size='%s'\
			,shelf_life='%s' where drug_id='%s'"%(drug_name,drug_size,shelf_life,drug_id)
	res = mysql_conn.exec_cudsql(sql)
	mysql_conn.commit()
	return render_template('searchbox.html')

'''
-------------------------------------------------------
-------------------------------------------------------
'''

'''
-------------------------------------------------------
-------------------------------------------------------
删除药品
'''
@app.route('/remove_drug',methods=['POST','GET'])
def remove_drug():
	drug_id = request.args.get('drug_id')
	sql = "delete from drug_info where drug_id='%s'"%drug_id
	mysql_conn.exec_cudsql(sql)
	global level
	if level>2:
		return render_template('searchbox.html')
	else:
		return "您无权进行此操作"

'''
-------------------------------------------------------
-------------------------------------------------------
综合查询模块
'''
@app.route('/query_all',methods=['GET'])
def query_all_box():
	return render_template('searchbox.html')

@app.route('/query_all',methods=['POST'])
def query_all():
	choice = request.form['choices-single-defaul']
	text = request.form['text']
	print choice,type(choice)
	choice = choice.encode("utf-8")
	text = text.encode("utf-8")
	print choice,type(choice)
	if choice=="药品":
		if text.isdigit():
			#若输入为数字，则先先按国药准字精确查询
			sql = " select drug_id,drug_name,drug_size,drug_info.supplier_id,supplier_name,shelf_life,stock \
				from drug_info,supplier_info where drug_info.supplier_id=supplier_info.supplier_id\
				and drug_id='%s'"%text
			res = mysql_conn.exec_readsql(sql)
			if not res:
				#若输入不是国药准字，则按照生产厂家许可证号精确查询药品
				sql = " select drug_id,drug_name,drug_size,drug_info.supplier_id,supplier_name,shelf_life,stock \
				from drug_info,supplier_info where drug_info.supplier_id=supplier_info.supplier_id\
				and drug_info.supplier_id='%s'"%text
				print sql
				res = mysql_conn.exec_readsql(sql)
			if res:
				return render_template('show_table.html', result=res, content="drug")

		else:
			#若输入不是数字，则先按药品名模糊查询
			sql = " select drug_id,drug_name,drug_size,drug_info.supplier_id,supplier_name,shelf_life,stock \
				from drug_info,supplier_info where drug_info.supplier_id=supplier_info.supplier_id\
				and drug_name like '%%%s%%'"%text
			res = mysql_conn.exec_readsql(sql)
			if not res:
				#若输入不是数字，则先按生产厂家名模糊查询
				sql = " select drug_id,drug_name,drug_size,drug_info.supplier_id,supplier_name,shelf_life,stock \
				from drug_info,supplier_info where drug_info.supplier_id=supplier_info.supplier_id\
				and supplier_name like '%%%s%%'"%text
				print sql
				res = mysql_conn.exec_readsql(sql)
			if res:
				return render_template('show_table.html', result=res, content="drug")

	if choice=="顾客":
		global level
		if level<11:
			return "您无权进行此操作"
		if text.isdigit():
			if len(text)==11:
				sql = "select * from custom_info where custom_tel='%s'"%text
				res = mysql_conn.exec_readsql(sql)
				if res:
					return render_template("show_table.html",result=res, content="custom")
			else:
				sql = "select * from custom_info where custom_id='%s'"%text
				res = mysql_conn.exec_readsql(sql)
				if res:
					return render_template("show_table.html",result=res, content="custom")
		else:
			sql = "select * from custom_info where custom_name like '%%%s%%'"%text
			res = mysql_conn.exec_readsql(sql)
			print sql
			print res
			if res:
				return render_template("show_table.html",result=res, content="custom")
		return render_template("show_table.html",result=[], content="custom")

	elif choice=="供应商":
		if text.isdigit():
			return redirect('/query_supplier/'+text)
		else:
			sql = " select supplier_id,address,supplier_name,boss_name,tel \
				from supplier_info where supplier_name like '%%%s%%'"%text
			res = mysql_conn.exec_readsql(sql)
			return render_template("show_table.html",result=res, content="supplier")

	elif choice=="售出":
		global level
		if level<2:
			return "您无权进行此操作"
		if text.isdigit():
			if len(text)==7:
				#优先按订单号查询
				sql = "select transaction_id,transaction_time,drug_name,drug_amount,custom_name,\
				single_price*drug_amount,drug_info.drug_id from transaction_list,drug_info,custom_info where\
				drug_amount>0 and  drug_info.drug_id=transaction_list.drug_id and \
				transaction_list.customer_id=custom_info.custom_id and transaction_id=%s\
				order by transaction_time desc"%text
				res = mysql_conn.exec_readsql(sql)

			if len(text)==8: text = text[2:]
			#将8位日期统一为6位
			if len(text)==6:
				#按照6位日期查询
				sql = "select transaction_id,transaction_time,drug_name,drug_amount,custom_name,\
				single_price*drug_amount,drug_info.drug_id from transaction_list,drug_info,custom_info where\
				drug_amount>0 and  drug_info.drug_id=transaction_list.drug_id and \
				transaction_list.customer_id=custom_info.custom_id and transaction_time>='%s'\
				 and transaction_time<='%s' order by transaction_time desc"%(text+'0000',text+'2359')
				print sql
				res = mysql_conn.exec_readsql(sql)

		elif ' ' in text and text.split(' ')[0].isdigit():
			a,b = text.split(' ')
			a,b = a[2:],b[2:]
			#查询一个时间段内交易流水
			if a.isdigit() and b.isdigit():
				sql = "select transaction_id,transaction_time,drug_name,drug_amount,custom_name,\
					single_price*drug_amount,drug_info.drug_id from transaction_list,drug_info,custom_info where\
					drug_amount>0 and  drug_info.drug_id=transaction_list.drug_id and \
					transaction_list.customer_id=custom_info.custom_id and transaction_time>'%s'\
					and transaction_time<'%s' order by transaction_time desc"%(str(int(a))+'0000',str(int(b))+'2359')
				print sql
				res = mysql_conn.exec_readsql(sql)


		else:
			sql = "select transaction_id,transaction_time,drug_name,drug_amount,custom_name,\
				single_price*drug_amount,drug_info.drug_id from transaction_list,drug_info,custom_info where\
				drug_amount>0 and  drug_info.drug_id=transaction_list.drug_id and \
				drug_name like '%%%s%%' and transaction_list.customer_id=custom_info.custom_id\
				order by transaction_time desc"%text
			res = mysql_conn.exec_readsql(sql)
			if not res:
				sql = "select transaction_id,transaction_time,drug_name,drug_amount,custom_name,\
				single_price*drug_amount,drug_info.drug_id from transaction_list,drug_info,custom_info where\
				drug_amount>0 and  drug_info.drug_id=transaction_list.drug_id and \
				custom_name like '%%%s%%' and transaction_list.customer_id=custom_info.custom_id\
				order by transaction_time desc"%text
				res = mysql_conn.exec_readsql(sql)
		count,acc = 0,0
		if res:
			for i in res:
				count += int(i[3])
				acc+=int(i[-2])
		with open ('/Users/chentianyi/mycode/mypython/db/static/download/query_res.csv','w') as f:
			f.writelines('售出订单号,交易日期,药品名称,药品数量,顾客姓名,交易金额\n')
			for i in res:
				f.writelines(str(i[0])+','+str(i[1])+','+str(i[2].encode('utf-8'))+','+str(i[3])+','+str(i[4].encode('utf-8'))+','+str(i[5])+'\n')
		#print sql
		return render_template('show_table.html', info=(count,acc) ,result=res, content="transaction")

	elif choice=="退货":
		global level
		if level<2:
			return "您无权进行此操作"
		if text.isdigit():
			if len(text)==7:
				sql = "select transaction_id,transaction_time,drug_name,drug_amount,custom_name,\
				single_price*drug_amount,note from transaction_list,drug_info,custom_info where\
				drug_amount<0 and  drug_info.drug_id=transaction_list.drug_id and \
				transaction_list.customer_id=custom_info.custom_id and transaction_id=%s"%text
				res = mysql_conn.exec_readsql(sql)

			if len(text)==6 or len(text)==8:
				sql = "select transaction_id,transaction_time,drug_name,drug_amount,custom_name,\
				single_price*drug_amount,note from transaction_list,drug_info,custom_info where\
				drug_amount<0 and  drug_info.drug_id=transaction_list.drug_id and \
				transaction_list.customer_id=custom_info.custom_id and transaction_time=%s"%text
				res = mysql_conn.exec_readsql(sql)

		else:
			sql = "select transaction_id,transaction_time,drug_name,drug_amount,custom_name,\
				single_price*drug_amount,note from transaction_list,drug_info,custom_info where\
				drug_amount<0 and  drug_info.drug_id=transaction_list.drug_id and \
				drug_name like '%%%s%%' and transaction_list.customer_id=custom_info.custom_id"%text
			res = mysql_conn.exec_readsql(sql)
			if not res:
				sql = "select transaction_id,transaction_time,drug_name,drug_amount,custom_name,\
				single_price*drug_amount,note from transaction_list,drug_info,custom_info where\
				drug_amount<0 and  drug_info.drug_id=transaction_list.drug_id and \
				custom_name like '%%%s%%' and transaction_list.customer_id=custom_info.custom_id"%text
				res = mysql_conn.exec_readsql(sql)
		print sql
		return render_template('show_table.html', result=res, content="refund")

	elif choice=="进货记录":
		global level
		if level<2:
			return "您无权进行此操作"
		sql = "select transaction_id,drug_name,amount,supplier_name,production_date,single_price\
				,drug_info.drug_id from purchase_info,drug_info,supplier_info\
				where purchase_info.drug_id=drug_info.drug_id and drug_info.supplier_id=supplier_info.supplier_id\
				and drug_name like '%%%s%%' order by production_date desc"%text
		print sql 
		res = mysql_conn.exec_readsql(sql)
		if not res:
			sql = "select transaction_id,drug_name,amount,supplier_name,production_date,single_price\
				,drug_info.drug_id from purchase_info,drug_info,supplier_info\
				where purchase_info.drug_id=drug_info.drug_id and drug_info.supplier_id=supplier_info.supplier_id\
				and supplier_name like '%%%s%%' order by production_date desc "%text
			res = mysql_conn.exec_readsql(sql)
		count,acc = 0,0
		for i in res:
			count += int(i[2])
			acc+=int(i[-2])*int(i[2])
		return render_template("show_table.html", info=(count,acc), result=res, content="purchase")

	return render_template('searchbox.html')
	

	
	

'''
-------------------------------------------------------
-------------------------------------------------------
'''

'''
-------------------------------------------------------
-------------------------------------------------------
查询供应商
'''
@app.route('/query_transactions',methods=['GET'])
def query_transactions():
	sql = "select * from supplier_info where supplier_id = %s"%supplier
	res = mysql_conn.exec_readsql(sql)
	return render_template('show_supplier.html',result = res)
	


@app.route('/query_supplier/<string:supplier>',methods=['GET'])
def query_supplier(supplier):
	sql = "select * from supplier_info where supplier_id = %s"%supplier
	res = mysql_conn.exec_readsql(sql)
	return render_template('show_table.html',result = res, content="supplier")


'''
-------------------------------------------------------
-------------------------------------------------------
'''

'''
-------------------------------------------------------
-------------------------------------------------------
登记进货记录
'''
@app.route('/purchase_reg',methods=['GET'])
def purchase_reg_form():
	return render_template('purchase_reg_form.html')

@app.route('/purchase_reg',methods=['POST'])
def purchase_reg():
	drug_id 		= request.form['drug_id']
	amount 			= request.form['amount']
	production_date = request.form['production_date']
	single_price 	= request.form['single_price']
	total_purchases = int(mysql_conn.exec_readsql("select count(*) from purchase_info;")[0][0])
	transaction_id  = str(10000+total_purchases)
	sql = "insert into purchase_info(transaction_id,drug_id,amount,production_date,single_price)\
		values('%s','%s','%s','%s','%s');"%(transaction_id,drug_id,amount,production_date,single_price)
	mysql_conn.exec_cudsql(sql)
	mysql_conn.commit()
	return render_template("searchbox.html")

'''
-------------------------------------------------------
-------------------------------------------------------
'''


'''
-------------------------------------------------------
-------------------------------------------------------
修改进货记录
'''
@app.route('/update_purchase',methods=['GET','POST'])
def udpate_purchase_form():
	transaction_id=request.args.get('transaction_id')
	transaction_time=request.args.get('transaction_time')
	drug_name=request.args.get('drug_name')
	drug_id=request.args.get('drug_id')
	amount = request.args.get('amount')
	production_date=request.args.get('production_date')
	single_price=request.args.get('single_price')
	res = [transaction_id,transaction_time,drug_name,amount,production_date,single_price,drug_id]
	return render_template('update_form.html',info=res,content="update_purchase")


@app.route('/update_purchase_change',methods=['GET','POST'])
def update_purchase():
	transaction_id = request.form['transaction_id']
	drug_id=request.form['drug_id']
	amount=request.form['amount']
	production_date=request.form['production_date']
	single_price = request.form['single_price']
	sql = "update purchase_info set drug_id='%s',amount='%s'\
			,production_date='%s', single_price='%s' \
			where transaction_id='%s';"%(drug_id,amount,production_date,single_price,transaction_id)
	res = mysql_conn.exec_cudsql(sql)
	buy_in = mysql_conn.exec_readsql("select sum(amount) from purchase_info where drug_id='%s';"%drug_id)
	sell_out = mysql_conn.exec_readsql("select sum(drug_amount) from transaction_list where drug_id='%s';"%drug_id)
	stock = int(buy_in[0][0])-int(sell_out[0][0])
	mysql_conn.exec_cudsql("update drug_info set stock=%s where drug_id='%s'"%(stock,drug_id))
	mysql_conn.commit()
	return render_template('searchbox.html')

@app.route('/remove_purchase',methods=['GET'])
def remove_purchase():
	transaction_id = request.args.get('transaction_id')
	drug_id = request.args.get('drug_id')
	sql = "delete from purchase_info where transaction_id='%s'"%transaction_id
	mysql_conn.exec_cudsql(sql)
	print drug_id
	buy_in = mysql_conn.exec_readsql("select sum(amount) from purchase_info where drug_id='%s';"%drug_id)
	sell_out = mysql_conn.exec_readsql("select sum(drug_amount) from transaction_list where drug_id='%s';"%drug_id)
	print buy_in
	print sell_out
	stock = int(buy_in[0][0])-int(sell_out[0][0])
	mysql_conn.exec_cudsql("update drug_info set stock=%s where drug_id='%s'"%(stock,drug_id))
	mysql_conn.commit()	
	return render_template('searchbox.html')

'''
-------------------------------------------------------
-------------------------------------------------------
'''


'''
-------------------------------------------------------
-------------------------------------------------------
药品交易流水(B2C)
'''
@app.route('/sell_reg',methods=['GET'])
def sell_reg_form():
	return render_template('sell_reg_form.html')

@app.route('/sell_reg',methods=['POST'])
def sell_reg():
	transaction_time = request.form['transaction_time']
	drug_id 		 = request.form['drug_id']
	drug_amount 	 = request.form['drug_amount']
	customer_id 	 = request.form['customer_id']
	single_price 	 = request.form['single_price']
	total_sells  = int(mysql_conn.exec_readsql("select count(*) from transaction_list;")[0][0])
	total_stock  = int(mysql_conn.exec_readsql("select stock from drug_info where drug_id='%s'"%drug_id)[0][0])
	print drug_amount,total_stock
	if int(drug_amount)>int(total_stock):
		return "库存不足！无法售出"
	transaction_id   = str(1000100+total_sells)
	sql = "insert into transaction_list(transaction_id,transaction_time,\
			drug_id,drug_amount,customer_id,single_price)\
			values('%s','%s','%s','%d','%s','%f');"%(
												transaction_id,transaction_time,drug_id,
												int(drug_amount),customer_id,float(single_price))
	mysql_conn.exec_cudsql(sql)
	mysql_conn.commit()
	return render_template("searchbox.html")

@app.route('/update_sell',methods=['GET','POST'])
def udpate_sell_form():
	transaction_id=request.args.get('transaction_id')
	transaction_time=request.args.get('transaction_time')
	drug_name=request.args.get('drug_name')
	drug_id=request.args.get('drug_id')
	drug_amount=request.args.get('drug_amount')
	custom_name=request.args.get('custom_name')
	total_price=request.args.get('total_price')
	single_price=float(str(total_price.encode('utf-8')))/float(str(drug_amount.encode('utf-8')))
	res = [transaction_id,transaction_time,drug_name,drug_id,drug_amount,custom_name,single_price]
	return render_template('update_form.html',info=res,content="update_sell")

@app.route('/update_sell_change',methods=['GET','POST'])
def update_sell():
	transaction_id = request.form['transaction_id']
	transaction_time=request.form['transaction_time']
	drug_id=request.form['drug_id']
	drug_amount=request.form['drug_amount']
	custom_name=request.form['custom_name']
	single_price = request.form['single_price']
	sql = "update transaction_list set transaction_time='%s',drug_id='%s',drug_amount='%s'\
			,single_price='%s' \
			where transaction_id='%s'"%(transaction_time,drug_id,drug_amount,single_price,transaction_id)
	res = mysql_conn.exec_cudsql(sql)
	buy_in = mysql_conn.exec_readsql("select sum(amount) from purchase_info where drug_id='%s';"%drug_id)
	sell_out = mysql_conn.exec_readsql("select sum(drug_amount) from transaction_list where drug_id='%s';"%drug_id)
	stock = int(buy_in[0][0])-int(sell_out[0][0])
	mysql_conn.exec_cudsql("update drug_info set stock=%s where drug_id='%s'"%(stock,drug_id))
	mysql_conn.commit()

	return render_template('searchbox.html')

@app.route('/remove_sell',methods=['GET'])
def remove_sell():
	transaction_id = request.args.get('transaction_id')
	drug_id = request.args.get('drug_id')
	sql = "delete from transaction_list where transaction_id='%s'"%transaction_id
	res = mysql_conn.exec_cudsql(sql)
	buy_in = mysql_conn.exec_readsql("select sum(amount) from purchase_info where drug_id='%s';"%drug_id)
	sell_out = mysql_conn.exec_readsql("select sum(drug_amount) from transaction_list where drug_id='%s';"%drug_id)
	stock = int(buy_in[0][0])-int(sell_out[0][0])
	mysql_conn.exec_cudsql("update drug_info set stock=%s where drug_id='%s'"%(stock,drug_id))
	mysql_conn.commit()
	return render_template('searchbox.html')
'''
-------------------------------------------------------
-------------------------------------------------------
'''


'''
-------------------------------------------------------
-------------------------------------------------------
顾客退货记录（仅退货 or 直接退款)
'''
@app.route('/refund',methods=['GET'])
def refund_form():
	return render_template('refund_form.html')

@app.route('/refund',methods=['POST'])
def refund():
	transaction_time = request.form['transaction_time']
	drug_id 		 = request.form['drug_id']
	drug_amount 	 = request.form['drug_amount']
	customer_id 	 = request.form['customer_id']
	single_price 	 = request.form['single_price']
	note			 = request.form['note']
	total_sells  = int(mysql_conn.exec_readsql("select count(*) from transaction_list;")[0][0])
	transaction_id   = str(9000000+total_sells)
	sql = "insert into transaction_list(transaction_id,transaction_time,drug_id,drug_amount,customer_id,single_price,note)\
		values('%s','%s','%s','%d','%s','%f','%s');"%(
			transaction_id,transaction_time,drug_id,-1*int(drug_amount),customer_id,float(single_price),note)
	mysql_conn.exec_cudsql(sql)
	mysql_conn.commit()
	return render_template("searchbox.html")

'''
-------------------------------------------------------
-------------------------------------------------------
'''


@app.route('/redo',methods=['GET'])
def redo():
	os.system(" python make_fake.py")
	return render_template("searchbox.html")

@app.route('/summit',methods=['GET'])
def summit():
	return render_template("summit.html")

@app.route('/render_drug',methods=['GET'])
def show_render():
	chart = request.args.get('chart')
	if chart=='1':
		make_render.make_pie()
		return render_template("render_drug.html")
	elif chart=='2':
		make_render.make_pie_ii()
		return render_template("render_custom.html")
	elif chart=='3':
		make_render.make_bar()
		return render_template("render_sell.html")
	elif chart=='4':
		make_render.make_bar_ii()
		return render_template("render_purchase.html")
	elif chart=='5':
		make_render.make_top5()
		return render_template("render_top5.html")




if __name__ == '__main__':
    app.run(
    	debug=True,
    	host='0.0.0.0',
    	port = 5000
    	)