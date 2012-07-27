TODO
----

1. Cache management (player and items):
	* Implement seperate function that checks if either or both is in cache. [x]
	* Modify cache reader/writer to accept a folder depending on item or player response [x]
2. Responses:
	* Seperate item and player responses. [x]
	* Write player response always, except in case of empty response. [x]
	* Write item response only when backpack contains items. [x]
3. Parsing:
	* Write seperate parse functions and a new function that joins the parsed responses. [-]
4. Item, property, and player info name replacement:
	* Write function that takes in joined (see no. 3) parsed response and returns it with modified names. [-]
5. Templates:
	* Add Bootstrap well above backpack results to show player data. [x]
