-- Total colleges count check
select count(*) from colleges;

-- Sample rows
select * from colleges limit 10;

-- State-wise college count
select state, count(*) as total_colleges
from colleges
group by state
order by total_colleges desc;