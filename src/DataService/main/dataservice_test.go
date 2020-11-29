package main

import (
	"io/ioutil"
	"net/http"
	"testing"
)

func TestRetrievePapers(t *testing.T) {
	InitServer()
	resp, err := http.Get("http://127.0.0.1:8082/papers")
	if err != nil {
		t.Log("Could not retrieve papers from data service")
		t.Fail()
	}
	if resp.StatusCode == http.StatusOK {
		_, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			t.Fail()
		}

		//body := string(bodyBytes)
		//fmt.Println(body)
		//f, _ := os.Create("./dbResponse.json")
		//f.WriteString(body)
	}
}
