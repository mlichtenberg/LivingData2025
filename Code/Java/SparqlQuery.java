import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SparqlQuery {

    private static final String ENDPOINT_URL = "https://query.wikidata.org/sparql";

    private static final String QUERY = """
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
            """;

    public static void main(String[] args) {
        try {
            String tsvResults = getResultsTSV(ENDPOINT_URL, QUERY);
            String cleanedResults = cleanTSV(tsvResults);
            System.out.println(cleanedResults);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * Sends a SPARQL request to the Wikidata endpoint and returns TSV results.
     */
    public static String getResultsTSV(String endpointUrl, String query) throws IOException, InterruptedException {
        HttpClient client = HttpClient.newHttpClient();

        String encodedQuery = URLEncoder.encode(query, StandardCharsets.UTF_8);
        String fullUrl = endpointUrl + "?query=" + encodedQuery;

        String userAgent = String.format(
            "WDQS-example Java/%s",
            System.getProperty("java.version")
        );
        // TODO: Replace with your real user agent, e.g.
        // userAgent = "BHL-Wikidata-Integration/1.0 (your.email@example.org)";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(fullUrl))
                .header("User-Agent", userAgent)
                .header("Accept", "text/tab-separated-values")
                .GET()
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() >= 400) {
            throw new IOException("HTTP Error: " + response.statusCode() + " - " + response.body());
        }

        return response.body().trim();
    }

    /**
     * Removes quotes, datatype markers, and language tags from TSV response.
     */
    public static String cleanTSV(String tsvText) {
        StringBuilder cleaned = new StringBuilder();
        Pattern pattern = Pattern.compile("^\"(.*)\"(@[a-z\\-]+|\\^\\^.+)?$");

        for (String line : tsvText.split("\\R")) { // \R matches any line break
            if (line.startsWith("#")) continue; // skip comment lines

            String[] fields = line.split("\t");
            for (int i = 0; i < fields.length; i++) {
                Matcher matcher = pattern.matcher(fields[i]);
                if (matcher.matches()) {
                    fields[i] = matcher.group(1); // extract the quoted part
                }
            }
            cleaned.append(String.join("\t", fields)).append("\n");
        }
        return cleaned.toString().trim();
    }
}
