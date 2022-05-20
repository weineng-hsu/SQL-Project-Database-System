drop table if exists Skill_with_Type cascade;
drop table if exists Type cascade;
drop table if exists Damage cascade;
drop table if exists Pokemon_first_seen cascade;
drop table if exists Pokemon_have_type cascade;
drop table if exists Requirement cascade;
drop table if exists Pokemon_learn_skill cascade;
drop table if exists Pokemon_evolve cascade;
drop table if exists Pokemon_base_type cascade;
drop table if exists Place_champion cascade;
drop table if exists Episode_happen_in cascade;
drop table if exists Trainer cascade;
drop table if exists Pokemon_Episode_Trainer cascade;
drop table if exists Trainer_Appear cascade;

create table Type(
	Name varchar(42) primary key,
	Generation integer not null
);

create table Trainer(
	Name varchar(42) primary key,
	Age integer,
	Gender varchar(42)
);

create table Skill_with_Type(
	Name varchar(42) primary key,
	Chance integer, 
	Damage integer,
	Type_name varchar(42) not null,
	foreign key (Type_name) references Type(Name)
);

create table Damage(
	Type_name_from varchar(42) not null,
	Type_name_to varchar(42) not null, 
	Multiply float not null,
	primary key (Type_name_from, Type_name_to), 
	foreign key (Type_name_from) references Type(Name),
	foreign key (Type_name_to) references Type(Name)
);

create table Place_champion(
	Name varchar(42) primary key,
	Design_from varchar(42),
	Champion varchar(42),
	foreign key (Champion) references Trainer(Name)
);

create table Episode_happen_in(
	Generation integer,
	Number	integer,
	Broadcast Date not null,
	Happen_in varchar(42),
	primary key	(Generation, Number),
	foreign key (Happen_in) references Place_champion(Name)
);

create table Pokemon_first_seen(
	id integer primary key,
	Name varchar(42) not null unique,
	HP integer  not null,
	Atk integer not null,
	Def integer not null,
	Special_Atk integer not null,
	Special_Def integer not null,
	Speed integer not null,
	Fisrt_seen_generation integer,
	Fisrt_seen_no integer,
	foreign key (Fisrt_seen_generation, Fisrt_seen_no) references Episode_happen_in(Generation, Number)
);

create table Pokemon_have_type(
	id integer, 
	Type_name varchar(42),
	primary key (id, Type_name),
	foreign key (Type_name) references Type(name),
	foreign key (id) references Pokemon_first_seen(id)
);

create table Requirement(
	Name varchar(42) primary key
);

create table Pokemon_learn_skill(
	id integer, 
	Skill_name varchar(42),
	Requirement_name varchar(42),
	primary key (id, Skill_name, Requirement_name),
	foreign key (Skill_name) references Skill_with_Type(name),
	foreign key (id) references Pokemon_first_seen(id),
	foreign key (Requirement_name) references Requirement(name)
);

create table Pokemon_evolve(
	Evolve_from integer,
	Evolve_to integer,
	Requirement_name varchar(42),
	primary key (Evolve_from, Evolve_to,Requirement_name),
	foreign key (Evolve_from) references Pokemon_first_seen(id),
	foreign key (Evolve_to) references Pokemon_first_seen(id),
	foreign key (Requirement_name) references Requirement(name)
);

create table Pokemon_base_type(
	Base integer,
	Variety integer,
	primary key (Base, Variety),
	foreign key (Base) references Pokemon_first_seen(id),
	foreign key (Variety) references Pokemon_first_seen(id)
);

create table Pokemon_Episode_Trainer(
	Pokemon_id integer,
	Episode_generation integer,
	Episode_Number integer,
	Trainer_Name varchar(42),
	primary key(Pokemon_id, Episode_generation, Episode_Number, Trainer_name),
	foreign key (Pokemon_id) references Pokemon_first_seen(id),
	foreign key (Trainer_Name) references Trainer(Name),
	foreign key (Episode_generation, Episode_Number) references Episode_happen_in(Generation, Number)
);

Create table Trainer_Appear(
	Trainer_name varchar(42),
	Episode_generation integer,
	Episode_number integer,
	primary key(Trainer_name, Episode_generation, Episode_number),
	foreign key (Trainer_Name) references Trainer(Name),
	foreign key (Episode_generation, Episode_number) references Episode_happen_in(Generation, Number)
);
