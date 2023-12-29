import streamlit as st
import py3Dmol
from Bio import PDB
import io
from stmol import showmol
from Bio.PDB.Polypeptide import protein_letters_3to1


def extract_protein_sequence(pdb_content):
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("protein_structure", io.StringIO(pdb_content.decode("utf-8")))
    for model in structure:
        for chain in model:
            sequence = ""
            for residue in chain.get_residues():
                if PDB.is_aa(residue, standard=True):
                    res_name = residue.get_resname()
                    sequence += protein_letters_3to1.get(res_name, '?')
            return sequence

def generate_sequence_html(sequence):
    html_sequence = "<div class='sequence'>"
    for i, char in enumerate(sequence):
         if i > 0 and i % 50 == 0:
            html_sequence += "<br>"
         html_sequence += f"<span class='residue' title='Position: {i }'>{char}</span>"
    html_sequence += "</div>"
    return html_sequence

# Custom CSS for styling the tooltips
custom_css = """
<style>
.residue {
    cursor: pointer;
    margin-right: 2px;
}
.sequence {
    letter-spacing: 3px;
}
</style>
"""

st.title("Protein Structure Viewer")
st.sidebar.title("Protein Sequence Settings")
uploaded_file = st.sidebar.file_uploader("Upload a PDB file", type="pdb")

if uploaded_file is not None:
    sequence = extract_protein_sequence(uploaded_file.getvalue())
    if sequence is not None:
        pdb = uploaded_file.getvalue().decode("utf-8")
        st.text("Protein Sequence:")
        sequence_html = generate_sequence_html(sequence)
        st.markdown(custom_css + sequence_html, unsafe_allow_html=True)
    else:
        st.error("No sequence found.")


if uploaded_file is not None:
    sequence = extract_protein_sequence(uploaded_file.getvalue())
    if sequence is not None:
       letters = sequence

       def apply_colors(letters, color_ranges):
         result = ""
         last_index = 0
         for start, end, color in sorted(color_ranges, key=lambda x: x[0]):
        # Add uncolored part
          result += letters[last_index:start]
        # Add colored part
          result += f'<span style="color: {color};">' + letters[start:end+1] + '</span>'
          last_index = end + 1
    # Add any remaining uncolored part
         result += letters[last_index:]
         return result

# Color options
    color_options = ["Red", "Blue", "Green", "Yellow", "Violet","Pink","Orange","Cyan"]
    color_dict = {"Red": "red", "Blue": "blue", "Green": "green", "Yellow": "yellow", "Purple": "purple", "Pink": "pink", "Orange": "orange", "Cyan": "cyan"}



# Interface to input ranges and colors
    st.sidebar.title("Subsequence Color Settings")
    num_of_ranges = st.sidebar.number_input("How many subsequences?", min_value=0, value=0, step=1)

    color_ranges = []
    start_index=[]
    end_index=[]
    color_index=[]
    for i in range(num_of_ranges):
     st.sidebar.write(f"Subsequence {i+1}")
     start = st.sidebar.number_input(f"Start Index {i+1}", min_value=0, max_value=len(letters)-1, value=0, key=f"start{i}")
     end = st.sidebar.number_input(f"End Index {i+1}", min_value=0, max_value=len(letters)-1, value=len(letters)-1, key=f"end{i}")
     color = st.sidebar.selectbox(f"Color {i+1}", color_options, key=f"color{i}")
     selected_color = color_dict[color]
     color_ranges.append((start, end, selected_color))
     start_index.append(start)
     end_index.append(end)
     color_index.append(selected_color)
     



# Apply colors to the specified ranges only once, outside the loop
    highlighted_text = apply_colors(letters, color_ranges)

# Displaying the result

    style_options = ["stick", "cartoon", "line", "cross", "sphere"]

# Dropdown menu for selecting the style
    st.sidebar.title("Structure Style Settings")
    selected_style = st.sidebar.selectbox("Select a Style for the Protein", style_options)


    def render_mol(pdb):
      xyzview = py3Dmol.view(width=760,height=460)
      xyzview.addModel(pdb,'pdb')
      xyzview.setStyle({selected_style: {}})
      #xyzview.setStyle({'stick':{}})
      xyzview.setBackgroundColor('white')#('0xeeeeee')
      xyzview.zoomTo()
      for i in range(num_of_ranges):
         xyzview.addStyle({'resi': f'{start_index[i]}-{end_index[i]}'}, {'stick': {'color': f'{color_index[i]}'}})
         #xyzview.addlabel("")
     #xyzview.addStyle({'resi': '1-32'}, {'cartoon': {'color': 'green'}})
     #xyzview.addStyle({'resi': '1'}, {'cartoon': {'color': 'green'}} )
     #xyzview.addStyle( {'resi': '62-82'}, {'cartoon': {'color': 'blue'}})
     #xyzview.addStyle({'resi': '84-105'}, {'cartoon': {'color': 'black'}})
     #xyzview.addStyle({'resi': '106-116'}, {'cartoon': {'color': 'red'}})
      showmol(xyzview, height = 500,width=800)
    
   
    pdb = uploaded_file.getvalue().decode("utf-8")
    st.write("Protein Structure:")
    render_mol(pdb)

    st.markdown(highlighted_text, unsafe_allow_html=True)
