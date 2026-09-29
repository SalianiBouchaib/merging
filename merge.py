import streamlit as st
import PyPDF2
import io


def merge_uploaded_pdfs(uploaded_files):
    writer = PyPDF2.PdfWriter()
    outline_warnings = []

    try:
        for pdf_file in uploaded_files:
            pdf_file.seek(0)
            try:
                writer.append(pdf_file, import_outline=True)
            except Exception as outline_error:
                pdf_file.seek(0)
                writer.append(pdf_file, import_outline=False)
                outline_warnings.append(
                    f"Signets ignorés pour « {pdf_file.name} » (fusion conservée) : {outline_error}"
                )

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return output, outline_warnings
    finally:
        writer.close()

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
            try:
                output, outline_warnings = merge_uploaded_pdfs(uploaded_files)
                
                # Téléchargement du fichier
                st.success("Fusion réussie! Cliquez ci-dessous pour télécharger le fichier fusionné.")
                for warning in outline_warnings:
                    st.warning(warning)
                
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