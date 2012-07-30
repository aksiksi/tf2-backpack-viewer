TODO
----

[x] = Done
[-] = Not necessary
[+] = In progress

1. Cache management (player and items):
	* Implement seperate function that checks if either or both is in cache. [x]
	* Modify cache reader/writer to accept a folder depending on item or player response [x]
2. Responses:
	* Seperate item and player responses. [x]
	* Write player response always, except in case of empty response. [x]
	* Write item response only when backpack contains items. [x]
 	* Modification: never write player responses; always grab new response on request. [x]
3. Parsing:
	* Write seperate parse functions and a new function that joins the parsed responses. [-]
4. Item, property, and player info name replacement:
	* Write function that takes in joined (see no. 3) parsed response and returns it with modified names. [x]
 	* Modification: write set of functions that modify the schema itself instead of replacing names on every request. [+]
5. Templates:
	* Add Bootstrap "well" above backpack results to show player data. [x]
	* Add table sorting mechanism. [x]
 	* Look for simply JS library for info on hover to return results as boxes instead of a table.
  	* Implement template inheritance.
6. Database:
	* Re-implement database methods using MySQLdb library. [+]
	* Configure it to write necessary item and player data to seperate DBs. [+]