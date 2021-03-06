-- number test for v9.0.0-beta.1.xTP aarch64-redhat-linux, built 2021/08/24 05:32:28, go1.15.13
-- Author: cuixiangling
-- Date: 2021/08/29
drop table if exists tn;
create table tn(a number);
insert into tn values(0.10e126);
insert into tn values(0.10e127);
insert into tn values(0.10e-130);
insert into tn values(0.10e-131);
insert into tn values(0.10e-132);
insert into tn values(123456789012);
insert into tn values(12345678901234567890);
insert into tn values(1234567890123456789012);
insert into tn values(123456789012345678901234);
select * from tn;
drop table tn;

create table tn(a number(400000000));
insert into tn values(0.10e127);
select sum(a) from tn;

drop table tn;
create table tn(a dec(10,2));
insert into tn values(54.00);
insert into tn values(4.0);
insert into tn select * from tn;
insert into tn select 1.0 from dual;
insert into tn values(4.5);
select * from tn;

select 1.0::dec(3,2) from dual;
drop table tn;
