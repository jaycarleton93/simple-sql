
import json
import mysql.connector
from mysql.connector import errorcode
import os

from datetime import datetime
import time

#Access logger. Assumes already created in anything that imports this
import logging
logger = logging.getLogger(__name__)


class sqlHelper:

	def __init__(self,username :str, password :str, host :str, port, database=None):
		'''
		Initalize the connection to the SQL database.

		@param username: Name of SQL user to connect with
		@param password: Password for the SQL user to conenct with
		@param host: The host server address
		@param port: The port number to attempt conenction on
		@param database: Optional, database to connect to inside the server. If the database is not specified here, it must be explicity specified in SQL queries/calls
		'''

		self.credentials={
			'username':username,
			'password':password,
			'host':host,
			'port':port
		}
		if database is not None:
			self.credentials['database']=database

		#Connection
		try:
			if database is None:
				self.cnx=mysql.connector.connect(
					user=self.credentials['username'],
					password=self.credentials['password'],
					host=self.credentials['host'],
					port=self.credentials['port']
				)
			else:
				self.cnx=mysql.connector.connect(
					user=self.credentials['username'],
					password=self.credentials['password'],
					host=self.credentials['host'],
					port=self.credentials['port'],
					database=self.credentials['database']
				)
			self.cursor=self.cnx.cursor()
			logger.debug(f"Successfully connected to {host} via MySQL.")

		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR :
				logger.error(f"Something is wrong with your user name or password, when connecting to {host} via MySQL")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				logger.error(f"Could not find {host}")
			else:
				logger.error("ERROR/CONNECTION: Details-> "+str(err))
			exit()


	def query(self,query :str, exit_on_fail=True,retries=0,retry_cooldown=7):
		'''
		Queries the SQL database

		@param query: The SQL query
		@param exit_on_fail: Whether to exit on failure of the SQL query
		@param retries: Number of times to retry on failure
		@param retry_cooldown: Number of seconds to wait between retries, on failue

		@return: A list of rows, in this format:
			[
				{'column1':row1column1Value,'column2':row1column1Value},
				{'column1':row2column1Value,'column2':row2column1Value},
				...
			]
		'''
		
		try:
			self.cursor.execute(query)
			success=True

		#Process failed query
		except mysql.connector.Error as err:
			logger.error("Error with query: " +str(err))
			logger.error(f"Query was: \n\t{query}")

			#Retry query, if specified
			success=False
			if retries>0:
				for attemptNo in range(2,retries+2):
					if success==False:
						logger.warning("Attempt "+str(attemptNo)+":")
						time.sleep(retry_cooldown)
						try:
							self.cursor.execute(query)
							logger.info("Success!\n")
							success=True
						except Exception as e:
							logger.error("Error with query: " +str(err))
							logger.error("Query was: "+query)

			if exit_on_fail and success==False:
				exit()
		
		#Convert to dict
		if success:
			headers=[]
			for field in self.cursor._description:
				headers.append(field[0])
			
			values=[]
			for row in self.cursor:
				newValue={}
				for index,header in enumerate(headers):
					newValue[header]=row[index]
				values.append(newValue)
			return values

		return None

	'''
	Runs SQL UPDATE,DELETE, or other commands

	@param execution_statement: The statement to execute
	@param exit_on_fail: Whether to exit on failure of the SQL statement
	@param retries: Number of times to retry on failure
	@param retry_cooldown: Number of seconds to wait between retries, on failue
	'''
	def execute(self,execution_statement,exitOnFail=True,retries=0,retry_cooldown=7):

		#Execute changes to DB
		try:
			self.cursor.execute(execution_statement)
			self.cnx.commit()
			success=True
		
		#Process errors
		except mysql.connector.Error as err:
			success=False

			logger.error("Error with statement: " +str(err))
			logger.error("Statement: "+execution_statement)

			#Attempt retries, if specified
			success=False
			if retries>0:

				for attemptNo in range(2,retries+2):
					if success==False:
						logger.warning("Attempt "+str(attemptNo)+":")
						time.sleep(retry_cooldown)
				
						try:
							self.cursor.execute(execution_statement)
							self.cnx.commit()
							logger.info("Success!")
							success=True
						except Exception as e:
							logger.error("Error: "+str(err))
							logger.error(f"Statement: {execution_statement}")

			if exitOnFail and success==False:
				exit()


	def clearTable(self,table: str):
		'''
		Clears all rows in a given SQL table.

		@param cnx: The SQL connection to commit
		@param cursor: The SQL cursor to write the clear statement
		@param table: The SQL table to clear
		@param message: The log message to give context
		'''

		logger.warning("Truncating/Clearing table "+self.credentials['host']+"/"+table)

		self.execute(f'TRUNCATE {table}')

def listToSQLArray(items,numeric=False):
	'''
	Takes a list of strings/numbers, and converts to SQL array format.
	Eg [1,2,3]-> `(1,2,3)`
	Eg [a,b,c]->`('a','b','c')`

	@param items: The list of items
	@param numeric: Whether the items are numbers are not
	'''

	if len(items)==0:
		return None

	string='('
	for item in items:
		if not numeric:
			string+="\n"+stringify(item)+","
		else:
			string+="\n"+str(item)+","
	string=string[:-1]+')'
	
	return string















