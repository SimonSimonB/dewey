package main

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"strings"
	"testing"
)

func TestRetrieveSimilarPapers(t *testing.T) {
	InitServer()
	queryJSON := strings.NewReader("{ \"query\":\"democracy voting\" }")
	resp, err := http.Post("http://127.0.0.1:8080/similarpapers", "application/json", queryJSON)
	if err != nil {
		t.Log("Could not retrieve similar papers from search service")
		t.Fail()
	}
	if resp.StatusCode == http.StatusOK {
		jsonResponse, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			t.Fail()
		}

		var parsedJSONResponse []map[string]interface{}
		json.Unmarshal([]byte(jsonResponse), &parsedJSONResponse)
		if len(parsedJSONResponse) == 0 {
			t.Log("The received JSON for the search results was empty.")
			t.Fail()
		}
	}
}
