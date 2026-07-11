package httpapi

import (
	"encoding/json"
	"net/http"
	"strings"
	"time"

	"example.com/nspo/api/internal/model"
	"example.com/nspo/api/internal/store"
)

type API struct{ Store *store.Store }

func (a API) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, map[string]any{"status": "ok", "mode": "research-public-data-only"})
	})
	mux.HandleFunc("/api/findings", a.findings)
	mux.HandleFunc("/api/reviews", a.reviews)
	return withCORS(mux)
}

func (a API) findings(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	findings, err := a.Store.Findings()
	if err != nil {
		http.Error(w, err.Error(), http.StatusServiceUnavailable)
		return
	}
	writeJSON(w, http.StatusOK, findings)
}

func (a API) reviews(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		reviews, err := a.Store.Reviews()
		if err != nil {
			http.Error(w, err.Error(), http.StatusServiceUnavailable)
			return
		}
		writeJSON(w, http.StatusOK, reviews)
	case http.MethodPost:
		var review model.Review
		if err := json.NewDecoder(r.Body).Decode(&review); err != nil {
			http.Error(w, "invalid JSON", http.StatusBadRequest)
			return
		}
		if strings.TrimSpace(review.FindingID) == "" || strings.TrimSpace(review.Reviewer) == "" {
			http.Error(w, "finding_id and reviewer are required", http.StatusBadRequest)
			return
		}
		review.CreatedAt = time.Now().UTC().Format(time.RFC3339Nano)
		if err := a.Store.AddReview(review); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		writeJSON(w, http.StatusCreated, review)
	default:
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
	}
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(value)
}

func withCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)
	})
}
