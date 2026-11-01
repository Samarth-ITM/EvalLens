// Scoring and comparison mathematics for EvalLens

/**
 * Calculates comparative statistics between human and AI scores
 *
 * @param {Array} criteria - List of rubric criteria
 * @param {Object} humanScores - Map of criterionId -> { score, feedback }
 * @param {Object} aiScores - Map of criterionId -> { score, rationale, evidence_quote }
 */
export function calculateComparison(criteria = [], humanScores = {}, aiScores = {}) {
  let humanTotal = 0;
  let aiTotal = 0;
  let maxTotal = 0;
  
  let validPairs = 0;
  let absErrorSum = 0;
  let rawDiffSum = 0;
  let closeMatches = 0;

  const criterionComparisons = criteria.map((c) => {
    const h = humanScores[c.id];
    const a = aiScores[c.id];

    const hScore = h && typeof h.score === 'number' ? h.score : null;
    const aScore = a && typeof a.score === 'number' ? a.score : null;

    if (hScore !== null) humanTotal += hScore;
    if (aScore !== null) aiTotal += aScore;
    maxTotal += c.max_marks;

    let delta = null;
    let normalizedErrorPct = null;
    let isClose = false;

    if (hScore !== null && aScore !== null && c.max_marks > 0) {
      validPairs++;
      delta = Number((aScore - hScore).toFixed(2));
      rawDiffSum += delta;
      
      const pctDiff = Math.abs(delta) / c.max_marks;
      normalizedErrorPct = Number((pctDiff * 100).toFixed(1));
      absErrorSum += pctDiff;

      if (normalizedErrorPct <= 10.0) {
        closeMatches++;
        isClose = true;
      }
    }

    return {
      criterionId: c.id,
      name: c.name,
      description: c.description,
      maxMarks: c.max_marks,
      humanScore: hScore,
      aiScore: aScore,
      humanFeedback: h?.feedback || '',
      aiReason: a?.reason || a?.rationale || '',
      aiCritic: a?.critic || '',
      aiRationale: a?.rationale || a?.reason || '',
      evidenceQuote: a?.evidence_quote || '',
      delta,
      normalizedErrorPct,
      isClose
    };
  });

  const maePct = validPairs > 0 ? Number(((absErrorSum / validPairs) * 100).toFixed(2)) : null;
  const directionalBias = validPairs > 0 ? Number((rawDiffSum / validPairs).toFixed(2)) : null;
  const agreementRatePct = validPairs > 0 ? Number(((closeMatches / validPairs) * 100).toFixed(1)) : null;

  let alignmentCategory = 'Pending';
  if (maePct !== null) {
    if (maePct <= 10.0) alignmentCategory = 'Strong Agreement';
    else if (maePct <= 25.0) alignmentCategory = 'Moderate Agreement';
    else alignmentCategory = 'Significant Divergence';
  }

  const humanPct = maxTotal > 0 ? Number(((humanTotal / maxTotal) * 100).toFixed(1)) : 0;
  const aiPct = maxTotal > 0 ? Number(((aiTotal / maxTotal) * 100).toFixed(1)) : 0;

  return {
    humanTotal: Number(humanTotal.toFixed(1)),
    aiTotal: Number(aiTotal.toFixed(1)),
    maxTotal,
    humanPct,
    aiPct,
    maePct,
    directionalBias,
    agreementRatePct,
    alignmentCategory,
    criterionComparisons
  };
}

