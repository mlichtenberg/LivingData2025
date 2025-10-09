class SPARQLQueryDispatcher {
	constructor(endpoint) {
		this.endpoint = endpoint;
	}

	query(sparqlQuery) {
		const headers = {
			'Accept': 'text/tab-separated-values',
			//'Accept': 'application/sparql-results+json',
			'Content-Type': 'application/sparql-query',
			'User-Agent': 'Wikidata-Query/1.0 (your.email@example.org)' 
		};

		// Use POST and send the SPARQL query in the request body
		return fetch(this.endpoint, {
			method: 'POST',
			headers,
			body: sparqlQuery
		}).then(response => {
			if (!response.ok) {
				throw new Error(`SPARQL query failed: ${response.status} ${response.statusText}`);
			}
			return response.text(); // Return TSV text
			//return response.json(); // Return JSON
		});
	}
}

function stripQuotesFromTSV(tsv) {
	const lines = tsv.split('\n').filter(line => line.trim() !== '');
	if (lines.length === 0) return '';

	const header = lines[0];
	const rows = lines.slice(1).map(line => {
		return line
			.split('\t')
			.map(value => value.replace(/^"(.*)"$/, '$1')) // remove surrounding quotes
			.join('\t');
	});
	return [header, ...rows].join('\n');
}

const endpointUrl = 'https://query.wikidata.org/sparql';
const sparqlQuery = `SELECT DISTINCT ?TitleID ?Wikidata ?OCLC ?DOI WHERE {
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
  { SERVICE wdsubgraph:scholarly_articles {
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
`;

const queryDispatcher = new SPARQLQueryDispatcher(endpointUrl);
queryDispatcher.query(sparqlQuery).then(data => {
	const cleaned = stripQuotesFromTSV(data);
	console.log(cleaned);
}).catch(error => {
	console.error('Error executing SPARQL query:', error);
});
