package store

import "example.com/nspo/api/internal/model"

// Backend is the review/findings persistence abstraction (JSON file or PostgreSQL).
type Backend interface {
	Findings() ([]model.Finding, error)
	Reviews() ([]model.Review, error)
	AddReview(review model.Review) error
}
