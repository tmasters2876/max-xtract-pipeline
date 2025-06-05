import pdfplumber

with pdfplumber.open("docs/First_Amendment_to_the_Declaration_of_Covenants,_Conditions_&_Restrictions_-_10-05-2004.pdf") as pdf:
    print(f"Pages: {len(pdf.pages)}")
    print(pdf.pages[0].extract_text())
