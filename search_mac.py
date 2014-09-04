#! /usr/bin/python

import MySQLdb as mdb
import prettytable
import sys
import creds

def main():
	try:
		ip = sys.argv[1]
	except IndexError:
		ip = raw_input("\nWhich IP address are you interested in? ")
	
	con = mdb.connect('localhost', creds.network_db_user, creds.network_db_pw, 'network');
	cur = con.cursor(mdb.cursors.DictCursor)
	
	sql_arp = "SELECT * FROM ARP_Table Where Node_IP='%s'" % ip
	cur.execute(sql_arp)
	arp_entry = cur.fetchall()
	
	mac = arp_entry[0]["Node_MAC"]
	
	sql_mac = "SELECT * FROM MAC_Table Where Node_MAC='%s' ORDER BY Switch, Port" % mac
	
	cur.execute(sql_mac)
	mac_entry = cur.fetchall()

	if mac_entry:
		tab = prettytable.PrettyTable(["Switch Name", "Switch IP", "VLAN", "Port", "Device IP", "Device MAC"])
		for entry in mac_entry:
			tab.add_row([entry["Switch"], entry["Switch_IP"], entry["VLAN"], entry["Port"], ip, entry["Node_MAC"]])
	
		print(tab)
		print("\n")
	else:
		print("\nNo information found for that IP Address. Exiting...\n")	

if __name__ == "__main__":
	try:
		main()
	except IndexError:
		print("\nIP Address not found in database. Exiting...\n")