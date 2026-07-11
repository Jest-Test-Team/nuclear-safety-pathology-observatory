package model

type Finding struct {
	FindingID               string         `json:"finding_id"`
	RuleID                  string         `json:"rule_id"`
	FindingType             string         `json:"finding_type"`
	Status                  string         `json:"status"`
	CreatedAt               string         `json:"created_at"`
	Scope                   map[string]any `json:"scope"`
	SupportingEvidence      []string       `json:"supporting_evidence"`
	MissingEvidence         []string       `json:"missing_evidence"`
	AlternativeExplanations []string       `json:"alternative_explanations"`
	Limitations             []string       `json:"limitations"`
	Uncertainty             float64        `json:"uncertainty"`
	Synthetic               bool           `json:"synthetic"`
}

type Review struct {
	FindingID string `json:"finding_id"`
	Decision  string `json:"decision"`
	Reviewer  string `json:"reviewer"`
	Comment   string `json:"comment"`
	CreatedAt string `json:"created_at"`
}
