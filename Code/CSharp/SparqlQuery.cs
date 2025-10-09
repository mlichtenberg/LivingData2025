try
{
    string cleanedTsv = SubmitSparqlQueryAndSaveTsvAsync().GetAwaiter().GetResult();
    Console.Write(cleanedTsv);
}
catch (Exception ex)
{
    Console.WriteLine($"Exception harvesting identifiers: {ex.Message}");
}

static async Task<string> SubmitSparqlQueryAndSaveTsvAsync()
{
    string cleanedTsv;
    string endpointUrl = "https://query.wikidata.org/sparql";
    string sparqlQuery = "SELECT DISTINCT ?TitleID ?Wikidata ?OCLC ?DOI WHERE { " + 
                          "{ " + 
                            "{ " + 
                              "SELECT DISTINCT ?item WHERE { " + 
                                "?item p:P4327 ?statement0. " + 
                                "?statement0 ps:P4327 _:anyValueP4327. " + 
                              "} " + 
                            "} " + 
                            "BIND(REPLACE(STR(?item), \"http://www.wikidata.org/entity/\", \"\") AS ?Wikidata ) " + 
                            "OPTIONAL { ?item wdt:P4327 ?TitleID. } " + 
                            "OPTIONAL { ?item wdt:P243 ?OCLC. } " + 
                            "OPTIONAL { ?item wdt:P356 ?DOI. } " + 
                          "} " + 
                          "UNION " +  
                          "{ " + 
                            "SERVICE wdsubgraph:scholarly_articles { " + 
                              "{ " + 
                                "SELECT DISTINCT ?item WHERE { " + 
                                  "?item p:P4327 ?statement0. " + 
                                  "?statement0 ps:P4327 _:anyValueP43272. " + 
                                "} " + 
                              "} " + 
                              "BIND(REPLACE(STR(?item), \"http://www.wikidata.org/entity/\", \"\") AS ?Wikidata ) " + 
                              "OPTIONAL { ?item wdt:P4327 ?TitleID. } " + 
                              "OPTIONAL { ?item wdt:P243 ?OCLC. } " + 
                              "OPTIONAL { ?item wdt:P356 ?DOI. } " + 
                            "} " + 
                          "} " + 
                        "}";


    using (HttpClient client = new HttpClient())
    {
        // Set user-agent (required by Wikidata Query Service)
        client.DefaultRequestHeaders.Add("User-Agent", "WikidataHarvest/1.0 (your@emailaddress.org)");

        // Prepare the request content
        var content = new FormUrlEncodedContent(new[]
        {
            new KeyValuePair<string, string>("query", sparqlQuery)
        });

        // Set Accept header to Tab-Separated Value
        client.DefaultRequestHeaders.Accept.Clear();
        client.DefaultRequestHeaders.Accept.Add(new System.Net.Http.Headers.MediaTypeWithQualityHeaderValue("text/tab-separated-values"));

        // Send POST request
        HttpResponseMessage response = await client.PostAsync(endpointUrl, content);

        if (response.IsSuccessStatusCode)
        {
            string tsvContent = await response.Content.ReadAsStringAsync();

            // Remove surrounding quotes from each TSV cell (just in case)
            cleanedTsv = string.Join("\n",
                tsvContent
                    .Split('\n')
                    .Select(line =>
                        string.Join("\t",
                            line.Split('\t')
                                .Select(cell => cell.Trim('"'))
                        )
                    )
            );
        }
        else
        {
            string errorContent = await response.Content.ReadAsStringAsync();
            throw new Exception($"Error: {response.StatusCode} - {response.ReasonPhrase}\n{errorContent}");
        }
    }

    return cleanedTsv;
}
