create table if not exists _workflow_spec (
  id uuid primary key,
  serialization json
);

create table if not exists _task_spec (
  workflow_spec_id uuid references _workflow_spec (id) on delete cascade,
  name text generated always as (serialization->>'name') stored,
  serialization json
);
create index if not exists task_spec_workflow on _task_spec (workflow_spec_id);
create index  if not exists task_spec_name on _task_spec (name);

create view if not exists workflow_spec as 
  with 
    ts as (select workflow_spec_id, json_group_object(name, json(serialization)) task_specs from _task_spec group by workflow_spec_id)
  select
    id, json_insert(serialization, '$.task_specs', json(task_specs)) serialization
    from (
      select _workflow_spec.id id, serialization, task_specs from _workflow_spec join ts on _workflow_spec.id=ts.workflow_spec_id
    );

create trigger if not exists insert_workflow_spec instead of insert on workflow_spec
begin
  insert into _workflow_spec (id, serialization) values (new.id, json_remove(new.serialization, '$.task_specs'));
  insert into _task_spec (workflow_spec_id, serialization) select new.id, value from json_each(new.serialization->>'task_specs');
end;

create trigger if not exists delete_workflow_spec instead of delete on workflow_spec
begin
  delete from _workflow_spec where id=old.id;
  delete from _task_spec where workflow_spec_id=old.id;
end;

create table if not exists _spec_dependency (
  parent_id uuid references _workflow_spec (id) on delete cascade,
  child_id uuid references _workflow_spec (id) on delete cascade
);
create index if not exists spec_parent on _spec_dependency (parent_id);
create index if not exists spec_child on _spec_dependency (child_id);

create view if not exists spec_dependency as
  with recursive
    dependency(root, descendant, depth) as (
      select parent_id, child_id, 0 from _spec_dependency
      union
      select root, child_id, depth + 1 from _spec_dependency, dependency where parent_id=dependency.descendant
    )
  select root, descendant, depth, serialization from dependency join workflow_spec on dependency.descendant=workflow_spec.id;

create table if not exists _workflow (
  id uuid primary key,
  workflow_spec_id uuid references _workflow_spec (id),
  serialization json
);

create table if not exists _task (
  workflow_id references _workflow (id) on delete cascade,
  id uuid generated always as (serialization->>'id') stored unique,
  serialization json
);
create index if not exists task_id on _task (id);
create index if not exists task_workflow_id on _task (workflow_id);

create table if not exists _task_data (
  workflow_id uuid references _workflow (id) on delete cascade,
  task_id uuid,
  name text,
  value json,
  last_updated timestamp default current_timestamp,
  unique (task_id, name)
);
create index if not exists task_data_id on _task_data (task_id);
create index if not exists task_data_name on _task_data (name);

create view if not exists task as
  with data as (
    select task_id, json_group_object(name, iif(json_valid(value), json(value), value)) task_data
      from _task_data group by task_id
  )
  select _task.workflow_id, _task.id, json_insert(serialization, '$.data', json(ifnull(task_data, '{}'))) serialization
    from _task left join data on _task.id=data.task_id;

create trigger if not exists insert_task instead of insert on task
  begin
    insert into _task (workflow_id, serialization) values (new.workflow_id, json_remove(new.serialization, '$.data'));
    insert into _task_data (workflow_id, task_id, name, value)
      select new.workflow_id, new.serialization->>'id', key, value from json_each(new.serialization->>'data') where true
      on conflict (task_id, name) do nothing;
  end;

create trigger if not exists update_task instead of update on task
  begin
    update _task set serialization=json_remove(new.serialization, '$.data') where _task.id=new.serialization->>'id';
    delete from _task_data where task_id=new.id and name not in (select key from json_each(new.serialization->>'data'));
    insert into _task_data (workflow_id, task_id, name, value)
      select new.workflow_id, new.serialization->>'id', key, value from json_each(new.serialization->>'data') where true
      on conflict (task_id, name) do update set value=excluded.value;
  end;

create trigger if not exists delete_task instead of delete on task
begin
  delete from _task where id=old.id;
  delete from _task_data where task_id=old.id;
end;

create table if not exists _workflow_data (
  workflow_id uuid references _workflow (id) on delete cascade,
  name text,
  value json,
  last_updated timestamp default current_timestamp,
  unique (workflow_id, name)
);
create index if not exists workflow_data_id on _workflow_data (workflow_id);
create index if not exists wokflow_data_name on _workflow_data (name);

create view if not exists workflow as
  with
    tasks as (select workflow_id, json_group_object(id, json(serialization)) tasks from task group by workflow_id),
    data as (select workflow_id, json_group_object(name, iif(json_valid(value), json(value), value)) data from _workflow_data group by workflow_id)
  select
    _workflow.id,
    _workflow.workflow_spec_id,
    json_insert(
      json_insert(
        json_insert(
          _workflow.serialization,
          '$.data',
          json(ifnull(data, '{}'))
        ),
        '$.tasks',
        json(tasks)
      ),
      '$.spec',
      json(workflow_spec.serialization)
    ) serialization
  from _workflow
    left join data on _workflow.id=data.workflow_id
    join tasks on _workflow.id=tasks.workflow_id
    join workflow_spec on _workflow.workflow_spec_id=workflow_spec.id;

create trigger if not exists insert_workflow instead of insert on workflow
begin
  insert into _workflow (id, workflow_spec_id, serialization) 
    values (
      new.id,
      new.workflow_spec_id,
      json_remove(json_remove(new.serialization, '$.tasks'), '$.data')
    );
  insert into task (workflow_id, serialization) select new.id, value from json_each(new.serialization->>'tasks');
  insert into _workflow_data (workflow_id, name, value) select new.id, key, value from json_each(new.serialization->>'data');
end;

create trigger if not exists update_workflow instead of update on workflow
begin
  update _workflow set serialization=json_remove(json_remove(new.serialization, '$.tasks'), '$.data') where _workflow.id=new.id;
  delete from task where workflow_id=new.id and id not in (select value->>'id' from json_each(new.serialization->>'tasks'));
  update task set serialization=value from (
    select value, serialization from json_each(new.serialization->>'tasks') t join _task on value->>'id'=_task.id
    ) t
    where value->>'id'=task.id and value->>'last_state_change' > t.serialization->>'last_state_change';
  insert into task (workflow_id, serialization) select new.id, value from json_each(new.serialization->>'tasks')
    where value->>'id' not in (select id from _task where workflow_id=new.id);
  delete from _workflow_data where workflow_id=new.id and name not in (select key from json_each(new.serialization->>'data'));
  insert into _workflow_data (workflow_id, name, value) select new.id, key, value from json_each(new.serialization->>'$.data') where true
    on conflict (workflow_id, name) do update set value=excluded.value;
end;

create trigger if not exists delete_workflow instead of delete on workflow
begin
  delete from _workflow where id=old.id;
  delete from _task where workflow_id=old.id;
  delete from _workflow_data where workflow_id=old.id;
end;

create view if not exists workflow_dependency as
  with recursive
    subworkflow as (select workflow_id, id from _task where id in (select id from _workflow)),
    dependency(root, descendant, depth) as (
      select workflow_id, id, 1 from subworkflow
      union
      select workflow_id, dependency.descendant, depth + 1 from subworkflow, dependency where subworkflow.id=dependency.root
    )
  select root, descendant, depth, serialization from dependency join workflow on dependency.descendant=workflow.id;

create view if not exists spec_library as
  select id, serialization->>'name' name, serialization->>'file' filename from workflow_spec
    where id not in (select distinct child_id from _spec_dependency);

create table if not exists instance (
  id uuid primary key references _workflow (id) on delete cascade,
  bullshit text,
  spec_name text,
  active_tasks int,
  started timestamp,
  updated timestamp,
  ended timestamp
);

create trigger if not exists create_instance instead of insert on workflow
begin
  insert into instance (id, spec_name, active_tasks, started) select * from (
    select new.id, name, count(value), current_timestamp
      from (select name from spec_library where id=new.workflow_spec_id), json_each(new.serialization->>'tasks')
      where value->>'state' between 8 and 32
  ) where new.serialization->>'typename'='BpmnWorkflow';
end;

create trigger if not exists update_instance instead of update on workflow
begin
  update instance set updated=current_timestamp, ended=t.ended from (
    select iif(count(value)=0, current_timestamp, null) ended
    from json_each(new.serialization->>'tasks') where value->>'state' < 64
  ) t where id=new.id;
end;

create trigger if not exists delete_instance instead of delete on workflow
begin
   delete from instance where id=old.id;
end;

