package store

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"time"

	"example.com/nspo/api/internal/model"

	_ "github.com/jackc/pgx/v5/stdlib"
)

// PostgresStore persists findings/reviews using the optional SQL schema.
type PostgresStore struct {
	db *sql.DB
}

func NewPostgresStore(databaseURL string) (*PostgresStore, error) {
	db, err := sql.Open("pgx", databaseURL)
	if err != nil {
		return nil, err
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := db.PingContext(ctx); err != nil {
		_ = db.Close()
		return nil, err
	}
	return &PostgresStore{db: db}, nil
}

func (s *PostgresStore) Close() error {
	return s.db.Close()
}

func (s *PostgresStore) Findings() ([]model.Finding, error) {
	rows, err := s.db.Query(`
		SELECT finding_id, rule_id, status, created_at, scope, evidence, alternatives, limitations, uncertainty
		FROM finding
		ORDER BY created_at DESC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var findings []model.Finding
	for rows.Next() {
		var item model.Finding
		var scopeRaw, evidenceRaw, alternativesRaw, limitationsRaw []byte
		var createdAt time.Time
		if err := rows.Scan(
			&item.FindingID,
			&item.RuleID,
			&item.Status,
			&createdAt,
			&scopeRaw,
			&evidenceRaw,
			&alternativesRaw,
			&limitationsRaw,
			&item.Uncertainty,
		); err != nil {
			return nil, err
		}
		item.CreatedAt = createdAt.UTC().Format(time.RFC3339Nano)
		item.FindingType = "stored"
		if err := json.Unmarshal(scopeRaw, &item.Scope); err != nil {
			return nil, err
		}
		if err := json.Unmarshal(evidenceRaw, &item.SupportingEvidence); err != nil {
			return nil, err
		}
		if err := json.Unmarshal(alternativesRaw, &item.AlternativeExplanations); err != nil {
			return nil, err
		}
		if err := json.Unmarshal(limitationsRaw, &item.Limitations); err != nil {
			return nil, err
		}
		findings = append(findings, item)
	}
	return findings, rows.Err()
}

func (s *PostgresStore) Reviews() ([]model.Review, error) {
	rows, err := s.db.Query(`
		SELECT finding_id, reviewer, decision, comment, created_at
		FROM expert_review
		ORDER BY created_at ASC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var reviews []model.Review
	for rows.Next() {
		var item model.Review
		var createdAt time.Time
		if err := rows.Scan(&item.FindingID, &item.Reviewer, &item.Decision, &item.Comment, &createdAt); err != nil {
			return nil, err
		}
		item.CreatedAt = createdAt.UTC().Format(time.RFC3339Nano)
		reviews = append(reviews, item)
	}
	if reviews == nil {
		reviews = []model.Review{}
	}
	return reviews, rows.Err()
}

func (s *PostgresStore) AddReview(review model.Review) error {
	allowed := map[string]bool{"acknowledged": true, "needs-more-data": true, "rejected": true, "corrected": true}
	if !allowed[review.Decision] {
		return errors.New("unsupported review decision")
	}
	_, err := s.db.Exec(
		`INSERT INTO expert_review (finding_id, reviewer, decision, comment, created_at) VALUES ($1,$2,$3,$4,$5)`,
		review.FindingID,
		review.Reviewer,
		review.Decision,
		review.Comment,
		time.Now().UTC(),
	)
	return err
}
