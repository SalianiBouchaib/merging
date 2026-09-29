import streamlit as st
import io
from pypdf import PdfWriter

st.set_page_config(page_title="Fusionneur de PDF", layout="centered")

st.title("Fusionneur de fichiers PDF")
st.write("Cette application vous permet de fusionner plusieurs fichiers PDF en un seul document.")

# Chargement des fichiers
uploaded_files = st.file_uploader("Choisissez les fichiers PDF à fusionner", 
                                 type="pdf", 
                                 accept_multiple_files=True)

if uploaded_files:
    st.write(f"**{len(uploaded_files)}** fichiers chargés.")
    
    # Affichage des noms des fichiers
    for i, pdf_file in enumerate(uploaded_files):
        st.write(f"{i+1}. {pdf_file.name}")

    # Bouton pour réorganiser les fichiers
    st.write("Vous pouvez réorganiser les fichiers en modifiant l'ordre de chargement.")
    
    # Bouton pour fusionner
    if st.button("Fusionner les PDF"):
        if len(uploaded_files) > 1:
            writer = PdfWriter()
            fichiers_sans_signets = []
            
            try:
                # Ajout de chaque PDF au merger
                for pdf_file in uploaded_files:
                    pdf_file.seek(0)
                    pdf_data = pdf_file.getvalue()
                    start_pages = len(writer.pages)

                    try:
                        writer.append(io.BytesIO(pdf_data), import_outline=True)
                    except Exception:
                        # Repli: ignorer les signets si leur import échoue pour ce document.
                        while len(writer.pages) > start_pages:
                            writer.remove_page(start_pages)
                        writer.append(io.BytesIO(pdf_data), import_outline=False)
                        fichiers_sans_signets.append(pdf_file.name)
                
                # Création du PDF fusionné
                output = io.BytesIO()
                writer.write(output)
                writer.close()
                output.seek(0)
                
                # Téléchargement du fichier
                st.success("Fusion réussie! Cliquez ci-dessous pour télécharger le fichier fusionné.")

                if fichiers_sans_signets:
                    st.warning(
                        "Certains signets n'ont pas pu être importés : "
                        + ", ".join(fichiers_sans_signets)
                    )

                st.download_button(
                    "Télécharger le PDF fusionné",
                    data=output.getvalue(),
                    file_name="document_fusionné.pdf",
                    mime="application/pdf",
                )
                
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la fusion: {str(e)}")
        else:
            st.warning("Veuillez charger au moins deux fichiers PDF pour effectuer une fusion.")
else:
    st.info("Veuillez charger au moins deux fichiers PDF pour commencer.")

# Ajouter des informations
st.sidebar.title("Instructions")
st.sidebar.write("""
1. Cliquez sur 'Browse files' pour sélectionner plusieurs fichiers PDF
2. Les fichiers seront fusionnés dans l'ordre où ils apparaissent 
3. Cliquez sur 'Fusionner les PDF'
4. Téléchargez le fichier résultant
""")