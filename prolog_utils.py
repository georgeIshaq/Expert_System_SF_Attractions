import csv
import io
import tempfile
import requests
import sys
from models import Colors, CSV_URL

# Utility: convert a comma-separated cell to a Prolog list
def to_prolog_list(cell_value: str) -> str:
    items = [item.strip() for item in cell_value.split(',') if item.strip()]
    inner = ",".join([f"'{item}'" for item in items])  # Quote each item properly
    return f"[{inner}]"

# Generate the Prolog knowledge base from the Google Sheet
def generate_kb() -> str:
    print(f"{Colors.CYAN}Fetching attraction data...{Colors.END}")
    
    try:
        resp = requests.get(CSV_URL)
        resp.raise_for_status()
        text = resp.text
    except Exception as e:
        print(f"{Colors.RED}Error fetching data: {e}{Colors.END}")
        sys.exit(1)
        
    reader = csv.DictReader(io.StringIO(text))

    lines = []
    # Declarations
    lines.append(":- dynamic known/3, multivalued/1, attraction/12.")
    lines.append("% Declare multivalued attributes")
    lines.append("multivalued(indoor_outdoor).")
    lines.append("multivalued(best_time).\n")

    # Facts
    attraction_count = 0
    for row in reader:
        name = row['Attraction Name'].replace("'", "\\'")
        type_ = row['Type']
        budget = row['Budget']
        time_needed = row['Time Needed']
        dist = row['Distance from Residence']
        io_cell = to_prolog_list(row['Indoor/Outdoor'])
        popularity = row['Popularity']
        phys = row['Physical Activity']
        best_times = to_prolog_list(row['Best Time'])
        access = row['Accessibility']
        desc = row['Description'].replace("'", "\\'")
        link = row['Link'].replace("'", "\\'")

        fact = (
            f"attraction('{name}',{type_},{budget},{time_needed},"
            f"{dist},{io_cell},{popularity},{phys},{best_times},{access},"
            f"'{desc}','{link}')."
        )
        lines.append(fact)
        attraction_count += 1

    print(f"{Colors.GREEN}Loaded {attraction_count} attractions successfully!{Colors.END}")

    # Askables
    lines.append("\n% --- Ask Implementation ---")
    lines.append("ask(A, V):-")
    lines.append("    known(yes, A, V), !.")
    lines.append("ask(A, V):-")
    lines.append("    known(_, A, V), !, fail.")
    lines.append("ask(A, V):-")
    lines.append("    \\+multivalued(A),")
    lines.append("    known(yes, A, V2),")
    lines.append("    V \\== V2, !, fail.")
    lines.append("ask(A, V):-")
    lines.append("    read_py(A, V, Y),")
    lines.append("    assertz(known(Y, A, V)),")
    lines.append("    Y == yes.\n")

    # Wrapper predicates
    wrappers = [
        'attraction_type', 'budget', 'time_available', 'distance_from_residence',
        'indoor_outdoor', 'popularity', 'physical_activity', 'time_of_day', 'accessibility'
    ]
    for w in wrappers:
        lines.append(f"{w}(X) :- ask({w}, X).")

    # Recommendation rule
    lines.append("\n% --- Recommendation Rule ---")
    lines.append("recommend(Name) :-")
    lines.append("    attraction(Name,Type,Budget,TimeNeeded,Dist,IO,Pop,Phys,BestTimes,Acc,Desc,Link),")
    lines.append("    attraction_type(Type),")
    lines.append("    budget(Budget),")
    lines.append("    time_available(TimeNeeded),")
    lines.append("    distance_from_residence(Dist),")
    lines.append("    % The indoor_outdoor matching allows attractions to match based on a value present in their IO list")
    lines.append("    % When user selects 'either', read_py will accept any IO value (indoor/outdoor/both)")
    lines.append("    % When an attraction has 'both' value, it will match with user selections of 'indoor' or 'outdoor'")
    lines.append("    member(IOVal, IO), indoor_outdoor(IOVal),")
    lines.append("    popularity(Pop),")
    lines.append("    physical_activity(Phys),")
    lines.append("    member(ChosenTime, BestTimes), time_of_day(ChosenTime),")
    lines.append("    % When user selects limited_accessibility, wheelchair_accessible locations are also included")
    lines.append("    accessibility(Acc).")
    
    # Add show_recommendation predicate to display details
    lines.append("\nshow_recommendation(Name) :-")
    lines.append("    attraction(Name,_,_,_,_,_,_,_,_,_,Desc,Link),")
    lines.append("    write_py(Name),")
    lines.append("    write_py(Desc),")
    lines.append("    write_py(Link).")

    kb = "\n".join(lines)
    tf = tempfile.NamedTemporaryFile(delete=False, suffix='.pl', mode='w', encoding='utf-8')
    tf.write(kb)
    tf.close()
    return tf.name 