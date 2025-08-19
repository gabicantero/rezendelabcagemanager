import streamlit as st
import pandas as pd
import datetime
import os 

st.set_page_config(page_title="Rat Cage Manager", layout="wide")
st.title("Animal Cage Manager")

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

PROJECTS_PATH = os.path.join(BASE_DIR, "projects.csv")
DATA_PATH = os.path.join(BASE_DIR, "data.csv")

# Funções para carregar e salvar dados 
def load_data():
    try:
        return pd.read_csv("rat_data.csv")
    except FileNotFoundError:
        cols = ["ID", "Project", "Cage", "DOB", "Sex", "Pregnant?", "Notes",
                "Next Experiment", "Experiment Date", "Expected DOB Puppies",
                "Real DOB Puppies", "Weaning Date", "Milking Days Done"]
        return pd.DataFrame(columns=cols)

def load_projects():
    if os.path.exists(PROJECTS_PATH):
        return pd.read_csv(PROJECTS_PATH)
    else:
        return pd.DataFrame()

def save_projects(df):
    df.to_csv("projects.csv", index=False)

# Carrega os dados no início da página
projects_df = load_projects()

# Sessão para controlar adicionar experimentos no form
if "new_exp_count" not in st.session_state:
    st.session_state.new_exp_count = 1
# Carrega os dados no início da página

# Controlar o "adicionar experiments" no form
if "new_exp_count" not in st.session_state:
    st.session_state.new_exp_count = 1

def save_data(df):
    df.to_csv("rat_data.csv", index=False)

# Carregar dados
data = load_data()
projects_df = load_projects()

# Lista de projetos para seleção (Add Animal, Cages)
projects_list = list(projects_df["Project"].unique())
if not projects_list:
    projects_list = ["No Projects Yet"]

# Menu lateral 
page = st.sidebar.selectbox("Navigation", ["Home", "Add Animal", "Cages", "Projects"])

# Página Home 
if page == "Home":
    st.subheader("Welcome to the Rezende's Lab Animal Manager App!")
    st.markdown("Use the sidebar to navigate between pages.")

# Página Add Animal
elif page == "Add Animal":
    st.subheader("Add a New Animal")

    id = st.text_input("Animal ID")
    project = st.selectbox("Project", projects_list)
    cage = st.text_input("Cage Number")
    dob = st.date_input("Date of Birth")
    sex = st.selectbox("Sex", ["Male", "Female"])
    pregnancy = st.selectbox("Pregnant?", ["No", "Yes"])
    notes = st.text_area("Notes")
    next_action = st.text_input("Next Experiment")
    bree_expe = st.selectbox("Breeder or Experimental?", ["Breeder", "Experimental","None"])

    add_exp_date = st.checkbox("Add Experiment Date?")
    action_date = None
    if add_exp_date:
        action_date = st.date_input("Experiment Date")

    edbp = rdbp = weaning = None
    if pregnancy == "Yes":
        edbp = st.date_input("Expected Date of Birth of the Puppies")
        rdbp = st.date_input("Real Date of Birth of the Puppies")
        weaning = st.date_input("Date of Weaning")

    milk_done = []
    if next_action.lower() == "milking":
        milk_days = ['1','2','3','4','5', '6','7','8', '9','10','11', '12','13','14', '15','16','17','18','19','20' '21']
        milk_done = st.multiselect("Milking days done", milk_days)

    if st.button("Add Animal"):
        new_row = {
            "ID": id,
            "Project": project,
            "Cage": cage,
            "DOB": dob,
            "Sex": sex,
            "Breeder or Experimental?": bree_expe,
            "Pregnant?": pregnancy,
            "Notes": notes,
            "Next Experiment": next_action,
            "Experiment Date": action_date,
            "Expected DOB Puppies": edbp,
            "Real DOB Puppies": rdbp,
            "Weaning Date": weaning,
            "Milking Days Done": ",".join(milk_done) if milk_done else None
        }
        data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
        save_data(data)
        st.success(f"Animal {id} added successfully!")
        # Atualiza lista de projetos
        if project not in projects_list:
            projects_list.append(project)

# Página Cages 
elif page == "Cages":
    st.subheader("🔲 Cage Overview")

    if data.empty:
        st.info("No animals registered yet.")
    else:
        # Lista de projetos válidos
        projects_list = projects_df["Project"].dropna().unique().tolist()
        projects_list = [p for p in projects_list if p.strip() != ""]

        # 1️⃣ Filtro por projeto
        selected_project = st.selectbox("Filter by Project", ["All"] + projects_list)

        if selected_project == "All":
            filtered_data = data.copy()
        else:
            filtered_data = data[data["Project"] == selected_project]

        if filtered_data.empty:
            st.warning("No animals in this project.")
        else:
            # 2️⃣ Filtro por tipo de animal (Breeder/Experimental)
            type_options = ["Breeder", "Experimental"]
            selected_types = st.multiselect("Filter by Type", type_options, default=type_options)
            filtered_data = filtered_data[filtered_data["Breeder or Experimental?"].isin(selected_types)]

            if filtered_data.empty:
                st.warning("No animals match this filter.")
            else:
                # 3️⃣ Mostrar cages resumidas
                st.write("### Cages Overview")
                cages_summary = filtered_data.groupby("Cage").agg(
                    num_animals=("ID", "count"),
                    num_males=("Sex", lambda x: (x=="Male").sum()),
                    num_females=("Sex", lambda x: (x=="Female").sum()),
                    next_experiment=("Next Experiment", lambda x: x.dropna().iloc[-1] if not x.dropna().empty else "None")
                ).reset_index()

                # Exibir cada cage como um botão/expander
                for _, cage_row in cages_summary.iterrows():
                    cage_expander = st.expander(
                        f"Cage {cage_row['Cage']} - {cage_row['num_animals']} animals "
                        f"(M: {cage_row['num_males']}, F: {cage_row['num_females']}) "
                        f"⚠ Next: {cage_row['next_experiment']}"
                    )

                    with cage_expander:
                        cage_data = filtered_data[filtered_data["Cage"] == cage_row["Cage"]]
                        st.dataframe(cage_data[["ID", "Sex", "Pregnant?", "Next Experiment", "DOB"]])

                        # Seleção de animal individual para editar
                        selected_animal_index = st.selectbox(
                            "Select an animal to edit",
                            cage_data.index,
                            format_func=lambda x: f"{cage_data.loc[x, 'ID']} - {cage_data.loc[x, 'Sex']}"
                        )

                        if "show_edit" not in st.session_state:
                            st.session_state.show_edit = False

                        if st.button("Edit selected animal info", key=f"edit_{cage_row['Cage']}"):
                            st.session_state.show_edit = not st.session_state.show_edit

                        if st.session_state.show_edit:
                            row = cage_data.loc[selected_animal_index]
                            with st.form(f"edit_animal_{selected_animal_index}"):
                                id = st.text_input("Animal ID", value=row["ID"])
                                project = st.selectbox("Project", projects_list,
                                                       index=projects_list.index(row["Project"]) if row["Project"] in projects_list else 0)
                                cage = st.text_input("Cage Number", value=row["Cage"])
                                dob = st.date_input("Date of Birth", pd.to_datetime(row["DOB"]))
                                sex = st.selectbox("Sex", ["Male", "Female"], index=0 if row["Sex"] == "Male" else 1)
                                pregnancy = st.selectbox("Pregnant?", ["No", "Yes"], index=0 if row["Pregnant?"]=="No" else 1)
                                notes = st.text_area("Notes", value=row["Notes"])
                                next_action = st.text_input("Next Experiment", value=row["Next Experiment"])
                                bree_expe = st.selectbox("Breeder or Experimental", ["Breeder","Experimental","None"],
                                                        index=0 if row["Breeder or Experimental?"]=="Breeder" else 1)

                                save_changes = st.form_submit_button("Save Changes")
                                if save_changes:
                                    data.loc[selected_animal_index] = [
                                        id, project, cage, dob, sex, pregnancy, notes,
                                        next_action, bree_expe, row["Experiment Date"],
                                        row["Expected DOB Puppies"], row["Real DOB Puppies"], row["Weaning Date"],
                                        row["Milking Days Done"]
                                    ]
                                    save_data(data)
                                    st.success("Animal updated successfully!")
                                    st.session_state.show_edit = False

            if st.button("Delete Animal"):
                data = data.drop(selected_animal_index)
                save_data(data)
                st.warning("Animal deleted successfully!")
                st.session_state.show_edit = False

# Página Projects 
if page == "Projects":
    st.subheader("📁 Projects")

    # Mostrar projetos existentes
    for idx, row in projects_df.iterrows():
        with st.expander(f"📂 {row['Project']}"):
            st.write(row["Description"])

            # Pegar colunas de experimentos
            exp_cols = [c for c in projects_df.columns if c.startswith("Exp") and "Name" in c]
            exp_nums = sorted([int(c.replace("Exp", "").replace("Name", "").strip()) for c in exp_cols])

            done_count = 0
            total_count = len(exp_nums)

            for num in exp_nums:
                name_col = f"Exp{num} Name"
                date_col = f"Exp{num} Date"
                done_col = f"Exp{num} Done"

                if done_col not in projects_df.columns:
                    projects_df[done_col] = False

                exp_name = projects_df.at[idx, name_col]
                exp_date = projects_df.at[idx, date_col]
                exp_done = st.checkbox(f"{exp_name} ({exp_date})", value=bool(row.get(done_col, False)),
                                       key=f"done_{idx}_{num}")

                if exp_done:
                    done_count += 1
                projects_df.at[idx, done_col] = exp_done

            # Calcular progresso
            percent_done = int((done_count / total_count) * 100) if total_count > 0 else 0
            if percent_done == 100:
                color = "green"
            elif percent_done >= 75:
                color = "lightgreen"
            elif percent_done >= 50:
                color = "yellow"
            else:
                color = "red"

            st.markdown(f"""
            <div style='width:100%;background-color:lightgray;border-radius:5px;'>
                <div style='width:{percent_done}%;background-color:{color};padding:5px;border-radius:5px;text-align:center;'>
                    {percent_done}%
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Botão para deletar projeto
        if st.button("Delete Project", key=f"delete_proj_{idx}"):
            projects_df = projects_df.drop(idx).reset_index(drop=True)
            save_projects(projects_df)
            st.success(f"Project '{row['Project']}' deleted successfully!")
            st.experimental_rerun()

            save_projects(projects_df)

    # Formulário para adicionar novo projeto
    st.markdown("---")
    st.subheader("Add New Project")

    with st.form("add_project_form"):
        new_proj_name = st.text_input("Project Name")
        new_proj_desc = st.text_area("Project Description")
        n_exp = st.number_input("Number of Experiments", min_value=1, max_value=10, value=3, step=1)

        new_exp_names = []
        new_exp_dates = []

        for i in range(1, n_exp + 1):
            new_exp_names.append(st.text_input(f"Experiment {i} Name", key=f"new_exp_name_{i}"))
            new_exp_dates.append(st.text_input(f"Planned Date for Starting Experiment {i} (YYYY-MM-DD)", key=f"new_exp_date_{i}"))

        submit_new_proj = st.form_submit_button("Add Project")

        if submit_new_proj:
            if new_proj_name.strip() == "":
                st.error("Project name cannot be empty.")
            elif new_proj_name in projects_df["Project"].values:
                st.error("Project with this name already exists.")
            else:
                new_row = {
                    "Project": new_proj_name,
                    "Description": new_proj_desc
                }
                for i in range(1, n_exp + 1):
                    new_row[f"Exp{i} Name"] = new_exp_names[i - 1]
                    new_row[f"Exp{i} Date"] = new_exp_dates[i - 1]
                    new_row[f"Exp{i} Done"] = False

                projects_df = pd.concat([projects_df, pd.DataFrame([new_row])], ignore_index=True)
                save_projects(projects_df)
                st.success(f"Project '{new_proj_name}' added!")