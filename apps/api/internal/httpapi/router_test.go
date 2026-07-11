package httpapi

import (
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"example.com/nspo/api/internal/store"
)

func TestHealth(t *testing.T) {
	dir := t.TempDir()
	if err := os.WriteFile(filepath.Join(dir, "findings.json"), []byte("[]\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	api := API{Store: store.New(dir, filepath.Join(dir, "reviews.json"))}
	req := httptest.NewRequest(http.MethodGet, "/healthz", nil)
	res := httptest.NewRecorder()
	api.Handler().ServeHTTP(res, req)
	if res.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", res.Code)
	}
}

func TestReviewsGetAndPost(t *testing.T) {
	dir := t.TempDir()
	if err := os.WriteFile(filepath.Join(dir, "findings.json"), []byte("[]\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	reviewPath := filepath.Join(dir, "reviews.json")
	api := API{Store: store.New(dir, reviewPath)}
	handler := api.Handler()

	getReq := httptest.NewRequest(http.MethodGet, "/api/reviews", nil)
	getRes := httptest.NewRecorder()
	handler.ServeHTTP(getRes, getReq)
	if getRes.Code != http.StatusOK {
		t.Fatalf("expected empty GET 200, got %d", getRes.Code)
	}
	if body := getRes.Body.String(); body != "[]\n" {
		t.Fatalf("expected empty list, got %q", body)
	}

	postReq := httptest.NewRequest(http.MethodPost, "/api/reviews", strings.NewReader(`{"finding_id":"finding-1","decision":"needs-more-data","reviewer":"analyst@example.invalid","comment":"check upstream"}`))
	postReq.Header.Set("Content-Type", "application/json")
	postRes := httptest.NewRecorder()
	handler.ServeHTTP(postRes, postReq)
	if postRes.Code != http.StatusCreated {
		t.Fatalf("expected POST 201, got %d body=%s", postRes.Code, postRes.Body.String())
	}

	listReq := httptest.NewRequest(http.MethodGet, "/api/reviews", nil)
	listRes := httptest.NewRecorder()
	handler.ServeHTTP(listRes, listReq)
	if listRes.Code != http.StatusOK {
		t.Fatalf("expected GET 200, got %d", listRes.Code)
	}
	if !strings.Contains(listRes.Body.String(), `"finding_id":"finding-1"`) {
		t.Fatalf("expected stored review in GET body, got %s", listRes.Body.String())
	}
}
