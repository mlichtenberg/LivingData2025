#gem install sparql
#http://www.rubydoc.info/github/ruby-rdf/sparql/frames

require 'sparql/client'

endpoint = "https://query.wikidata.org/sparql"
sparql = <<'SPARQL'.chop
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

SPARQL

client = SPARQL::Client.new(endpoint,
                            :method => :get,
                            # TODO adjust user agent; see https://w.wiki/CX6
                            headers: {'User-Agent' => 'WDQS-example Ruby'})
rows = client.query(sparql)

puts "Number of rows: #{rows.size}"
for row in rows
  for key,val in row do
    # print "#{key.to_s.ljust(10)}: #{val}\t"
    print "#{key}: #{val}\t"
  end
  print "\n"
end
