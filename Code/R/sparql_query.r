# Required packages
# install.packages("httr")
# install.packages("readr")
# install.packages("stringr")
# install.packages("ggplot2")
library(httr)
library(readr)
library(stringr)
library(ggplot2)

# SPARQL endpoint and query
endpoint <- "https://query.wikidata.org/sparql"

query <- '
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
'

# Define a user agent (Wikidata requires a descriptive one)
# TODO: Replace with your real one
useragent <- "Wikidata-Query/1.0 (your.email@example.org)"

# Perform the SPARQL query using GET request
response <- GET(
  url = endpoint,
  query = list(query = query),
  add_headers(
    "User-Agent" = useragent,
    "Accept" = "text/tab-separated-values"
  )
)

# Check for HTTP errors
stop_for_status(response)

# Read the returned TSV into a dataframe
tsv_text <- content(response, "text", encoding = "UTF-8")

# Remove comment lines (that start with "#")
tsv_lines <- strsplit(tsv_text, "\n")[[1]]
tsv_lines <- tsv_lines[!grepl("^#", tsv_lines)]  # skip header comment lines

# Parse the TSV text
df <- read_tsv(
  paste(tsv_lines, collapse = "\n"),
  show_col_types = FALSE,
  na = ""
)

# Remove surrounding quotes, datatype markers, and language tags
# Example: "Q123"^^xsd:string -> Q123, "Title"@en -> Title
clean_field <- function(x) {
  ifelse(
    is.na(x),
    NA_character_,
    str_replace(x, '^"(.*)"(@[a-zA-Z\\-]+|\\^\\^.+)?$', '\\1')
  )
}

df_clean <- df
df_clean[] <- lapply(df_clean, clean_field)

# Print cleaned data
print(df_clean)

# Example visualization (optional)
# ggplot(df_clean, aes(x = TitleID)) + geom_bar()
