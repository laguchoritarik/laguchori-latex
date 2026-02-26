from src.laguchori_latex import LatexParser, clean_file

clean_file("input.tex", "output.tex", add_labels=True)

parser = LatexParser()
data = parser.parse_file("output.tex")
print(len(data["document"]["sections"]))