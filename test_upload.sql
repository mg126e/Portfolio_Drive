-- this sql file tests if the uploaded data is actually store into the databse
-- you can replace 'Upload Test 1' with the item name you entered.

select
    i.input_id,
    i.sid,
    i.title,
    i.document,
    i.created_at,
    f.file_id,
    f.original_filename,
    f.storage_key,
    f.file_size,
    f.time_uploaded
from input as i
left join file_attachment as f
    on i.input_id = f.input_id
where i.title = 'Upload Test 1'
order by i.input_id desc;

-- check which tags are connected to the uploaded item.

select
    i.input_id,
    i.title,
    t.name as tag_name
from input as i
join input_to_tag as it
    on i.input_id = it.input_id
join tag as t
    on it.tag_id = t.tag_id
where i.title = 'Upload Test 1'
order by i.input_id desc, t.name;