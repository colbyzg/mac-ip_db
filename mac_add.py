#! /usr/bin/python
import sys
import re
import MySQLdb as mdb
import paramiko
import time
import creds

# Set global variables here
devices = ["192.168.25.1",]
commands = ["show mac add", "sh mac-add", "sh ip arp",]
username = creds.username
password = creds.password
enable_pw = creds.enable_pw
pager = "terminal length 0"

# Match anything at beginning of line up to #.
regex_name_1 = "^(.*?)\#"
# Match anything surrounded by #.
regex_name_2 = "#.+#"
regex_ip = "(?:[0-9]{1,3}\.){3}[0-9]{1,3}\/[0-3][0-9]|(?:[0-9]{1,3}\.){3}[0-9]{1,3}"
regex_vlan = "[0-9]+"
regex_mac = "([0-9A-Fa-f]){4}\.([0-9A-Fa-f]){4}\.([0-9A-Fa-f]){4}"
regex_switchport = "(Gi|Fa|Eth|Te)[0-9]+\/[0-9]+\/[0-9]+|(Gi|Fa|Eth|Te)[0-9]+\/[0-9]+"

con = mdb.connect('localhost', creds.network_db_user, creds.network_db_pw, 'network');
cur = con.cursor(mdb.cursors.DictCursor)


def main():
	for device in devices:
		conn_pre = paramiko.SSHClient()
		conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		conn_pre.connect(device, username=username, password=password)
		time.sleep(1)
		conn = conn_pre.invoke_shell()
		time.sleep(1)
		if conn:
			if ">" in conn.recv(100000):
				enable(conn, enable_pw)
				time.sleep(1)
			conn.send(pager + "\r")
			time.sleep(1)
			out_file = open(device + ".out", "w")
			out_file.close()
			for cmd in commands:
				try:
					conn.send(cmd + "\r")
					time.sleep(3)
					output = conn.recv(100000)
					with open(device + ".out", "a") as file:
						file.writelines(output)
				except:
					continue
			conn.send("exit\r")
			create_tables(device)
		else:
			continue

def enable(conn, enable_pw):
	conn.send("enable\r")
	time.sleep(1)
	conn.send(enable_pw + "\r")
	time.sleep(1)

def create_tables(device):
	list = open(device + ".out", "r").readlines()
	for line in list:
		if "#" in line:
			match = re.search(regex_name_1, line)
			name = match.group()
		if "DYNAMIC" in line:
			mac_table.append(line + " " + device + " #" + name)
		elif "ARPA" in line:
			arp_table.append(line)

def mac_db():
	cur.execute("DROP TABLE IF EXISTS MAC_Table")
	cur.execute("CREATE TABLE MAC_Table(Id INT PRIMARY KEY AUTO_INCREMENT, \
					Switch VARCHAR(50), \
					Switch_IP VARCHAR(50), \
					Port VARCHAR(10), \
					VLAN VARCHAR(50), \
					Node_MAC VARCHAR(200))")
	
	for line in mac_table:
		match = re.sub("\\r\\n|DYNAMIC", "", line)
		match = re.sub("\s{2,}", " ", match)
		match = re.sub("^\s", "", match)
		clean_list.append(match)

	for line in clean_list:
		try:
			switch_name = re.search(regex_name_2, line)
			switch_name = switch_name.group()
			switch_name = re.sub("#", "", switch_name)
			switchport = re.search(regex_switchport, line)
			switchport = switchport.group()
			mac = re.search(regex_mac, line)
			mac = mac.group()
			vlan = re.search(regex_vlan, line)
			vlan = vlan.group()
			switch_ip = re.search(regex_ip, line)
			switch_ip = switch_ip.group()
		except Exception as e:
			print(e)
			pass
		with con:
			sql_cmd = "INSERT INTO MAC_Table(Switch, Switch_IP, Port, VLAN, Node_MAC) VALUES('{}', '{}', '{}', '{}', '{}')".format(switch_name, switch_ip, switchport, vlan, mac)
			cur.execute(sql_cmd)

def arp_db():
	cur.execute("DROP TABLE IF EXISTS ARP_Table")
	cur.execute("CREATE TABLE ARP_Table(Id INT PRIMARY KEY AUTO_INCREMENT, \
					Node_IP VARCHAR(50), \
					Node_MAC VARCHAR(200))")	

	arp_list = []
	for line in arp_table:
		match = re.sub("\\r\\n|DYNAMIC|ARPA|Internet", "", line)
		match = re.sub("\s{2,}", " ", match)
		match = re.sub("^\s", "", match)
		arp_list.append(match)
	
	for line in arp_list:
		try:
			node_ip = re.search(regex_ip, line)
			node_ip = node_ip.group()
			mac = re.search(regex_mac, line)
			mac = mac.group()
		except Exception as e:
			pass
		with con:
			sql_cmd = "INSERT INTO ARP_Table(Node_IP, Node_MAC) VALUES('{}', '{}')".format(node_ip, mac)
			cur.execute(sql_cmd)


if __name__ == "__main__":
	mac_table = []
	arp_table = []
	clean_list = []
	main()
	mac_db()
	arp_db()
	print("\nTasks completed successfully!\n")
