package store

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"sync"

	"example.com/nspo/api/internal/model"
)

type Store struct {
	mu          sync.RWMutex
	dataDir     string
	reviewStore string
}

func New(dataDir, reviewStore string) *Store {
	return &Store{dataDir: dataDir, reviewStore: reviewStore}
}

func (s *Store) Findings() ([]model.Finding, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	data, err := os.ReadFile(filepath.Join(s.dataDir, "findings.json"))
	if err != nil {
		return nil, err
	}
	var findings []model.Finding
	if err := json.Unmarshal(data, &findings); err != nil {
		return nil, err
	}
	return findings, nil
}

func (s *Store) AddReview(review model.Review) error {
	allowed := map[string]bool{"acknowledged": true, "needs-more-data": true, "rejected": true, "corrected": true}
	if !allowed[review.Decision] {
		return errors.New("unsupported review decision")
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	if err := os.MkdirAll(filepath.Dir(s.reviewStore), 0o755); err != nil {
		return err
	}
	var reviews []model.Review
	if data, err := os.ReadFile(s.reviewStore); err == nil {
		_ = json.Unmarshal(data, &reviews)
	}
	reviews = append(reviews, review)
	data, err := json.MarshalIndent(reviews, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(s.reviewStore, append(data, '\n'), 0o644)
}
