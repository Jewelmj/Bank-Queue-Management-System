-- Creating database named Bank_Db
create database Bank_Db;

-- Switching to the Bank_Db database
use Bank_Db;

-- Creating table Role to store user roles
Create table Role(
ID tinyint not null, -- Role ID
RoleName varchar(30) not null, -- Role name
Constraint PK_Role primary key(ID)) -- Primary key constraint on ID

-- Inserting roles into the Role table
insert into Role values(1,'Admin') -- Inserting Admin role
insert into Role values(2,'Accounts') -- Inserting Accounts role
insert into Role values(3,'Deposits') -- Inserting Deposits role
insert into Role values(4,'Loans') -- Inserting Loans role

-- Selecting all records from Role table
Select * from Role

-- Creating table Users to store user information
Create table Users(
ID tinyint not null, -- User ID
RoleID tinyint not null, -- Role ID
UserName varchar(30) not null, -- User name
Passwords varchar(30) not null, -- User password
Constraint PK_Users primary key(ID), -- Primary key constraint on ID
Constraint FK_Role foreign key(RoleID) references Role(ID)) -- Foreign key constraint referencing Role table

-- Inserting users into the Users table
insert into Users values (1, 1, 'Admin1', 'Admin123') -- Inserting Admin user
insert into Users values (2, 2, 'Accounts1', 'Admin123') -- Inserting Accounts user
insert into Users values (3, 3, 'Deposits1', 'Admin123') -- Inserting Deposits user
insert into Users values (4, 4, 'Loans1', 'Admin123') -- Inserting Loans user

-- Selecting all records from Users table
select * from Users

-- Creating table ServiceType to store types of services
CREATE TABLE ServiceType (
    ID tinyint NOT NULL, -- Service type ID
    ServiceType varchar(20) NOT NULL, -- Service type name
    CONSTRAINT PK_ServiceType PRIMARY KEY (ID), -- Primary key constraint on ID
    CONSTRAINT UK_ServiceType_ID UNIQUE (ID) -- Unique constraint on ID
);

-- Inserting service types into the ServiceType table
Insert into ServiceType values(1,'Accounts') -- Inserting Accounts service type
Insert into ServiceType values(2,'Loans') -- Inserting Loans service type
Insert into ServiceType values(3,'Deposits') -- Inserting Deposits service type

-- Selecting all records from ServiceType table
Select * from ServiceType

-- Creating table Servicename to store names of services
CREATE TABLE Servicename (
    ID smallint NOT NULL, -- Unique identifier for each service.
    ServiceTypeID tinyint NOT NULL, -- Identifier for the type of service.
    ServicesName varchar(40) NOT NULL UNIQUE, -- Name of the service, which is unique.
    CONSTRAINT PK_Servicename PRIMARY KEY (ID), -- Primary key constraint for the ID field.
    CONSTRAINT FK_ServiceType FOREIGN KEY (ServiceTypeID) REFERENCES ServiceType(ID) -- Foreign key constraint referencing the ServiceType table.
);

-- Inserting service names into the Servicename table
Insert into Servicename values(1,1,'Open new account') -- Inserting Open new account service
Insert into Servicename values(2,1,'Cheque Deposit') -- Inserting Cheque Deposit service
Insert into Servicename values(3,1,'Cash Deposit') -- Inserting Cash Deposit service
Insert into Servicename values(4,1,'Withdraw') -- Inserting Withdraw service
Insert into Servicename values(5,1,'Request Passbook Update') -- Inserting Request Passbook Update service
Insert into Servicename values(6,1,'Request Cheque book') -- Inserting Request Cheque book service
Insert into Servicename values(7,1,'Close Account') -- Inserting Close Account service
Insert into Servicename values(8,3,'Apply for new loan') -- Inserting Apply for new loan service
Insert into Servicename values(9,3,'EMI Payment') -- Inserting EMI Payment service
Insert into Servicename values(10,3,'Close Loan') -- Inserting Close Loan service
Insert into Servicename values(11,3,'Foreign exchange transactions') -- Inserting Foreign exchange transactions service
Insert into Servicename values(12,2,'Open FD') -- Inserting Open FD service
Insert into Servicename values(13,2,'Open RD') -- Inserting Open RD service
Insert into Servicename values(14,2,'Deposit') -- Inserting Deposit service
Insert into Servicename values(15,2,'Close FD') -- Inserting Close FD service
Insert into Servicename values(16,2,'Close RD') -- Inserting Close RD service

-- Selecting all records from Servicename table
Select * from Servicename

-- Creating table ServiceStatus to store status of services
Create table ServiceStatus(
ID tinyint not null, -- Status ID
Status varchar(30) not null, -- Status name
Constraint PK_ServiceStatus primary key(ID)) -- Primary key constraint on ID

-- Inserting service status into the ServiceStatus table
Insert into ServiceStatus values (0,'Cancelled') -- Inserting Cancelled status
Insert into ServiceStatus values (1,'Open') -- Inserting Open status
Insert into ServiceStatus values (2,'Processed') -- Inserting Processed status

-- Selecting all records from ServiceStatus table
Select * from ServiceStatus

-- Creating table Request to store service requests
CREATE TABLE Request (
    ID tinyint NOT NULL, -- Request ID
    TokenNum tinyint NOT NULL, -- Token number
    Date_Time datetime NOT NULL, -- Date and time of request
    RaisedBy varchar(30), -- User who raised the request
    ServiceID tinyint NOT NULL, -- Service ID
    Processed bit NOT NULL, -- Processed status of the request
    CONSTRAINT PK_Request PRIMARY KEY (ID) -- Primary key constraint on ID
);

-- Inserting a request into the Request table
INSERT INTO Request VALUES (1, 1, '2024-02-13', 'Sharma', 16, 1); -- Inserting a sample request

-- Switching back to the Bank_Db database
use Bank_Db

-- Selecting all records from Servicename table
Select * from Servicename

-- Selecting all records from Request table
Select * from Request
