from extract_pages import extract_pages_from_pdf
from batch_gpt_parse import parse_pages_with_gpt
from upload_to_supabase import upload_clauses
from document_links import get_document_link

doc_path = "docs/First_Amendment_to_the_Declaration_of_Covenants,_Conditions_&_Restrictions_-_10-05-2004.pdf"
doc_name = "First_Amendment_to_the_Declaration_of_Covenants,_Conditions_&_Restrictions_-_10-05-2004"
link = get_document_link(doc_name)

pages = extract_pages_from_pdf(doc_path, doc_name)

clauses = []
for page in pages:
    parsed = parse_pages_with_gpt(page["text"], page["page"], doc_name)
    for clause in parsed:
        clause["link"] = link
        clauses.append(clause)

upload_clauses(clauses)
