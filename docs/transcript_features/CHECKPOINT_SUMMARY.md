# Transcript-feature checkpoint summary

- **Works:** Local Python extraction with the Loughran–McDonald financial
  dictionary; overall, management, management-prepared, management-Q&A, and
  analyst sentiment; positive/negative/uncertainty counts and proportions;
  congratulations flag; analyst question-mark count; and word counts.
- **Test data:** 20 fictional mini-call excerpts, complete for the measured
  speaker sections, matched to 20 synthetic event IDs. All 20 produce overall
  sentiment and analyst question counts.
  Separate tests verify incomplete and missing inputs retain null feature
  values. No real transcript text was accessed or processed.
- **Privacy and licensing:** The extractor makes no external AI/API calls.
  The dictionary is used locally under the authors' academic-research
  permission and is not included in the repository. Real transcript
  collection/retention rights remain to be verified per provider.
- **Not established:** The synthetic run does not validate accuracy on real
  earnings calls, demonstrate return predictiveness, or establish that a
  given provider's transcript format can be parsed without a source adapter.
- **Next:** Confirm the real transcript source and permitted local retention,
  normalize speaker turns, run the same event-keyed pipeline, inspect
  missing-section coverage, then share the separate feature CSV with Michelle
  for an agreed merge. Regression/holdout comparison belongs to Cammy's
  analysis workflow and should use the same events for both models.
