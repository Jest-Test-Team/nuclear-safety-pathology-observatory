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
	dataDir := env("NSPO_DATA_DIR", "../../data/derived")
	reviewStore := env("NSPO_REVIEW_STORE", "../../data/runtime/reviews.json")
	api := httpapi.API{Store: store.New(dataDir, reviewStore)}
	log.Printf("NSPO review API listening on %s", addr)
	log.Fatal(http.ListenAndServe(addr, api.Handler()))
}
