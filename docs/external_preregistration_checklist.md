# External preregistration checklist

The live audit must not begin until an OSF or AsPredicted registration has been submitted and its permanent URL has been recorded.

## Recommended route: OSF

OSF is the preferred option because a public registration is frozen, timestamped, and assigned a DOI.

1. Sign in to OSF.
2. Open **My Registrations** and select **Add a Registration**.
3. Start from scratch or from an OSF project.
4. Choose the **OSF Preregistration** template or the **AsPredicted Preregistration** template.
5. Copy the relevant material from [`osf_preregistration.md`](osf_preregistration.md).
6. Confirm that no live model response has been requested or viewed.
7. Attach or link the locked configuration and preregistration files if desired.
8. Review every field. A submitted registration and its attached files cannot be edited in place.
9. Submit publicly for an immediate public record and DOI, or use an embargo if confidentiality is necessary.
10. Save the permanent registration URL and DOI.

## Faster alternative: AsPredicted

1. Sign in to AsPredicted.
2. Create a new preregistration.
3. Copy the eight answers from [`aspredicted_preregistration.md`](aspredicted_preregistration.md).
4. Review and submit before any live request.
5. Save the timestamped PDF and permanent verification URL.

## Record the registration in the project

After submission:

1. Replace the `PENDING` fields in the relevant preregistration document.
2. Add the URL and submission date to `docs/deviations_from_preregistration.md` as a prospective record, not a deviation.
3. Set the environment variable:

```bash
export EXTERNAL_PREREGISTRATION_URL="https://osf.io/xxxxx"
```

4. Run the test suite.
5. Start the live core audit only after the registration URL is accepted by the runner.

## Final pre-run checklist

- [ ] External registration submitted before the first live API request
- [ ] Permanent OSF or AsPredicted URL saved
- [ ] Exact model ID locked
- [ ] Prompt version locked
- [ ] Temperature locked at 0.0
- [ ] 128 resumes regenerated from the committed configuration
- [ ] 640 planned evaluations confirmed
- [ ] No treatment-specific execution blocks
- [ ] No selective reruns permitted
- [ ] API credentials absent from Git and shell history where practicable
- [ ] Repository commit SHA recorded with the registration
