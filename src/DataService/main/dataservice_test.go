package main

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"strings"
	"testing"
)

func TestRetrievePaper(t *testing.T) {
	InitServer()
	resp, err := http.Get("http://127.0.0.1:8082/papers/10.1086/700029")
	if err != nil {
		t.Log("Could not retrieve paper from data service")
		t.Fail()
	}
	if resp.StatusCode == http.StatusOK {
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			t.Fail()
		}

		var paperData map[string]interface{}
		json.Unmarshal(body, &paperData)

		if paperData["title"] != "Grit*" {
			t.Fail()
		}
	}
}
func TestRetrievePapers(t *testing.T) {
	InitServer()
	resp, err := http.Get("http://127.0.0.1:8082/papers")
	if err != nil {
		t.Log("Could not retrieve papers from data service")
		t.Fail()
	}
	if resp.StatusCode == http.StatusOK {
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			t.Fail()
		}

		if !strings.Contains(string(body), "Ethics") {
			t.Fail()
		}
	}
}
