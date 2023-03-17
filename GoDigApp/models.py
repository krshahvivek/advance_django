# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthUserEmails(models.Model):
    emailkey = models.AutoField(db_column='EmailKey', primary_key=True)  # Field name made lowercase.
    emailid = models.CharField(db_column='EmailID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    adminid = models.ForeignKey('GroupAdmins', models.DO_NOTHING, db_column='AdminID', blank=True, null=True)  # Field name made lowercase.
    permitas = models.IntegerField(db_column='PermitAs', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'auth_user_emails'


class Contractors(models.Model):
    contractorid = models.AutoField(db_column='ContractorID', primary_key=True)  # Field name made lowercase.
    contractorname = models.CharField(db_column='ContractorName', max_length=50, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'contractors'


class Dummytable(models.Model):
    wellid = models.AutoField(db_column='WellID', primary_key=True)  # Field name made lowercase.
    operatorid = models.IntegerField(db_column='OperatorID', blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=50, blank=True, null=True)  # Field name made lowercase.
    area = models.CharField(db_column='Area', max_length=50, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    wellname = models.CharField(db_column='WellName', max_length=50, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    field = models.CharField(db_column='Field', max_length=50, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    block = models.CharField(db_column='Block', max_length=50, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    licenseid = models.IntegerField(db_column='LicenseID', blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=50, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    latdec = models.FloatField(db_column='LatDec', blank=True, null=True)  # Field name made lowercase.
    londec = models.FloatField(db_column='LonDec', blank=True, null=True)  # Field name made lowercase.
    northing = models.FloatField(db_column='Northing', blank=True, null=True)  # Field name made lowercase.
    easting = models.FloatField(db_column='Easting', blank=True, null=True)  # Field name made lowercase.
    northingwgs84 = models.FloatField(db_column='NorthingWGS84', blank=True, null=True)  # Field name made lowercase.
    eastingwgs84 = models.FloatField(db_column='EastingWGS84', blank=True, null=True)  # Field name made lowercase.
    welltype = models.CharField(db_column='WellType', max_length=50, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='Location', max_length=10, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    td = models.FloatField(db_column='TD', blank=True, null=True)  # Field name made lowercase.
    result = models.CharField(db_column='Result', max_length=25, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    spuddate = models.DateTimeField(db_column='SpudDate', blank=True, null=True)  # Field name made lowercase.
    onhiredate = models.DateTimeField(db_column='OnHireDate', blank=True, null=True)  # Field name made lowercase.
    releasedate = models.DateTimeField(db_column='ReleaseDate', blank=True, null=True)  # Field name made lowercase.
    totdays = models.FloatField(db_column='TotDays', blank=True, null=True)  # Field name made lowercase.
    contractorid = models.IntegerField(db_column='ContractorID', blank=True, null=True)  # Field name made lowercase.
    rigid = models.IntegerField(db_column='RigID', blank=True, null=True)  # Field name made lowercase.
    elevation = models.FloatField(db_column='Elevation', blank=True, null=True)  # Field name made lowercase.
    watdepth = models.FloatField(db_column='WatDepth', blank=True, null=True)  # Field name made lowercase.
    spheroid = models.CharField(db_column='Spheroid', max_length=50, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    regionid = models.IntegerField(db_column='RegionID', blank=True, null=True)  # Field name made lowercase.
    sswhead = models.TextField(db_column='SSWhead', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    platform = models.CharField(db_column='Platform', max_length=50, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    slot = models.CharField(db_column='Slot', max_length=10, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    epsg = models.IntegerField(db_column='EPSG', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dummytable'


class GroupAdmins(models.Model):
    adminid = models.AutoField(db_column='AdminID', primary_key=True)  # Field name made lowercase.
    adminname = models.CharField(db_column='AdminName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    adminemailid = models.CharField(db_column='AdminEmailID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    groupid = models.ForeignKey('Groups', models.DO_NOTHING, db_column='GroupID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'group_admins'


class Groups(models.Model):
    groupid = models.AutoField(db_column='GroupID', primary_key=True)  # Field name made lowercase.
    groupname = models.CharField(db_column='GroupName', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'groups'


class Licenses(models.Model):
    licenseid = models.AutoField(db_column='LicenseID', primary_key=True)  # Field name made lowercase.
    regionid = models.ForeignKey('Regions', models.DO_NOTHING, db_column='RegionID', blank=True, null=True)  # Field name made lowercase.
    licname = models.CharField(db_column='LicName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nocorns = models.SmallIntegerField(db_column='NoCorns', blank=True, null=True)  # Field name made lowercase.
    spheroid = models.CharField(db_column='Spheroid', max_length=50, blank=True, null=True)  # Field name made lowercase.
    groupkey = models.CharField(db_column='GroupKey', max_length=64, blank=True, null=True)  # Field name made lowercase.
    systemkey = models.CharField(db_column='SystemKey', max_length=64, blank=True, null=True)  # Field name made lowercase.
    datumkey = models.CharField(db_column='DatumKey', max_length=64, blank=True, null=True)  # Field name made lowercase.
    unitkey = models.CharField(db_column='UnitKey', max_length=64, blank=True, null=True)  # Field name made lowercase.
    handle = models.CharField(db_column='Handle', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lrp = models.FloatField(db_column='LRP', blank=True, null=True)  # Field name made lowercase.
    hrp = models.FloatField(db_column='HRP', blank=True, null=True)  # Field name made lowercase.
    taxrate = models.FloatField(db_column='TaxRate', blank=True, null=True)  # Field name made lowercase.
    royalty = models.FloatField(db_column='Royalty', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'licenses'


class LoginUuids(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uuid = models.CharField(db_column='UUID', max_length=255)  # Field name made lowercase.
    emailid = models.CharField(db_column='EmailID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    createdon = models.DateTimeField(db_column='CreatedOn')  # Field name made lowercase.
    expireon = models.DateTimeField(db_column='ExpireON')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'login_uuids'


class PetroliumRates(models.Model):
    rateid = models.AutoField(db_column='RateID', primary_key=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date')  # Field name made lowercase.
    cruderate = models.FloatField(db_column='CrudeRate', blank=True, null=True)  # Field name made lowercase.
    cbmrate = models.FloatField(db_column='CBMRate', blank=True, null=True)  # Field name made lowercase.
    gasrate = models.FloatField(db_column='GasRate', blank=True, null=True)  # Field name made lowercase.
    condensaterate = models.FloatField(db_column='CondensateRate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'petrolium_rates'


class Productions(models.Model):
    productionid = models.AutoField(db_column='ProductionID', primary_key=True)  # Field name made lowercase.
    productiondate = models.DateTimeField(db_column='ProductionDate', blank=True, null=True)  # Field name made lowercase.
    wellid = models.ForeignKey(Dummytable, models.DO_NOTHING, db_column='WellID', blank=True, null=True)  # Field name made lowercase.
    crudeoil = models.FloatField(db_column='CrudeOil', blank=True, null=True)  # Field name made lowercase.
    naturalgas = models.FloatField(db_column='NaturalGas', blank=True, null=True)  # Field name made lowercase.
    condensate = models.FloatField(db_column='Condensate', blank=True, null=True)  # Field name made lowercase.
    cbm = models.FloatField(db_column='CBM', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'productions'


class Regions(models.Model):
    regionid = models.AutoField(db_column='RegionID', primary_key=True)  # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=50, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    mapfile = models.CharField(db_column='Mapfile', max_length=50, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.
    cm = models.IntegerField(db_column='CM', blank=True, null=True)  # Field name made lowercase.
    hemi = models.CharField(db_column='Hemi', max_length=1, db_collation='utf8mb3_general_ci', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'regions'


class User(models.Model):
    userid = models.AutoField(db_column='UserID', primary_key=True)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=128)  # Field name made lowercase.
    groupid = models.ForeignKey(Groups, models.DO_NOTHING, db_column='GroupID')  # Field name made lowercase.
    username = models.CharField(db_column='UserName', max_length=50)  # Field name made lowercase.
    isadmin = models.IntegerField(db_column='IsAdmin')  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.
    emailid = models.CharField(db_column='EmailID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    contactno = models.CharField(db_column='ContactNo', max_length=50,blank=True,null=True)

    class Meta:
        managed = False
        db_table = 'user'


class Welldescription(models.Model):
    wellid = models.AutoField(db_column='WellID', primary_key=True)  # Field name made lowercase.
    operatorid = models.IntegerField(db_column='OperatorID', blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=50, blank=True, null=True)  # Field name made lowercase.
    area = models.CharField(db_column='Area', max_length=50, blank=True, null=True)  # Field name made lowercase.
    wellname = models.CharField(db_column='WellName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    field = models.CharField(db_column='Field', max_length=50, blank=True, null=True)  # Field name made lowercase.
    block = models.CharField(db_column='Block', max_length=50, blank=True, null=True)  # Field name made lowercase.
    licenseid = models.ForeignKey(Licenses, models.DO_NOTHING, db_column='LicenseID', blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=50, blank=True, null=True)  # Field name made lowercase.
    latdec = models.FloatField(db_column='LatDec', blank=True, null=True)  # Field name made lowercase.
    londec = models.FloatField(db_column='LonDec', blank=True, null=True)  # Field name made lowercase.
    northing = models.FloatField(db_column='Northing', blank=True, null=True)  # Field name made lowercase.
    easting = models.FloatField(db_column='Easting', blank=True, null=True)  # Field name made lowercase.
    northingwgs84 = models.FloatField(db_column='NorthingWGS84', blank=True, null=True)  # Field name made lowercase.
    eastingwgs84 = models.FloatField(db_column='EastingWGS84', blank=True, null=True)  # Field name made lowercase.
    welltype = models.CharField(db_column='WellType', max_length=50, blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='Location', max_length=10, blank=True, null=True)  # Field name made lowercase.
    td = models.FloatField(db_column='TD', blank=True, null=True)  # Field name made lowercase.
    result = models.CharField(db_column='Result', max_length=25, blank=True, null=True)  # Field name made lowercase.
    spuddate = models.DateTimeField(db_column='SpudDate', blank=True, null=True)  # Field name made lowercase.
    onhiredate = models.DateTimeField(db_column='OnHireDate', blank=True, null=True)  # Field name made lowercase.
    releasedate = models.DateTimeField(db_column='ReleaseDate', blank=True, null=True)  # Field name made lowercase.
    totdays = models.FloatField(db_column='TotDays', blank=True, null=True)  # Field name made lowercase.
    contractorid = models.ForeignKey(Contractors, models.DO_NOTHING, db_column='ContractorID', blank=True, null=True)  # Field name made lowercase.
    rigid = models.IntegerField(db_column='RigID', blank=True, null=True)  # Field name made lowercase.
    elevation = models.FloatField(db_column='Elevation', blank=True, null=True)  # Field name made lowercase.
    watdepth = models.FloatField(db_column='WatDepth', blank=True, null=True)  # Field name made lowercase.
    spheroid = models.CharField(db_column='Spheroid', max_length=50, blank=True, null=True)  # Field name made lowercase.
    regionid = models.ForeignKey(Regions, models.DO_NOTHING, db_column='RegionID', blank=True, null=True)  # Field name made lowercase.
    sswhead = models.TextField(db_column='SSWhead', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    platform = models.CharField(db_column='Platform', max_length=50, blank=True, null=True)  # Field name made lowercase.
    slot = models.CharField(db_column='Slot', max_length=10, blank=True, null=True)  # Field name made lowercase.
    epsg = models.IntegerField(db_column='EPSG', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'welldescription'
