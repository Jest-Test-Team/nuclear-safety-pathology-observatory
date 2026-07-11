package main

import (
	"log"
	"net/http"
	"os"

	"example.com/nspo/api/internal/httpapi"
	"example.com/nspo/api/internal/store"
)

func env(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}

func main() {
	addr := env("NSPO_API_ADDR", ":8080")
	var backend store.Backend
	if databaseURL := os.Getenv("NSPO_DATABASE_URL"); databaseURL != "" {
		pg, err := store.NewPostgresStore(databaseURL)
		if err != nil {
			log.Fatalf("postgres store: %v", err)
		}
		backend = pg
		log.Printf("NSPO review API using PostgreSQL backend")
	} else {
		dataDir := env("NSPO_DATA_DIR", "../../data/derived")
		reviewStore := env("NSPO_REVIEW_STORE", "../../data/runtime/reviews.json")
		backend = store.NewFileStore(dataDir, reviewStore)
		log.Printf("NSPO review API using file backend under %s", dataDir)
	}
	api := httpapi.API{Store: backend}
	log.Printf("NSPO review API listening on %s", addr)
	log.Fatal(http.ListenAndServe(addr, api.Handler()))
}
