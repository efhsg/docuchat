from pypdf import PdfReader


def extract_text(uploaded_file):
    file_extension = uploaded_file.name.split(".")[-1].lower()
    extractors = {
        "pdf": extract_text_from_pdf,
        "txt": extract_text_from_txt,
    }
    if file_extension in extractors:
        return extractors[file_extension](uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: '{file_extension}'")


def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_txt(uploaded_file):
    return uploaded_file.getvalue().decode("utf-8")
