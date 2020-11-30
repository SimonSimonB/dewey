package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"sort"
)

// InitServer initializes the HTTP server for the search API.
func InitServer() error {
	configFile, err := os.Open("../../config.json")
	if err != nil {
		fmt.Println(err)
	}
	configFileContents, _ := ioutil.ReadAll(configFile)

	var config map[string]interface{}
	json.Unmarshal([]byte(configFileContents), &config)

	searchServicePort := config["search_service"].(map[string]interface{})["port"].(float64)
	similarityServicePort := config["similarity_service"].(map[string]interface{})["port"].(float64)
	dataServicePort := config["data_service"].(map[string]interface{})["port"].(float64)

	router := http.NewServeMux()
	router.HandleFunc("/similarpapers", func(responseWriter http.ResponseWriter, request *http.Request) {
		if request.Method != http.MethodPost {
			responseWriter.WriteHeader(http.StatusBadRequest)
			return
		}

		// Ask similarity service to compute similarities for the given query.
		similarityServiceQuery := request.Body
		similarityServiceResponse, err := http.Post(
			fmt.Sprintf("http://127.0.0.1:%g/similarities", similarityServicePort),
			"application/json",
			similarityServiceQuery)

		if err != nil {
			log.Fatal("Request to similarity service failed.")
			responseWriter.WriteHeader(http.StatusInternalServerError)
			return
		} else if similarityServiceResponse.StatusCode != 200 {
			log.Fatal("Similarity service returned with status code ",
				similarityServiceResponse.StatusCode)
			responseWriter.WriteHeader(http.StatusInternalServerError)
			return
		}

		similarityServiceResponseContent, _ := ioutil.ReadAll(similarityServiceResponse.Body)
		var similarities map[string]interface{}
		json.Unmarshal([]byte(similarityServiceResponseContent), &similarities)

		// Sort papers by similarity.
		type doiSimilarity struct {
			doi        string
			similarity float64
		}

		var doiSimilarities []doiSimilarity
		for doi, similarity := range similarities {
			doiSimilarities = append(doiSimilarities, doiSimilarity{doi, similarity.(float64)})
		}
		sort.Slice(doiSimilarities, func(i, j int) bool {
			return doiSimilarities[i].similarity > doiSimilarities[j].similarity
		})
		log.Print("Returning results, sorted by similarity: ", doiSimilarities)

		const numPapersToReturn = 10
		var searchResultsData []map[string]interface{}
		for _, paperDoiSimilarity := range doiSimilarities {
			doi := paperDoiSimilarity.doi
			if len(searchResultsData) >= numPapersToReturn {
				break
			}

			dataServiceResponse, err := http.Get(
				fmt.Sprintf("http://127.0.0.1:%g/papers/%v", dataServicePort, doi))
			if err != nil {
				break
			}
			dataServiceResponseContent, _ := ioutil.ReadAll(dataServiceResponse.Body)

			var paperData map[string]interface{}
			json.Unmarshal([]byte(dataServiceResponseContent), &paperData)
			searchResultsData = append(searchResultsData, map[string]interface{}{
				"title":        paperData["title"],
				"author":       paperData["author"],
				"year":         paperData["year"],
				"journal":      paperData["journal"],
				"abstract":     paperData["abstract"],
				"auto_summary": paperData["auto_summary"],
				"doi":          paperData["doi"],
			})
		}

		searchResultsJSON, err := json.Marshal(searchResultsData)
		if err != nil {
			log.Fatal("Failed to convert search results to JSON")
			responseWriter.WriteHeader(http.StatusInternalServerError)
			return
		}

		responseWriter.Header().Set("Content-Type", "application/json")
		responseWriter.Write(searchResultsJSON)
	})
	log.Println("Starting server on port ", searchServicePort)
	configFile.Close()

	go http.ListenAndServe(fmt.Sprintf(":%g", searchServicePort), router)

	return nil
}

func main() {
	InitServer()
	fmt.Println("Press any key to terminate the search service...")
	fmt.Scanln()
}
