import streamlit as st
import PyPDF2
import io


def _fit_from_destination(destination):
    destination_type = getattr(destination, "typ", None)
    fit_factory = PyPDF2.generic.Fit

    if destination_type == "/XYZ":
        return fit_factory.xyz(
            left=getattr(destination, "left", None),
            top=getattr(destination, "top", None),
            zoom=getattr(destination, "zoom", None),
        )
    if destination_type == "/FitH":
        return fit_factory.fit_horizontally(top=getattr(destination, "top", None))
    if destination_type == "/FitV":
        return fit_factory.fit_vertically(left=getattr(destination, "left", None))
    if destination_type == "/FitR":
        return fit_factory.fit_rectangle(
            left=getattr(destination, "left", None),
            bottom=getattr(destination, "bottom", None),
            right=getattr(destination, "right", None),
            top=getattr(destination, "top", None),
        )
    if destination_type == "/FitB":
        return fit_factory.fit_box()
    if destination_type == "/FitBH":
        return fit_factory.fit_box_horizontally(top=getattr(destination, "top", None))
    if destination_type == "/FitBV":
        return fit_factory.fit_box_vertically(left=getattr(destination, "left", None))
    return fit_factory.fit()


def _copy_outline_items(writer, reader, outline_items, page_offset, source_name, warnings, parent=None):
    last_item = None

    for item in outline_items:
        if isinstance(item, list):
            if last_item is not None:
                _copy_outline_items(
                    writer,
                    reader,
                    item,
                    page_offset,
                    source_name,
                    warnings,
                    parent=last_item,
                )
            continue

        try:
            page_number = reader.get_destination_page_number(item)
            color = getattr(item, "color", None)
            font_format = getattr(item, "font_format", 0) or 0
            last_item = writer.add_outline_item(
                title=getattr(item, "title", "Signet"),
                page_number=page_offset + page_number,
                parent=parent,
                color=tuple(color) if color else None,
                bold=bool(font_format & 2),
                italic=bool(font_format & 1),
                fit=_fit_from_destination(item),
            )
        except Exception as outline_error:
            last_item = None
            warnings.append(
                f"Signet ignoré dans « {source_name} » (fusion conservée) : {outline_error}"
            )


def merge_uploaded_pdfs(uploaded_files):
    writer = PyPDF2.PdfWriter()
    outline_warnings = []

    try:
        for pdf_file in uploaded_files:
            pdf_file.seek(0)
            try:
                reader = PyPDF2.PdfReader(pdf_file)
                page_offset = len(writer.pages)

                for page in reader.pages:
                    writer.add_page(page)

                try:
                    outline_items = reader.outline
                    _copy_outline_items(
                        writer,
                        reader,
                        outline_items,
                        page_offset,
                        pdf_file.name,
                        outline_warnings,
                    )
                except Exception as outline_error:
                    outline_warnings.append(
                        f"Signets ignorés pour « {pdf_file.name} » (fusion conservée) : {outline_error}"
                    )
            except Exception as merge_error:
                outline_warnings.append(
                    f"Impossible d'importer les signets de « {pdf_file.name} » (fusion conservée) : {merge_error}"
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