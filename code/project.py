import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser

"# Pokemon Master"


@st.cache
def get_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


@st.cache
def query_db(sql: str):
    # print(f"Running query_db(): {sql}")

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)

    # Obtain data
    data = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df


"## Read tables"

sql_all_table_names = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';"
try:
    all_table_names = query_db(sql_all_table_names)["relname"].tolist()
    table_name = st.selectbox("Choose a table", all_table_names)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if table_name:
    f"Display the table"

    sql_table = f"SELECT * FROM {table_name};"
    try:
        df = query_db(sql_table)
        st.dataframe(df)
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
        )

"## Pokemon with Skills"

sql_skill_names = "SELECT name FROM Skill_with_Type;"
try:
    skill_names = query_db(sql_skill_names)["name"].tolist()
    skill_name = st.selectbox("Choose a skill", skill_names)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if skill_name:
    sql_skill = f"""
        SELECT P.name as Pokemon, PS.Requirement_name as Requirement 
        FROM Pokemon_learn_skill PS, Pokemon_first_seen P 
        WHERE PS.Skill_name = '{skill_name}' 
        AND PS.id = P.id;"""
    try:
        df = query_db(sql_skill)
        st.dataframe(df)
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
        )

"## Pokemon Evolution"

sql_pokemon_names = "SELECT name FROM Pokemon_first_seen;"
try:
    pokemon_names = query_db(sql_pokemon_names)["name"].tolist()
    pokemon_name = st.selectbox("Choose a Pokemon", pokemon_names)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if pokemon_name:
    sql_pokemon = f"""
        SELECT E.requirement_name as requirement, P2.name as name, P2.HP as HP, P2.Atk as Atk, P2.Def as Def, P2.Special_Atk as Special_Atk, P2.Special_Def as Special_Def, P2.Speed as Speed
        FROM Pokemon_evolve E, Pokemon_first_seen P1, Pokemon_first_seen P2
        WHERE P1.name = '{pokemon_name}'
        AND P1.id = E.Evolve_from
        AND P2.id = E.Evolve_to;"""
    try:
        df = query_db(sql_pokemon)
        st.dataframe(df)
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
        )

"## Analyzing different type in customized data"

try:
    sql_prop = f"""
        SELECT MAX(P.HP) HP, MAX(P.Atk) ATK,  MAX(P.Def) DEF, MAX(P.Special_Atk) SATK, MAX(P.Special_Def) SDEF, MAX(P.Speed) Speed, MAX(P.HP+P.Atk+P.Def+P.Special_Atk+P.Special_Def+P.Speed) SS
        FROM Pokemon_first_seen P;"""
    prop = query_db(sql_prop).loc[0]
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

try:
    minimum_HP = st.slider("Choose your minimum HP", 0, int(prop["hp"]),0)
    minimum_ATK = st.slider("Choose your minimum Attack", 0, int(prop["atk"]),0)
    minimum_DEF = st.slider("Choose your minimum Defense", 0, int(prop["def"]),0)
    minimum_SATK = st.slider("Choose your minimum Special Attack", 0, int(prop["satk"]),0)
    minimum_SDEF = st.slider("Choose your minimum Special Defense", 0, int(prop["sdef"]),0)
    minimum_SP = st.slider("Choose your minimum Speed", 0, int(prop["speed"]),0)
    minimum_SS = st.slider("Choose your minimum of species strength (total number of each property)", 0 , int(prop["ss"]),0)
    passport = minimum_HP and minimum_DEF and minimum_ATK and minimum_SATK and minimum_SDEF and minimum_SP and minimum_SS
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

sql_type_data = f"""
    SELECT PT.Type_name, COUNT(*) quantity
    FROM Pokemon_first_seen P, Pokemon_have_Type PT
    WHERE PT.id = P.id
    AND P.HP >= '{minimum_HP}'
    AND P.Atk >= '{minimum_ATK}'
    AND P.Def >= '{minimum_DEF}'
    AND P.Special_Atk >= '{minimum_SATK}'
    AND P.Special_Def >= '{minimum_SDEF}'
    AND P.Speed >= '{minimum_SP}'
    AND P.HP+P.Atk+P.Def+P.Special_Atk+P.Special_Def+P.Speed >= '{minimum_SS}'
    GROUP BY PT.Type_name;"""
try:
    df = query_db(sql_type_data)
    st.dataframe(df)
except:
    st.write(
        "Sorry! Something went wrong with your query, please try again."
    )

"## What will the type be multiplied when encounter enemy"

sql_type_names = "SELECT name FROM type;"
sql_pokemon_names = "SELECT name FROM pokemon_first_seen;"
try:
    atk_type_names = query_db(sql_type_names)["name"].tolist()
    pokemon_names = query_db(sql_pokemon_names)["name"].tolist()
    atk_type_name = st.selectbox("Choose your type of attack", atk_type_names)
    pokemon_name = st.selectbox("Choose your enemy", pokemon_names)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if atk_type_name and pokemon_name:
    sql_poketype = f"""
        SELECT PT.Type_name
        FROM Pokemon_first_seen P, Pokemon_have_type PT
        WHERE P.name = '{pokemon_name}'
        AND PT.id = P.id;"""
    try:
        multiply = 1
        for def_type_name in query_db(sql_poketype)["type_name"].tolist():
            sql_damage = f"""
                SELECT D.multiply
                FROM Damage D
                WHERE D.Type_name_from = '{atk_type_name}'
                AND D.Type_name_to = '{def_type_name}';"""
            ##if len(query_db(sql_damage)["multiply"].tolist()) != 0:
            multiply *= (query_db(sql_damage).loc[0])["multiply"]
        st.write(f"Attack from {atk_type_name} to {pokemon_name} will be multiplied by {multiply}")
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

"## What skill sould you learn to beat enemy"

sql_pokemon_names = "SELECT P.name FROM pokemon_first_seen P, Pokemon_learn_skill PS WHERE P.id = PS.id GROUP BY P.name HAVING count(*) > 0;"
try:
    pokemon_names = query_db(sql_pokemon_names)["name"].tolist()
    p1_pokemon_name = st.selectbox("Choose your Pokemon", pokemon_names)
    p2_pokemon_name = st.selectbox("Choose enemies' Pokemon", pokemon_names)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if p1_pokemon_name and p2_pokemon_name:
    sql_p1_pokeskill = f"""
        SELECT S.name, S.chance, S.damage, S.Type_name
        FROM Pokemon_first_seen P, Pokemon_learn_skill PS, Skill_with_Type S
        WHERE P.name = '{p1_pokemon_name}'
        AND P.id = PS.id
        AND PS.skill_name = S.name;"""
    sql_p2_poketype = f"""
        SELECT PT.Type_name
        FROM Pokemon_first_seen P, Pokemon_have_type PT
        WHERE P.name = '{p2_pokemon_name}'
        AND PT.id = P.id;"""
    try:
        max_skill_damage = -1
        max_skill_name = None
        best_skill_damage = -1
        best_skill_name = None
        for skill in query_db(sql_p1_pokeskill).iterrows():
            skill_name, skill_chance, skill_damage, skill_type_name = (
                skill[1]["name"],
                skill[1]["chance"],
                skill[1]["damage"],
                skill[1]["type_name"],
            )
            multiply = 1
            for def_type_name in query_db(sql_p2_poketype)["type_name"].tolist():
                sql_damage = f"""
                    SELECT D.multiply
                    FROM Damage D
                    WHERE D.Type_name_from = '{atk_type_name}'
                    AND D.Type_name_to = '{def_type_name}';"""
                ##if len(query_db(sql_damage)["multiply"].tolist()) != 0:
                multiply *= (query_db(sql_damage).loc[0])["multiply"]
            if skill_damage * multiply > max_skill_damage:
                max_skill_name = skill_name
                max_skill_damage = skill_damage * multiply
            if skill_damage * multiply * skill_chance/100 > best_skill_damage:
                best_skill_name = skill_name
                best_skill_damage = skill_damage * multiply * skill_chance/100      
        st.write(f"You should use {max_skill_name} to hit {p2_pokemon_name} to cause {max_skill_damage} with highest value")
        st.write(f"You should use {best_skill_name} to hit {p2_pokemon_name} to cause {best_skill_damage} with highest exxpected value")
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")
        
"## Duel of champions"
st.write("These are the champions from differnt regions. Select their names.")
sql_champion_names = "SELECT name, champion FROM place_champion;"
try:
    champion_names1 = query_db(sql_champion_names)["champion"]
    champion_names2 = query_db(sql_champion_names)["champion"]
    champion1 = st.radio("Choose a contestant1", champion_names1)
    champion2 = st.radio("Choose a contestant2", champion_names2)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")
    
if champion1 and champion2 and champion1 == champion2:
    st.write("Sorry! Two contestants are the same. Please choose again")

if champion1 and champion2 and champion1 != champion2:
    sql_champion1_champion2_pokemons = f"""
        SELECT champ1.pokemon_ID as champ1, champ2.pokemon_ID as champ2
        FROM pokemon_episode_trainer champ1, pokemon_episode_trainer champ2
        WHERE champ1.trainer_name = '{champion1}'
        and champ2.trainer_name = '{champion2}';"""
    try:
        champ1_champ2_combination = query_db(sql_champion1_champion2_pokemons)
        champ_duel_rand_pokemon = champ1_champ2_combination.sample()
        #st.dataframe(champ_duel_rand_pokemon)
        champ1_pokemon_id = champ_duel_rand_pokemon["champ1"].iloc[0]
        champ2_pokemon_id = champ_duel_rand_pokemon["champ2"].iloc[0]
        sql_champion1_champion2_who_wins = f"""
            SELECT champ1.name as champ1_pokemon, champ2.name as champ2_pokemon, champ1.HP as champ1_hp, champ1.def as champ1_def, champ1.atk as champ1_atk, champ2.hp as champ2_hp, champ2.def as champ2_def, champ2.atk as champ2_atk, c1skill.skill_name as champ1_skill, c2skill.skill_name as champ2_skill, c1skill_data.chance as champ1_skill_chance, c1skill_data.damage as champ1_skill_damage, c2skill_data.chance as champ2_skill_chance, c2skill_data.damage as champ2_skill_damage
            FROM pokemon_first_seen champ1, pokemon_first_seen champ2, pokemon_learn_skill c1skill, pokemon_learn_skill c2skill, skill_with_type c1skill_data, skill_with_type c2skill_data
            WHERE champ1.id = '{champ1_pokemon_id}'
            and champ2.id = '{champ2_pokemon_id}'
            and c1skill.id = '{champ1_pokemon_id}'
            and c2skill.id = '{champ2_pokemon_id}'
            and c1skill.skill_name = c1skill_data.name
            and c2skill.skill_name = c2skill_data.name;"""
        champs_duel_data = query_db(sql_champion1_champion2_who_wins).sample()
        st.dataframe(champs_duel_data)
        champ1_pokemon = champs_duel_data["champ1_pokemon"].iloc[0]
        champ2_pokemon = champs_duel_data["champ2_pokemon"].iloc[0]
        champ1_use_skill = champs_duel_data["champ1_skill"].iloc[0]
        champ2_use_skill = champs_duel_data["champ2_skill"].iloc[0]
        champ1_skill_chance = champs_duel_data["champ1_skill_chance"].iloc[0]
        champ2_skill_chance = champs_duel_data["champ2_skill_chance"].iloc[0]
        champ1_skill_damage = champs_duel_data["champ1_skill_damage"].iloc[0]
        champ2_skill_damage = champs_duel_data["champ2_skill_damage"].iloc[0]
        champ1_pokemon_hp = champs_duel_data["champ1_hp"].iloc[0]
        champ2_pokemon_hp = champs_duel_data["champ2_hp"].iloc[0]
        champ1_pokemon_atk = champs_duel_data["champ1_atk"].iloc[0]
        champ2_pokemon_atk = champs_duel_data["champ2_atk"].iloc[0]
        champ1_pokemon_def = champs_duel_data["champ1_def"].iloc[0]
        champ2_pokemon_def = champs_duel_data["champ2_def"].iloc[0]
        st.write(f"{champion1} send {champ1_pokemon} and use {champ1_use_skill} has {champ1_skill_chance}% to hit {champ1_skill_damage}")
        st.write(f"{champion2} send {champ2_pokemon} and use {champ2_use_skill} has {champ2_skill_chance}% to hit {champ2_skill_damage}")
        if (int(champ1_pokemon_hp) + int(champ1_pokemon_def) - int(champ2_skill_chance) * int(champ2_skill_damage) > int(champ2_pokemon_hp) + int(champ2_pokemon_def) - int(champ1_skill_chance) * int(champ1_skill_damage)):
            st.write(f"{champ1_pokemon} took {champ2_skill_damage} damage. But {champ1_pokemon} has higher HP and Def. {champion1} wins this round.")
        else:
            st.write(f"{champ2_pokemon} took {champ1_skill_damage} damage. But {champ2_pokemon} has higher HP and Def. {champion2} wins this round.")
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")
        
"## Who would you choose???"
st.write("There are four first partners to choose from. Who is your favorite")
sql_starter_names = "SELECT name FROM pokemon_first_seen where (id = 1 or id = 4 or id =7 or id = 25);"
try:
    starter_names = query_db(sql_starter_names)["name"].tolist()
    starter_chosen = st.selectbox("Choose your favorite partner", starter_names)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")
if starter_chosen:
    sql_starter_comparison = f"""
        SELECT p.name, p.hp, p.atk, p.def, st.type_name, ps.skill_name, pe1.evolve_to as first_evolve_to, pe1.requirement_name as first_evolve_requirement
        FROM pokemon_first_seen p, skill_with_type st, pokemon_learn_skill ps, pokemon_evolve pe1
        where (p.id = 1 or p.id = 4 or p.id =7 or p.id = 25)
        and ps.id = p.id
        and st.name = ps.skill_name
        and pe1.evolve_from = p.id;"""
    sql_who_has_better_stats = f"""
        SELECT p.name, ROW_NUMBER() OVER(ORDER BY SUM(p.hp + p.atk + p.def + p.special_atk + p.special_def + p.speed) desc) AS stats_ranking
        FROM pokemon_first_seen p
        where (p.id = 1 or p.id = 4 or p.id =7 or p.id = 25)
        group by p.name;"""
    sql_skill_counts = f"""
        SELECT p.name, COUNT(ps.skill_name)
        FROM pokemon_first_seen p, pokemon_learn_skill ps
        where (p.id = 1 or p.id = 4 or p.id =7 or p.id = 25)
        and ps.id = p.id
        group by p.name;"""
    sql_skill_types_counts = f"""
        SELECT p.name, st.type_name, COUNT(*)
        FROM pokemon_first_seen p, skill_with_type st, pokemon_learn_skill ps
        where (p.id = 1 or p.id = 4 or p.id =7 or p.id = 25)
        and ps.id = p.id
        and st.name = ps.skill_name
        group by p.name, st.type_name
        order by p.name;"""
    sql_evolve_sequence = f"""
        SELECT evolve_results.name, p2.name as evolve_1st, evolve_results.evolve_1st_re, p3.name as evolve_2nd, evolve_results.evolve_2nd_re 
        FROM 
            (SELECT p.name, pe1.evolve_to as evolve_1st, pe1.Requirement_name as evolve_1st_re, pe2.evolve_to as evolve_2nd, pe2.Requirement_name as evolve_2nd_re FROM pokemon_first_seen p, pokemon_evolve pe1 full outer join pokemon_evolve pe2 on (pe1.evolve_to = pe2.evolve_from)
            where (p.id = 1 or p.id = 4 or p.id =7 or p.id = 25)
            and p.id = pe1.evolve_from
            group by p.name, pe1.evolve_to, pe2.evolve_to, pe1.Requirement_name, pe2.Requirement_name) as evolve_results
            full outer join 
            pokemon_first_seen p2 on evolve_results.evolve_1st = p2.id
            full outer join 
            pokemon_first_seen p3 on evolve_results.evolve_2nd = p3.id
        where evolve_results.name = 'Bulbasaur' or evolve_results.name = 'Charmander' or evolve_results.name = 'Squirtle' or evolve_results.name = 'Pikachu';"""
    try:
        starter_comparison = query_db(sql_starter_comparison)
        stats_ranking = query_db(sql_who_has_better_stats)
        chosen_ranking = stats_ranking.loc[stats_ranking['name'] == starter_chosen]
        skill_counts = query_db(sql_skill_counts)
        chosen_skill_counts = skill_counts.loc[skill_counts['name'] == starter_chosen]
        skill_types_counts = query_db(sql_skill_types_counts)
        chosen_types_counts = skill_types_counts.loc[skill_types_counts['name'] == starter_chosen]
        evolve_sequence = query_db(sql_evolve_sequence)
        chosen_evolve_sequence = evolve_sequence.loc[evolve_sequence['name'] == starter_chosen]
        st.write("Here's the comparison chart: ")
        st.dataframe(starter_comparison)
        st.write("The stats of your partner is ranked at: ")
        st.dataframe(chosen_ranking)
        st.write("The number of skills your partner can learn is: ")
        st.dataframe(chosen_skill_counts)
        st.write("The types of skills your partner can learn are: ")
        st.dataframe(chosen_types_counts)
        st.write("Your partner can evolve to: ")
        st.dataframe(chosen_evolve_sequence)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")
