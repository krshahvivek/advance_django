from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, DateTime, Boolean, Float, Integer, TIMESTAMP, create_engine
import sqlalchemy as db
from sqlalchemy.schema import ColumnDefault
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import Session
import os
import json
import pathlib
import logging
from logging import Logger
import pandas as pd
from pandas.io.sql import DatabaseError  # type: ignore
from sqlalchemy.exc import SQLAlchemyError

from typing import Any, Callable, Optional, Tuple


Base = declarative_base()


class DBConnect:
    logger: Logger
    config: dict
    dbKey : str
    _alchemyCnxn: db.engine.Engine
    defaultSchema: str

    DB_NULL_VALUE = "[[DBNULL]]"

    def __init__(self, config, dbKey):
        self.logger = logging.getLogger("minimal")
        self.config = config
        self.secretsConfig = config["secrets"][dbKey]
        self._openDBConnection(secretsConfig=self.secretsConfig)
        return

    def __enter__(self):
        self._openDBConnection(secretsConfig=self.secretsConfig)

    def __exit__(self):
        self._closeDBConnection()

    def __del__(self):
        self._closeDBConnection()

    def _openDBConnection(self, secretsConfig) -> bool:
        config = dict(
            subString.split("=")
            for subString in secretsConfig.split(";")
            if ("=" in subString)
        )
        connection_string = (
            "mysql+pymysql://"
            + (config["user"] + ":" + config["pwd"])
            + "@"
            + config["host"]
            + "/"
            + config["database"]
        )
        self._alchemyCnxn = create_engine(connection_string, echo=False)
        # Create the Metadata Object
        self.metaData = db.MetaData(bind=self._alchemyCnxn)
        db.MetaData.reflect(self.metaData)

    def _closeDBConnection(self):
        if self._alchemyCnxn is not None:
            self._alchemyCnxn.dispose()

    # Function that takes as argument another function and optional keyword arguments
    # The execFunction is executed with db connection retry enabled - so if there is
    # a communication failure error, the connection is re-established and the function
    # is executed again.
    def _execWithCnxnRetry(
        self,
        execFunction: Optional[Callable] = None,
        # alchemySession: bool = False,
        hasIterableResults: bool = False,
        **kwargs,
    ) -> Any:
        results = None
        retryCount = 0
        retryFlag = True
        maxRetries = self.config["maxRetries"]
        while retryFlag and retryCount <= maxRetries:
            retryCount += 1
            try:
                with Session(self._alchemyCnxn) as session:
                    session.begin()
                    if execFunction is None:
                        results = self._alchemyCnxn.execute(kwargs["query"]).fetchall()
                    else:
                        results = execFunction(
                            con=self._alchemyCnxn.get_bind(), query=kwargs["query"]
                        )
                    # If select query is executed, results will have to be concatenated
                    if hasIterableResults:
                        results = pd.concat(
                            [chunk for chunk in results], axis=0, ignore_index=True
                        )
                    session.commit()
                retryFlag = False
            except (SQLAlchemyError, DatabaseError) as err:
                self.logger.error(f"DB Error : {err}")
                if retryCount > maxRetries:
                    raise f"Unable to execute after multiple retries. {err}"
                self.logger.error(f"DB Error: Retrying {retryCount}/{maxRetries}.")
                self._closeDBConnection()
                self._openDBConnection(secretsConfig=self.secretsConfig)
            except Exception as err:
                self.logger.error(
                    f"{type(err)} error encountered when executing SQL query."
                )
                self.logger.error(err)
                return results
        return results

    # Function that creates the sqlalchemy select query
    def getSelectQuery(
        self,
        table: str,
        columnList: list = None,
    ) -> tuple[str, str]:
        baseQuery = db.select([table])
        if columnList is None:
            execQuery = baseQuery
        else:
            selectList = list()
            selectList = [table.columns[column] for column in columnList]
            execQuery = db.select(selectList)
        return execQuery, baseQuery

    # Function to select specific data from a specific table
    def selectTable(
        self,
        tableName: str,
        columnList: list = None,
        onlyQuery: bool = False,
    ) -> tuple[pd.DataFrame, str]:

        # if not self.checkTableExists(tableName=tableName):
        #     raise f"Select statement failed - {tableName} does not exist."
        table = self.metaData.tables[tableName]
        execQuery, baseQuery = self.getSelectQuery(table=table, columnList=columnList)
        if onlyQuery:
            return None, baseQuery
        data = self._execWithCnxnRetry(query=execQuery)
        return data

    # Function to select specific columns from a specific table with a WHERE clause
    def selectWithWhere(
        self,
        tableName: str,
        # schemaName: Optional[str] = None,
        columnList: Optional[list] = None,
        filterColumn: Optional[str] = None,
        filterOperator: Optional[str] = None,
        filterValue: Any = None,
        onlyQuery: bool = False,
    ) -> Tuple[Optional[pd.DataFrame], str]:

        return self.selectWithMultipleWheres(
            tableName=tableName,
            # schemaName=schemaName,
            columnList=columnList,
            filterConditions=[(filterColumn, filterOperator, filterValue)],
            onlyQuery=onlyQuery,
        )

    # Function to select specific columns from a specific table with multiple WHERE clause
    def selectWithMultipleWheres(
        self,
        tableName: str,
        # schemaName: Optional[str] = None,
        columnList: Optional[list] = None,
        filterConditions: Optional[list] = None,
        onlyQuery: bool = False,
    ) -> Tuple[Optional[pd.DataFrame], str]:
        # if not self.checkTableExists(tableName=tableName, schemaName=schemaName):
        #     raise  f"Select statement failed - {tableName} does not exist."
        table = self.metaData.tables[tableName]

        selecQuery, baseQuery = self.getSelectQuery(table=table, columnList=columnList)
        execQuery = self.addWhereClauses(
            query=selecQuery, table=table, filterConditions=filterConditions
        )
        if onlyQuery:
            return None, baseQuery
        data = self._execWithCnxnRetry(query=execQuery)
        return data

    def addWhereClauses(self, query, table, filterConditions):
        for filter in filterConditions:
            if type(filter[2]) == list:
                execQuery = query.where(table.columns[filter[0]].in_(filter[2]))
            else:
                if filter[1] in ["==", None]:
                    execQuery = query.where(table.columns[filter[0]] == (filter[2]))
                if filter[1] == ">":
                    execQuery = query.where(table.columns[filter[0]] > (filter[2]))
                if filter[1] == "<":
                    execQuery = query.where(table.columns[filter[0]] < (filter[2]))
        return execQuery

    def createTable(self, tableName: str, allColumns: list = None):
        allColumns = [
            Column("Id", Integer()),
            Column("name", String(255), nullable=False),
            Column("salary", Float(), default=100.0),
            Column("active", Boolean(), default=True),
        ]

        allColumns=list()
        tableColumns = [
            {"columnName": "Id", "type": "Integer()", "primary_key": True},
            {"columnName": "name", "type": "String(255)", "nullable": False},
            {"columnName": "salary", "type": "Float()", "default": 10000},
            {"columnName": "active", "type": "Boolean()", "default": True},
        ]
        for kwarg in tableColumns:
            # print(kwarg)
            singleColumn= self.getColumnParameters(**kwarg)
            # print(kwarg["type"])
            allColumns.append(singleColumn)


        newTable = db.Table(tableName, self.metaData, *allColumns)
        self.metaData.create_all(self._alchemyCnxn)
        return

    def getColumnParameters(self, columnName: str, type: str, primary_key: Optional[Boolean] =False, nullable: Optional[Boolean] =True,  default:Optional [str]=None):
        newConverter = {
            "String(255)" : str,
            "String(max)": str,
            "Integer()": int,
            "Boolean()": bool,
            "Float()": float,
        }
        columnType=newConverter.get(type, type)
        if default is not None:
            default=columnType(default)
        if type == "TIMESTAMP" and default is not None:
            default = eval(default)
        if primary_key == True:
            singleColumn= Column(columnName, eval(type), primary_key=primary_key)

        return Column(columnName, eval(type), ColumnDefault(default), primary_key=primary_key, nullable=nullable)

    def insertDataByRow(self, tableName, values):
        tableName = tableName.lower()
        table = self.metaData.tables[tableName]
        query = db.insert(table).values(**values) 
        results = self._alchemyCnxn.execute(query)

    def insertDataInBulk(self, tableName: str, valuesList: list):
        tableName = tableName.lower()
        table = self.metaData.tables[tableName]
        query = db.insert(table)
        results = self._alchemyCnxn.execute(query, valuesList)

    def updateData(self, tableName: str, updates: list, filterConditions: list):
        # updates take a list of tuples. Each tuple is a key value pair, where key is the column to be updated by the given value.
        table = self.metaData.tables[tableName]
        updateQuery = db.update(table)
        for update in updates:
            updateQuery = updateQuery.values(update[0] == update[1])

        execQuery = self.addWhereClauses(
            query=updateQuery, table=table, filterConditions=filterConditions
        )
        results = self._alchemyCnxn.execute(execQuery)

    def deleteData(self, tableName: str, filterConditions: list):
        table = self.metaData.tables[tableName.lower()]
        deleteQuery = db.delete(table)
        execQuery = self.addWhereClauses(
            query=deleteQuery, table=table, filterConditions=filterConditions
        )
        try:
            results = self._alchemyCnxn.execute(execQuery)
            return True
        except :
            return False
    
    def dropTable(self, tableName: str):
        table = self.metaData.tables[tableName.lower()]
        table.drop(self._alchemyCnxn)


    def getJoinedTables(self, tableNames:list):
        joindedTable = self.metaData.tables[tableNames[0]]
        for tableName in tableNames[1:]:
            table = self.metaData.tables[tableName]
            joindedTable= joindedTable.join(table, isouter=True)
        execQuery, baseQuery = self.getSelectQuery(table=joindedTable)
        data = self._alchemyCnxn.execute(execQuery)
        return data
        



