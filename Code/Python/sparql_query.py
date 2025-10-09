import sys
import re
import requests

endpoint_url = "https://query.wikidata.org/sparql"

query = """
SELECT DISTINCT ?TitleID ?Wikidata ?OCLC ?DOI WHERE {
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
  { 
    SERVICE wdsubgraph:scholarly_articles {
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

# Send a SPARQL request to the Wikidata query endpoint and return tab-separated values
def get_results_tsv(endpoint_url, query):
    user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
    # TODO adjust user agent; see https://w.wiki/CX6
	# user_agent = "Wikidata-Query/1.0 (your.email@example.org)"
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/tab-separated-values"
    }
    params = {
        "query": query
    }

    response = requests.get(endpoint_url, headers=headers, params=params)
    response.raise_for_status()  # Raise exception for HTTP errors
    return response.text.strip()

# Remove surrounding quotes and datatype/language tags from the Wikidata response
def clean_tsv(tsv_text):
    cleaned_lines = []
    for line in tsv_text.splitlines():
        # Skip comment lines (like "#titleID ...")
        if line.startswith("#"):
            continue

        # Split on tabs
        fields = line.split("\t")

        # Remove quotes, datatype markers, and language tags
        cleaned = []
        for f in fields:
            f = re.sub(r'^"(.*)"(@[a-z\-]+|\^\^.+)?$', r'\1', f)  # remove quotes + tags
            cleaned.append(f)
        cleaned_lines.append("\t".join(cleaned))
    return "\n".join(cleaned_lines)

# Send a SPARQL request to the Wikidata query endpoint and return JSON
def get_results_json(endpoint_url, query):
    user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
    # TODO adjust user agent; see https://w.wiki/CX6
	# user_agent = "BHL-Wikidata-Integration/1.0 (your.email@example.org)"
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/sparql-results+json"
    }
    params = {
        "query": query
    }

    response = requests.get(endpoint_url, headers=headers, params=params)
    response.raise_for_status()  # Raise exception for HTTP errors
    return response.json()

# Remove the comments from the following lines to get JSON output
#json_results = get_results_json(endpoint_url, query)
#for result in json_results["results"]["bindings"]:
#    print(result)

# Get tab-separated-value output
tsv_results = get_results_tsv(endpoint_url, query)
clean_tsv_results = clean_tsv(tsv_results) 
print(clean_tsv_results)
