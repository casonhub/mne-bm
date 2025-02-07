from flask import Flask, render_template, request,jsonify
import pandas as pd

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html')

# Load data
biomarker_file = 'data/biomarkers.xlsx'
cognitive_skill_file = 'data/2Cognitive_Skills_Data.xlsx'
# Load the Excel files
data_biomarkers = pd.read_excel('data/Cognitive_BioMarker.xlsx')
data_skills = pd.read_excel('data/2Cognitive_Skills_Data.xlsx')
# Load data for each app
data_file = 'data/2Cognitive_Skills_Data.xlsx'  # Replace with actual file path

@app.route('/biomarkers', methods=['GET', 'POST'])
def biomarkers():
    # Load the Excel file and process data
    file_path = 'data/biomarkers_new.xlsx'
    df = pd.read_excel(file_path)

    # Convert data into a dictionary where biomarkers map to their applicable disorders and details
    biomarker_dict = {}
    for _, row in df.iterrows():
        biomarker = row['Bio_Markers']
        applicable_disorders = {}
        for disorder, value in row.items():
            if disorder != 'Bio_Markers' and pd.notna(value):  # Check for non-null values
                applicable_disorders[disorder] = value  # Store the detailed information
        biomarker_dict[biomarker] = applicable_disorders

    selected_biomarkers = []
    associated_disorders = {}

    if request.method == 'POST':
        # Retrieve selected biomarkers from the form
        selected_biomarkers = request.form.get('selected_biomarkers', '').split(',')
        print(f"Selected Biomarkers: {selected_biomarkers}")  # Debug: Print selected biomarkers

        # Apply AND logic: Find common disorders and their associated details
        if selected_biomarkers:
            # Initialize with disorders of the first selected biomarker
            initial_biomarker = selected_biomarkers[0]
            if initial_biomarker in biomarker_dict:
                common_disorders = {
                    disorder: [(initial_biomarker, biomarker_dict[initial_biomarker][disorder])]
                    for disorder in biomarker_dict[initial_biomarker]
                }
            else:
                common_disorders = {}

            # Intersect with disorders of remaining selected biomarkers
            for biomarker in selected_biomarkers[1:]:
                if biomarker in biomarker_dict:
                    # Update common_disorders to include only shared disorders with their details
                    common_disorders = {
                        disorder: common_disorders[disorder] + [(biomarker, biomarker_dict[biomarker][disorder])]
                        for disorder in common_disorders.keys() & biomarker_dict[biomarker].keys()
                    }
                else:
                    # If a biomarker is not in the dataset, the result will be empty
                    common_disorders = {}
                    break

            # Format the disorders and their associated details
            for disorder, biomarker_details in common_disorders.items():
                detailed_info = ", ".join(
                    [f"{biomarker}: {details}" for biomarker, details in biomarker_details]
                )
                associated_disorders[disorder] = detailed_info

        print(f"Associated Disorders: {associated_disorders}")  # Debug: Print associated disorders

    # Prepare output for display
    disorders_output = [
    f"<strong>{disorder}</strong>: " + ", ".join(
        [f"<strong>{biomarker}</strong>: {details}" for biomarker, details in common_disorders[disorder]]
    )
    for disorder in associated_disorders.keys()
    ]

    return render_template(
        'biomarkers.html',
        selected_biomarkers=selected_biomarkers,
        disorders=disorders_output,
        biomarker_data=df['Bio_Markers'].unique()
    )



@app.route('/skills', methods=['GET', 'POST'])
def skills():
    # Load the Excel file and process data
    file_path = 'data/Cognitive_skills_new.xlsx'
    df = pd.read_excel(file_path)

    # Convert data into a dictionary where Bio_M_Skills map to their applicable cognitive impairments and regions
    biomarker_dict = {}
    for _, row in df.iterrows():
        biomarker = row['Bio_M_Skills']
        applicable_disorders = {}
        for column, value in row.items():
            if column != 'Bio_M_Skills' and pd.notna(value):
                applicable_disorders[column] = value
        biomarker_dict[biomarker] = applicable_disorders

    disorders_with_biomarkers = []
    selected_biomarkers = []

    if request.method == 'POST':
        # Retrieve selected Bio_M_Skills from the form
        selected_biomarkers = request.form.get('selected_biomarkers', '').split(',')
        print(f"Selected Bio_M_Skills: {selected_biomarkers}")  # Debug: Print selected Bio_M_Skills

        if selected_biomarkers:
            # Initialize with disorders of the first selected biomarker
            initial_biomarker = selected_biomarkers[0]
            if initial_biomarker in biomarker_dict:
                common_disorders = set(biomarker_dict[initial_biomarker].keys())
            else:
                common_disorders = set()

            # Intersect with disorders of remaining selected biomarkers
            for biomarker in selected_biomarkers[1:]:
                if biomarker in biomarker_dict:
                    skill_disorders = set(biomarker_dict[biomarker].keys())
                    common_disorders &= skill_disorders
                else:
                    common_disorders = set()
                    break

            # Collect disorders along with their biomarkers for display
            for disorder in common_disorders:
                biomarkers = {
                    biomarker: biomarker_dict[biomarker][disorder]
                    for biomarker in selected_biomarkers if disorder in biomarker_dict[biomarker]
                }
                disorders_with_biomarkers.append({'disorder': disorder, 'biomarkers': biomarkers})

        print(f"Disorders and associated biomarkers: {disorders_with_biomarkers}")  # Debug: Print results

    return render_template(
        'skills.html',
        selected_biomarkers=selected_biomarkers,
        disorders_with_biomarkers=disorders_with_biomarkers,
        biomarker_data=df['Bio_M_Skills'].unique()
    )



# Bio_M_Skills selection route
@app.route('/cognitive', methods=['GET', 'POST'])
def cognitive():
    # Load the Excel file and process data
    file_path = 'data/Cognitive_Skills_Data.xlsx'
    df = pd.read_excel(file_path)

    # Convert data into a dictionary where Bio_M_Skills map to their applicable disorders and biomarkers
    biomarker_dict = {}
    disorder_columns = df.columns[1:]  # Columns after 'Bio_M_Skills' contain disorders
    for _, row in df.iterrows():
        skill = row['Bio_M_Skills']
        biomarker_dict[skill] = {
            disorder: row[disorder] for disorder in disorder_columns if pd.notnull(row[disorder])
        }

    selected_biomarkers = []
    disorders_with_biomarkers = []  # To store disorders along with their biomarkers

    if request.method == 'POST':
        # Retrieve selected Bio_M_Skills from the form
        selected_biomarkers = request.form.get('selected_biomarkers', '').split(',')
        print(f"Selected Bio_M_Skills: {selected_biomarkers}")  # Debug: Print selected skills

        # Apply AND logic: Find disorders common to all selected Bio_M_Skills
        if selected_biomarkers:
            # Initialize with disorders of the first selected skill
            initial_skill = selected_biomarkers[0]
            if initial_skill in biomarker_dict:
                common_disorders = set(biomarker_dict[initial_skill].keys())
            else:
                common_disorders = set()

            # Intersect with disorders of remaining selected skills
            for skill in selected_biomarkers[1:]:
                if skill in biomarker_dict:
                    skill_disorders = set(biomarker_dict[skill].keys())
                    common_disorders &= skill_disorders
                else:
                    # If a skill is not in the dataset, the result will be empty
                    common_disorders = set()
                    break

            # Collect disorders along with their biomarkers for display
            for disorder in common_disorders:
                biomarkers = {
                    skill: biomarker_dict[skill][disorder]
                    for skill in selected_biomarkers if disorder in biomarker_dict[skill]
                }
                disorders_with_biomarkers.append({'disorder': disorder, 'biomarkers': biomarkers})

        print(f"Disorders and associated biomarkers: {disorders_with_biomarkers}")  # Debug: Print result

    return render_template(
        'cognitive.html',
        selected_biomarkers=selected_biomarkers,
        disorders_with_biomarkers=disorders_with_biomarkers,  # Pass disorders and biomarkers to the template
        biomarker_data=df['Bio_M_Skills'].unique()
    )





biomarker_data = pd.read_excel(biomarker_file, index_col=0)
cognitive_skill_data = pd.read_excel(cognitive_skill_file, index_col=0)


@app.route('/bmdisorders')
def bm_to_disorders():
    # Send biomarkers to the front end for selection
    biomarkers = biomarker_data.index.tolist()
    return render_template('bmdisordersskill.html', biomarkers=biomarkers)


@app.route('/get_results', methods=['POST'])
def get_results():
    # Get user-selected biomarkers
    selected_biomarkers = request.json.get('selected_biomarkers', [])
    if not selected_biomarkers:
        return jsonify({'error': 'No biomarkers selected'})

    # Ensure all selected biomarkers exist in the data
    missing_biomarkers = [b for b in selected_biomarkers if b not in biomarker_data.index]
    if missing_biomarkers:
        return jsonify({'error': f"The following biomarkers are not found: {', '.join(missing_biomarkers)}"})

    # Find mental disorders associated with all selected biomarkers (AND operation)
    disorder_sets = []
    for biomarker in selected_biomarkers:
        disorders = set(biomarker_data.columns[biomarker_data.loc[biomarker] == 'X'])
        disorder_sets.append(disorders)

    # Perform intersection across all sets of disorders
    if disorder_sets:
        mental_disorders = set.intersection(*disorder_sets)
    else:
        mental_disorders = set()

    # Find associated cognitive skills
    result = {}
    for disorder in mental_disorders:
        if disorder in cognitive_skill_data.columns:
            skills = cognitive_skill_data.index[cognitive_skill_data[disorder].notna()]
            result[disorder] = list(skills)

    return jsonify(result)


print("Biomarker Columns:", data_biomarkers.columns.tolist())
print("Skills Columns:", data_skills.columns.tolist())

print(data_skills.head())  # Print first few rows of the skills data

# Extract cognitive skills
available_skills = data_biomarkers['skill_disorders'].dropna().tolist()

@app.route('/cogskills')
def cogskills():
    return render_template('cogskills.html', skills=available_skills)

@app.route('/process', methods=['POST'])
def process():
    selected_skills = request.json.get('skills', [])
    if not selected_skills:
        return jsonify({"error": "No cognitive skills selected."})

    # Initialize disorders with all available disorders
    disorders = set(data_biomarkers.columns[2:])  # Exclude 'skill_disorders' and 'Major Dep'

    # Apply AND logic: Find disorders common to all selected skills
    for skill in selected_skills:
        skill_disorders = data_biomarkers.loc[
            data_biomarkers['skill_disorders'] == skill
        ].iloc[0, 2:].dropna()  # Start from index 2 to skip 'skill_disorders' and 'Major Dep'

        # Get disorders where there is an 'X'
        skill_disorders = set(skill_disorders.index[skill_disorders == 'X'])

        # Update disorders to keep only those common to all selected skills
        disorders &= skill_disorders  # Intersection of disorders

    results = {}

    # Define a mapping of cognitive skills to colors
    skill_colors = {
        "Sustained Attention": "#007bff",
        "Working Memory": "#28a745",
        "Cognitive Flexibility": "#ffc107",
        "Emotional Regulation": "#dc3545",
        # Add more skills and their associated colors as needed
    }

    # Single color for all biomarkers
    biomarker_color = "red"

    # If no common disorders exist, return an empty result
    if not disorders:
        return jsonify({disorder: [] for disorder in data_biomarkers.columns[2:]})

    # For each common disorder, find the biomarkers
    for disorder in disorders:
        results[disorder] = []
        for skill in selected_skills:
            biomarkers = data_skills.loc[data_skills['Bio_M_Skills'] == skill, disorder].dropna()
            print(f"Biomarkers for disorder '{disorder}' and skill '{skill}': {biomarkers}")  # Debugging output

            if not biomarkers.empty:
                biomarker_str = biomarkers.values[0].strip()  # Strip whitespace
                if biomarker_str:  # Check if biomarker string is not empty
                    skill_color = skill_colors.get(skill, "#007bff")  # Default to black if skill not found
                    results[disorder].append({
                        "cognitive_skill": skill,
                        "skill_color": skill_color,
                        "biomarkers": biomarker_str,
                        "biomarker_color": biomarker_color
                    })
                else:
                    print(f"Empty biomarker string for disorder '{disorder}' and skill '{skill}'")  # Debugging output
            else:
                print(f"No biomarkers found for disorder '{disorder}' and skill '{skill}'")  # Debugging output

    return jsonify(results)



cognitive_skills_df = pd.read_excel(data_file)

#Mental Disorders to Cognitive Skills
@app.route('/mental_disorders')
def mental_disorders():
    """Renders Mental Disorders to Cognitive Skills UI."""
    disorders = cognitive_skills_df.columns[1:].tolist()
    return render_template('mdskill.html', disorders=disorders)

@app.route('/get_skills', methods=['POST'])
def get_skills():
    """API to get cognitive skills based on selected mental disorders."""
    data = request.get_json()
    selected_disorders = data.get('disorders', [])
    results = []

    for index, row in cognitive_skills_df.iterrows():
        cognitive_skill = row['Bio_M_Skills']
        biomarker_info = {}

        for disorder in selected_disorders:
            if disorder in cognitive_skills_df.columns:
                biomarkers = row[disorder]
                if isinstance(biomarkers, str) and biomarkers.strip():
                    biomarker_info[disorder] = biomarkers.strip()

        if biomarker_info:
            results.append({
                'cognitive_skill': cognitive_skill,
                'biomarkers': biomarker_info
            })

    return jsonify(results)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
