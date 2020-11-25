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
	columns, _ := rows.Columns()
	columnCount := len(columns)
	columnValues := make([]interface{}, columnCount)
	columnValuePointers := make([]interface{}, columnCount)
	for i := range columnValues {
		columnValuePointers[i] = &columnValues[i]
	}

	data := make(map[string][]interface{})

	for rows.Next() {
		rows.Scan(columnValuePointers...)
		for i, v := range columnValues {
			t := reflect.TypeOf(v).Kind()
			switch t {
			case reflect.String:
				data[columns[i]] = append(data[columns[i]], fmt.Sprintf("%v", v))
			case reflect.Int64:
				data[columns[i]] = append(data[columns[i]], v.(int64))
			default:
				fmt.Printf("Can't deal with type %T", v)
			}
		}
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
