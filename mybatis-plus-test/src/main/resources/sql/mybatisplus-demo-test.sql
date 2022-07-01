create database TOCD_TEST;
use TOCD_TEST;

create table tbUser
(
    Id         bigint(20) auto_increment primary key,
    Name       varchar(20) not null,
    CreateTime datetime    not null default now(),
    UpdateTime datetime    not null default now()
);

create table tbUserLog
(
    Id         bigint(20) auto_increment primary key,
    UserId     bigint(20)  not null,
    Name       varchar(20) not null,
    CreateTime datetime    not null default now(),
    UpdateTime datetime    not null default now(),

    foreign key (UserId) references tbUser (Id)
);