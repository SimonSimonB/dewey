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
	"reflect"

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

	err := json.NewEncoder(w).Encode(data)
	if err != nil {
		log.Fatal("Failed to encode papers SQL table as JSON")
	}
}

// InitServer initializes the HTTP server for the data API.
func InitServer() error {
	db, err := sql.Open("sqlite3", "../papers.db")
	if err != nil {
		return errors.New("could not open SQLite database file")
	}

	router := http.NewServeMux()
	router.HandleFunc("/papers", func(responseWriter http.ResponseWriter, request *http.Request) {
		if request.Method == http.MethodGet {
			rows, err := db.Query("SELECT * FROM papers")
			if err != nil {
				log.Fatal("Database query failed.")
			}

			queryResultToJSON(rows, responseWriter)
			responseWriter.Header().Set("Content-Type", "application/json")
		} else {
			responseWriter.WriteHeader(http.StatusBadRequest)
		}
	})

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
	fmt.Println("Press any key to terminate the database service...")
	fmt.Scanln()
}
