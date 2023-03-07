import json
import os
import pathlib
# from db import DBConnect
from GoDigApp.src.db import DBConnect
import pandas as pd
from typing import Any, Optional
import numpy as np


# configDir = os.path.join(pathlib.Path(__file__).parents[1], "config")
# with open(os.path.join(configDir, "config.json")) as configFile:
#     config = json.load(configFile)

# with open(os.path.join(configDir, config["secretsJson"])) as secretsJson:
#     config["secrets"] = json.load(secretsJson)


class Data:
    def __init__(self, config):
        self.config = config


    def getWellDescriptionDropdowns(self, regionName: str = None):
        allRegions = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tblregions", columnList=["RegionID", "Region"]
            )
        )
        allWells = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tblwelldesc"  # , columnList=["id", "RegionID", "area", "country", "well_type"]
            )
        )
        wellAllDescirption = allWells.merge(allRegions, how="outer", on="RegionID")

        if regionName == "All":
            areaList = wellAllDescirption["Area"].dropna().unique().tolist()
            countryList = wellAllDescirption["Country"].dropna().unique().tolist()
        else:
            areaList = (
                wellAllDescirption["Area"][wellAllDescirption["Region"] == regionName]
                .dropna()
                .unique()
                .tolist()
            )
            countryList = (
                wellAllDescirption["Country"][
                    wellAllDescirption["Region"] == regionName
                ]
                .dropna()
                .unique()
                .tolist()
            )

        locationList = wellAllDescirption["Location"].dropna().unique().tolist()
        wellTypeList = wellAllDescirption["WellType"].dropna().unique().tolist()
        resultList = wellAllDescirption["Result"].dropna().unique().tolist()

        operatorTable = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tbloperators", columnList=["OperatorName"]
            )
        )
        operatorList = operatorTable["OperatorName"].dropna().unique().tolist()
        contractorTable = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tbldrlgcontractors", columnList=["ContractorName"]
            )
        )
        contractorList = contractorTable["ContractorName"].dropna().unique().tolist()
        rigTable = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tblrigs", columnList=["RigName"]
            )
        )
        rigList = rigTable["RigName"].dropna().unique().tolist()

        licenseTable = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tbllicnames", columnList=["LicenseID", "LicName"]
            )
        )
        licenseList = licenseTable["LicName"].dropna().unique().tolist()
        for lst in [
            operatorList,
            licenseList,
            locationList,
            wellTypeList,
            resultList,
            contractorList,
            rigList,
        ]:
            lst.insert(0, None)
        return (
            areaList,
            operatorList,
            countryList,
            licenseList,
            locationList,
            wellTypeList,
            resultList,
            contractorList,
            rigList,
        )

    def getWellInfo(self, wellName: str = None):

        wellAllDescirption = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(tableName="tblwelldesc")
        )

        operatorTable = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tbloperators", columnList=["OperatorID", "OperatorName"]
            )
        )
        wellAllDescirption = wellAllDescirption.merge(
            operatorTable, how="outer", on="OperatorID"
        )

        licenseTable = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tbllicnames", columnList=["LicenseID", "LicName"]
            )
        )
        wellAllDescirption = wellAllDescirption.merge(
            licenseTable, how="outer", on="LicenseID"
        )

        rigTable = pd.DataFrame(
            DBConnect(self.config, "wellinformed").selectTable(
                tableName="rig", columnList=["id", "rig_name"]
            )
        )
        rigTable.rename(columns={"id": "RigID"}, inplace=True)
        wellAllDescirption = wellAllDescirption.merge(rigTable, how="outer", on="RigID")

        contractorTable = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tbldrlgcontractors",
                columnList=["ContractorID", "ContractorName"],
            )
        )

        wellAllDescirption = wellAllDescirption.merge(
            contractorTable, how="outer", on="ContractorID"
        )

        wellInfo = wellAllDescirption.loc[
            wellAllDescirption["WellName"] == wellName
        ].to_dict("list")
        for item in [
            "ContractorName",
            "rig_name",
            "OperatorName",
            "LicName",
            "Country",
            "Area",
            "Field",
            "Location",
            "Platform",
            "SSWhead",
            "State",
            "Result",
        ]:
            if str(wellInfo[item][0]) == "nan":
                wellInfo[item][0] = None

        return wellInfo

    def getIdFromName(
        self,
        name: str,
        tableName: str,
        nameColumn: str,
        idColumn: str,
        schema: Optional[str] = "welldata",
    ):
        dataTable = pd.DataFrame(
            DBConnect(self.config, schema).selectTable(tableName=tableName)
        )
        return int(dataTable[idColumn][dataTable[nameColumn] == name].values[0])

    def getCompleteWellDropdowns(self):
        allRegions = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tblregions", columnList=["RegionID", "Region"]
            )
        )
        allWells = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tblwelldesc",
                columnList=["WellID", "RegionID", "Area", "WellName"],
            )
        )
        allWellPaths = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tblwellpaths", columnList=["WellID", "WellPath"]
            )
        )
        # allWellPaths.rename(columns={"WellID": "id"}, inplace=True)
        allRegionAreaWell = allWells.merge(allRegions, how="outer", on="RegionID")
        allRegionAreaWellPaths = allRegionAreaWell.merge(
            allWellPaths, how="outer", on="WellID"
        )[["Region", "Area", "WellName", "WellPath"]].drop_duplicates()

        return allRegionAreaWellPaths

    def getContractorRigData(self):
        # contractorRigNameData = pd.DataFrame(DBConnect(self.config, "welldata").getJoinedTables(tableNames=['tbldrlgcontractors', 'tblrigs']))
        contractorNames = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(
                tableName="tbldrlgcontractors"
            )
        )
        rigData = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(tableName="tblrigs")
        )
        contractorRigNameData = contractorNames.merge(
            rigData, how="left", on="ContractorID"
        )
        rigTypeData = pd.DataFrame(
            DBConnect(self.config, "welldata").selectTable(tableName="tblrigtypes")
        )
        contractorRigNameData.rename(columns={"RigTypeID": "RigType"}, inplace=True)
        contractorRigData = contractorRigNameData.merge(
            rigTypeData, how="left", on="RigType"
        )
        return contractorRigData

    def getLicenseData(self):
        licenseData = pd.DataFrame(
            DBConnect(self.config, "welldata").getJoinedTables(
                tableNames=[
                    "tbllicnames",
                    "tblregions",
                    "tbllicpartpct",
                    "tbllicpartnames",
                    "tblliccoords",
                ]
            )
        )
        return licenseData

    def getTableData(
        self,
        tableName,
        columnList: list = None,
        filterColumn: str = None,
        filterOperator : str = None,
        filterValue: Any = None,
    ):
        if filterColumn is None:
            tableData = pd.DataFrame(
                DBConnect(self.config, "welldata").selectTable(tableName=tableName, columnList = columnList)
            )
        else:
            tableData = pd.DataFrame(
                DBConnect(self.config, "welldata").selectWithWhere(
                    tableName=tableName, columnList = columnList, filterColumn=filterColumn, filterOperator = filterOperator, filterValue=filterValue
                )
            )
        return tableData

    def addNewRowInTable(self, tableName, values, schema: str = "welldata"):
        return DBConnect(self.config, schema).insertDataByRow(
            tableName=tableName, values=values
        )

    def deleteRowFromTable(
        self, tableName: str, filterConditions: list, schema: str = "welldata"
    ):
        return DBConnect(self.config, schema).deleteData(
            tableName=tableName, filterConditions=filterConditions
        )

    def updateData(
        self,
        tableName,
        updates,
        filterConditions
    ):
        DBConnect(self.config, "welldata").updateData(tableName=tableName, updates = updates, filterConditions = filterConditions)
        return


# df=pd.DataFrame(Data(config).data)
# print(df.info())

# df1=pd.DataFrame(Data(config).data1)
# print(df1.info())
# # print()
