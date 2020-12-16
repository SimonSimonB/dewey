![A GIF of the Dewey search engine](web_demo.gif)

# Summary

Dewey is an (unfinished) search engine for academic papers. 
* It supports searching not only based on keywords, but also based on the contents of entire documents, such as a paper draft that the user works on.
* In the search results, Dewey displays quotes from the retrieved papers. The quotes are intended to allow users to get a sense of what a paper is about. Dewey currently uses simple heuristics to select these quotes. 

I work on Dewey to learn more about Go, REST APIs, and microservice architecture. 


# Usage

Run `docker-compose up` from the root directory. Open the search engine at `http://localhost:9000`.