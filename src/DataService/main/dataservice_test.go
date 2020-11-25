package main

import (
	"io/ioutil"
	"net/http"
	"os"
	"testing"
)

func TestRetrievePapers(t *testing.T) {
	InitServer()
	resp, _ := http.Get("http://127.0.0.1:8080/papers")
	if resp.StatusCode == http.StatusOK {
		bodyBytes, _ := ioutil.ReadAll(resp.Body)
		body := string(bodyBytes)
		//fmt.Println(body)
		f, _ := os.Create("./dbResponse.json")
		f.WriteString(body)
	}
}
