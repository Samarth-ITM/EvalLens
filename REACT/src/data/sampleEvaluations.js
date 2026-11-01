// Pre-loaded realistic sample evaluations for EvalLens

export const INITIAL_EVALUATIONS = [
  {
    id: "eval-001",
    title: "Distributed Edge Anomaly Detection: Architecture & Performance Evaluation",
    submission_type: "Technical Report",
    instructions: "Evaluate the submitted technical report focusing on methodology, telemetry results, and edge hardware trade-offs.",
    content_text: `# Distributed Edge Anomaly Detection: Architecture & Performance Evaluation\n\n## Abstract\nWe evaluate lightweight unsupervised anomaly detection on heterogeneous ARM edge clusters. Telemetry models were benchmarked across Raspberry Pi 4B and NVIDIA Jetson Nano under synthetic sensor fault injection.\n\n## Telemetry Results\nUnder fault injection scenarios (Table 2), isolation forests achieved 94.2% detection recall with 42ms median latency. Flash write cycles were reduced by 64% through write coalescing.\n\n## Edge Architecture Trade-Offs\nMemory consumption stabilized at 128 MB RAM per container node, ensuring zero thrashing across 72 hours continuous operation.`,
    word_count: 1338,
    status: "completed",
    created_at: "2026-11-01T14:20:00Z",
    criteria: [
      {
        id: "crit-1",
        name: "Methodology & Benchmark Rigor",
        max_marks: 5,
        description: "Clarity of experimental setup, hardware specifications, and baseline controls.",
        scoring_guidance: "Full marks requires explicit cluster hardware and fault injection parameters."
      },
      {
        id: "crit-2",
        name: "Telemetry Telemetry Results & Analysis",
        max_marks: 5,
        description: "Accuracy of detection metrics, latency profiles, and wear leveling data.",
        scoring_guidance: "Requires numeric citations for recall, latency, and memory footprint."
      },
      {
        id: "crit-3",
        name: "Architectural Feasibility & Flash Longevity",
        max_marks: 5,
        description: "Consideration of real-world edge hardware limitations and eMMC flash wear.",
        scoring_guidance: "Evaluate practical operational viability and flash reduction."
      }
    ],
    human_scores: {
      "crit-1": { score: 4.5, feedback: "Excellent setup description with clear hardware baseline." },
      "crit-2": { score: 4.5, feedback: "Specific numbers provided for recall (94.2%) and latency (42ms)." },
      "crit-3": { score: 4.0, feedback: "Write coalescing is well documented, but power consumption data was omitted." }
    },
    ai_scores: {
      "crit-1": {
        score: 4.5,
        rationale: "The experimental baseline cleanly outlines the ARM cluster nodes and fault injection methodology.",
        evidence_quote: "Telemetry models were benchmarked across Raspberry Pi 4B and NVIDIA Jetson Nano under synthetic sensor fault injection."
      },
      "crit-2": {
        score: 5.0,
        rationale: "Comprehensive numeric telemetry benchmarks are provided with exact metrics.",
        evidence_quote: "isolation forests achieved 94.2% detection recall with 42ms median latency."
      },
      "crit-3": {
        score: 4.0,
        rationale: "Strong focus on eMMC endurance and RAM bounds, though thermals are not reported.",
        evidence_quote: "Flash write cycles were reduced by 64% through write coalescing. Memory consumption stabilized at 128 MB RAM."
      }
    }
  },
  {
    id: "eval-002",
    title: "Supabase Cloud Database Schema & Row Level Security Policies",
    submission_type: "Code",
    instructions: "Audit PostgreSQL tables, foreign key constraints, and RLS policies for multi-tenant data isolation.",
    content_text: `-- Supabase Multi-Tenant Schema Verification\n\nCREATE TABLE organizations (\n  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n  name TEXT NOT NULL,\n  created_at TIMESTAMPTZ DEFAULT now()\n);\n\nCREATE TABLE audit_logs (\n  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,\n  action TEXT NOT NULL,\n  actor_id UUID NOT NULL,\n  created_at TIMESTAMPTZ DEFAULT now()\n);\n\nALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;\n\nCREATE POLICY "org_member_access" ON audit_logs\n  FOR SELECT\n  USING (auth.uid() IN (\n    SELECT user_id FROM organization_members WHERE org_id = audit_logs.org_id\n  ));`,
    word_count: 450,
    status: "completed",
    created_at: "2026-11-01T16:45:00Z",
    criteria: [
      {
        id: "crit-201",
        name: "Schema Design & Relational Integrity",
        max_marks: 5,
        description: "Correct primary keys, foreign keys, cascade deletes, and timestamp tracking.",
        scoring_guidance: "Verify foreign keys and cascade rules prevent orphaned records."
      },
      {
        id: "crit-202",
        name: "Row Level Security (RLS) Policy Soundness",
        max_marks: 5,
        description: "Enforcement of tenant isolation and prevention of unauthorized data leaks.",
        scoring_guidance: "Policy must verify membership in the owning tenant."
      }
    ],
    human_scores: {
      "crit-201": { score: 5.0, feedback: "UUIDs and foreign key cascade deletes are properly configured." },
      "crit-202": { score: 4.5, feedback: "Sound subquery for organization membership; index needed for org_member join." }
    },
    ai_scores: {
      "crit-201": {
        score: 5.0,
        rationale: "Relational constraints and cascade rules strictly enforce parent-child integrity.",
        evidence_quote: "org_id UUID REFERENCES organizations(id) ON DELETE CASCADE"
      },
      "crit-202": {
        score: 4.5,
        rationale: "RLS policy restricts read queries to authorized organization members.",
        evidence_quote: "USING (auth.uid() IN (SELECT user_id FROM organization_members WHERE org_id = audit_logs.org_id))"
      }
    }
  }
];

