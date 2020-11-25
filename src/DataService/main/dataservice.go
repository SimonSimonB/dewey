package main

import (
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"reflect"
	"time"

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
	go http.ListenAndServe(":8080", router)

	return nil
}

func main() {
	InitServer()
	time.Sleep(1000000000000)
}
