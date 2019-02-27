#encoding:utf-8
import database.mysql_operation
import random
import fake_name
import fake_phone
#mysql_conn = database.mysql_operation.MysqlConn("10.245.146.146","root","315e2664db","drug_sys","utf8")
mysql_conn = database.mysql_operation.MysqlConn("0.0.0.0","root","","drug_sys","utf8")

'''
该程序用于生产随机进货订单、售出订单
以及批量生成顾客姓名电话等
并将上述内容添加到数据库中
'''

#print drug_ids
def make_fake_datetime():
	year,month,day = str(random.randint(14,18)),str(random.randint(1,12)),str(random.randint(1,28))
	h,m,s = str(random.randint(8,20)),str(random.randint(0,59)),str(random.randint(0,59))
	if len(month)==1:	month = '0' + month
	if len(day)==1:	day = '0' + day
	if len(h)==1:	h = '0' + h
	if len(m)==1:	m = '0' + m
	if len(s)==1:	s = '0' + s
	time = str(year)+str(month)+str(day)+str(h)+str(m)+str(s)
	return time


def make_fake_customer():
	for i in range(100,200):
		name = fake_name.get_fake_name()
		phone = fake_phone.get_fake_phone()
		sex=""

		if i%2==0:
			sex="男"
		else:
	 		sex="女"
	 	custom_age = random.randint(10,60)
		mysql_conn.exec_readsql("insert into custom_info(custom_id,custom_name,custom_sex,custom_tel,custom_age) values('%s','%s','%s','%s','%s')"%(i,name,sex,phone,custom_age))
	mysql_conn.commit()

def make_fake_transaction():
	drug_ids = []
	for i in mysql_conn.exec_readsql("select distinct drug_id,transaction_date,single_price from purchase_info "):
		drug_ids.append((i[0],i[1],i[2]))
	#print str(drug_ids[0][1])
	for i in range(1000000,1002000):
		time = make_fake_datetime()
		drug_id = drug_ids[random.randint(0,len(drug_ids)-1)]
		drug_amount = random.randint(1,8)
		customer_id = random.randint(101,199)
		sql = "insert into transaction_list(transaction_id,transaction_time,drug_id,drug_amount,customer_id,single_price)\
				values('%s','%s','%s','%s','%s',1.5*%f)"%(i,time,drug_id[0],drug_amount,customer_id,drug_id[2])
		mysql_conn.exec_cudsql(sql)
	mysql_conn.commit()

def make_fake_purchase():
	drug_ids = []
	for i in mysql_conn.exec_readsql("select distinct drug_id from drug_info"):
		drug_ids.append(i[0])
	for i in range(10000,10200):
		purchase_time = make_fake_datetime()
		drug_id = drug_ids[random.randint(0,len(drug_ids)-1)]
		drug_amount = random.randint(30,100)
		production_time = make_fake_datetime()
		while production_time >= purchase_time :
			production_time = make_fake_datetime()
		single_price = random.randint(10,30)
		sql = " insert into purchase_info(transaction_id,transaction_date,\
				drug_id,amount,production_date,single_price) values\
				('%s','%s','%s','%s','%s','%s');"%(i,purchase_time,drug_id,drug_amount,production_time,single_price)
		mysql_conn.exec_cudsql(sql)
	mysql_conn.commit()

def keep_updating():
	sql = "insert into custom_info(custom_id,custom_name,custom_sex,custom_tel) values"

def delete_database_and_flee():
	mysql_conn.exec_cudsql("DELETE FROM purchase_info;")
	mysql_conn.exec_cudsql("DELETE FROM transaction_list;")
	mysql_conn.exec_cudsql("DELETE FROM custom_info;")
	mysql_conn.exec_cudsql("UPDATE drug_info SET stock=0;")
	mysql_conn.commit()

if __name__ == "__main__":
	delete_database_and_flee()
	make_fake_customer()
	make_fake_purchase()
	make_fake_transaction()
	mysql_conn.close_db()
