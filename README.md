mac-ip_db
======

# Description:
These scripts populate a MySQL database using MAC and ARP tables from various hosts.

The mac_add.py script pulls info from a list of devices, parses the output, and pushes the relevant information into the database.

The search_mac.py script takes an IP address from the user and outputs which switch and port the MAC is connected to.

# Usage:
<pre>
# ./mac_add.py 

Tasks completed successfully!
</pre>

<pre>
# ./search_mac.py 192.168.25.20
+--------------+--------------+------+-------+---------------+----------------+
| Switch Name  |  Switch IP   | VLAN |  Port |   Device IP   |   Device MAC   |
+--------------+--------------+------+-------+---------------+----------------+
| home-core-01 | 192.168.25.1 |  25  | Gi0/9 | 192.168.25.20 | 0050.56b2.5a83 |
+--------------+--------------+------+-------+---------------+----------------+
</pre>