# sparqlwrapper is a python package that provides a simple wrapper around the SPARQL service
# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
import json
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT DISTINCT ?TitleID ?Wikidata ?OCLC ?DOI WHERE {
  {
  {
    SELECT DISTINCT ?item WHERE {
      ?item p:P4327 ?statement0.
      ?statement0 ps:P4327 _:anyValueP4327.
    }
  }
  BIND(REPLACE(STR(?item), "http://www.wikidata.org/entity/", "") AS ?Wikidata )
  OPTIONAL { ?item wdt:P4327 ?TitleID. }
  OPTIONAL { ?item wdt:P243 ?OCLC. }
  OPTIONAL { ?item wdt:P356 ?DOI. }  
  }
    UNION  
  { SERVICE wdsubgraph:scholarly_articles {  # Federated query
  {
    SELECT DISTINCT ?item WHERE {
      ?item p:P4327 ?statement0.
      ?statement0 ps:P4327 _:anyValueP43272.
    }
  }
  BIND(REPLACE(STR(?item), "http://www.wikidata.org/entity/", "") AS ?Wikidata )
  OPTIONAL { ?item wdt:P4327 ?TitleID. }
  OPTIONAL { ?item wdt:P243 ?OCLC. }
  OPTIONAL { ?item wdt:P356 ?DOI. }
 }
 }
}
"""

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def json_to_tsv(input_text):
    """
    Convert newline-delimited JSON objects into a TSV string.
    Each object must have a structure like:
    {'Wikidata': {'type': 'literal', 'value': 'Q123'}, ...}
    """
    records = []

    # Parse each line as JSON
    for inputline in input_text:
        line = str(inputline)

        line = line.strip()
        if not line:
            continue
        # Allow single quotes by replacing with double quotes
        # (valid JSON uses double quotes)
        if line.startswith("{'"):
            line = line.replace("'", '"')
        record = json.loads(line)
        # Flatten to key -> value
        flat = {k: v.get('value', '') for k, v in record.items()}
        records.append(flat)

    # Determine all possible columns
    all_keys = ['Wikidata', 'TitleID', 'OCLC', 'DOI']
    header = '\t'.join(all_keys)

    # Convert to TSV rows
    rows = [header]
    for rec in records:
        row = '\t'.join(rec.get(k, '') for k in all_keys)
        rows.append(row)

    return '\n'.join(rows)

json_results = get_results(endpoint_url, query)
# Remove the comments from the following lines to get JSON output
#for result in json_results["results"]["bindings"]:
#    print(result)
print(json_to_tsv(json_results["results"]["bindings"]))
