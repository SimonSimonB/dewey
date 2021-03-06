package main

import (
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"reflect"

	"github.com/gorilla/mux"
	_ "github.com/mattn/go-sqlite3"
)

type attribute struct {
	name    string
	sqlType string
}

var paperAttributes = []attribute{
	{"title", "text"},
	{"author", "text"},
	{"doi", "text"},
	{"year", "int"},
	{"journal", "text"},
	{"abstract", "text"},
	{"body", "text"},
	{"auto_summary", "text"},
}

func queryResultToJSON(rows *sql.Rows, w io.Writer) {
	columnNames, _ := rows.Columns()
	columnCount := len(columnNames)
	columnValues := make([]interface{}, columnCount)
	columnValuePointers := make([]interface{}, columnCount)
	for i := range columnValues {
		columnValuePointers[i] = &columnValues[i]
	}

	var data []map[string]interface{}

	for rows.Next() {
		rows.Scan(columnValuePointers...)
		row := make(map[string]interface{})
		for i, v := range columnValues {
			t := reflect.TypeOf(v).Kind()
			switch t {
			case reflect.String:
				row[columnNames[i]] = fmt.Sprintf("%v", v)
			case reflect.Int64:
				row[columnNames[i]] = v.(int64)
			default:
				fmt.Printf("Can't deal with type %T", v)
			}
		}

		data = append(data, row)
	}

	// If it was a single row, encode a map[string]interface{} rather than a []map[string]interface{}.
	var err error
	if len(data) == 1 {
		err = json.NewEncoder(w).Encode(data[0])
	} else {
		err = json.NewEncoder(w).Encode(data)
	}

	if err != nil {
		log.Fatal("Failed to encode papers SQL table as JSON")
	}
}

// InitServer initializes the HTTP server for the data API.
func InitServer() error {
	executablePath, err := os.Executable()
	if err != nil {
		return errors.New("could not retrieve path of executable, relative to which the database path is specified")
	}
	dbPath := filepath.Join(filepath.Dir(executablePath), "papers.db")
	fmt.Println(dbPath)

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return errors.New("could not open SQLite database file")
	}

	router := mux.NewRouter()

	router.HandleFunc("/papers", func(responseWriter http.ResponseWriter, request *http.Request) {
		if request.Method == http.MethodGet {
			rows, err := db.Query("SELECT * FROM papers")
			if err != nil {
				log.Fatal("Database query failed.")
			}

			queryResultToJSON(rows, responseWriter)
			log.Print("Returning all papers in response to request.")
			responseWriter.Header().Set("Content-Type", "application/json")
		} else {
			responseWriter.WriteHeader(http.StatusBadRequest)
		}
	})

	router.HandleFunc("/papers/{doiPrefix}/{doiSuffix}", func(responseWriter http.ResponseWriter, request *http.Request) {
		doiPrefix := mux.Vars(request)["doiPrefix"]
		doiSuffix := mux.Vars(request)["doiSuffix"]
		doi := doiPrefix + "/" + doiSuffix
		if request.Method == http.MethodGet {
			rows, err := db.Query("SELECT * FROM papers WHERE doi=?", doi)
			if err != nil {
				log.Fatalf("Database query for paper with DOI %v failed.", doi)
			}

			queryResultToJSON(rows, responseWriter)
			responseWriter.Header().Set("Content-Type", "application/json")
		} else {
			responseWriter.WriteHeader(http.StatusBadRequest)
		}
	})

	// Read port on which the data service should run from the config file.
	configFile, err := os.Open("../../config.json")
	if err != nil {
		fmt.Println(err)
	}
	configFileContents, _ := ioutil.ReadAll(configFile)
	var config map[string]interface{}
	json.Unmarshal([]byte(configFileContents), &config)
	dataServicePort := config["data_service"].(map[string]interface{})["port"].(float64)

	log.Println("Starting server on port ", dataServicePort)
	configFile.Close()

	go http.ListenAndServe(fmt.Sprintf(":%g", dataServicePort), router)

	return nil
}

func main() {
	InitServer()
	select {}
}
