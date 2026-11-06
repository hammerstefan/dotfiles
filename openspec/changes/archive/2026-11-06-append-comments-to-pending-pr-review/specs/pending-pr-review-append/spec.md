## ADDED Requirements

### Requirement: Auto-detect a single matching pending review

The skill MUST filter the PR's reviews for entries where `user.login` exactly equals the authenticated login, `state` equals `PENDING`, the canonical `pull_request_url` matches the resolved pull request, and `commit_id` equals the resolved head SHA. From this candidate set, the skill MUST enter exactly one of three modes:

- create mode when the candidate set is empty,
- append mode when the candidate set contains exactly one review,
- refuse mode when the candidate set contains two or more reviews.

The decision MUST be made before any comment payload is built, so the validator, anchor text, and reviewer tooling see one consistent comment list in both create and append modes.

#### Scenario: Zero matching reviews routes to create mode
- **WHEN** the PR has no `PENDING` review owned by the authenticated user on the current head SHA
- **THEN** the skill creates a new pending review through REST `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews`

#### Scenario: Exactly one matching review routes to append mode
- **WHEN** the PR has exactly one `PENDING` review owned by the authenticated user on the current head SHA
- **THEN** the skill enters append mode and records the target review's numeric id and node id

#### Scenario: Two or more matching reviews refuse
- **WHEN** the PR has two or more `PENDING` reviews owned by the authenticated user on the current head SHA
- **THEN** the skill stops without mutation, lists each matching review id, and asks the user to delete the unwanted ones in the GitHub UI

#### Scenario: A pending review owned by another user does not match
- **WHEN** the PR has a `PENDING` review owned by a different login
- **THEN** that review is excluded from the candidate set and the skill never appends to it

#### Scenario: A pending review on a stale head SHA does not match
- **WHEN** the PR has a `PENDING` review owned by the authenticated user but `commit_id` differs from the current head SHA
- **THEN** that review is excluded from the candidate set and the skill never appends to it

### Requirement: Append mode uses GraphQL addPullRequestReviewThread

In append mode the skill MUST add each new comment through the GraphQL `addPullRequestReviewThread` mutation, sending one mutation per appended comment. The mutation input MUST carry the target review's `node_id` (not numeric id), `path`, `line`, `side`, `body`, and `subjectType: "LINE"`. When the comment covers a range, the input MUST also carry `startLine` and `startSide`. The skill MUST NOT use the deprecated `addPullRequestReviewComment` mutation. The skill MUST NOT call `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events`, `PUT /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}`, or `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}` while in append mode.

#### Scenario: A single-line comment is added through one mutation
- **WHEN** the appended comment list contains a single-line comment anchored at `path:line` on `side`
- **THEN** the skill sends one `addPullRequestReviewThread` mutation with `pullRequestReviewId`, `path`, `line`, `side`, `body`, and `subjectType: "LINE"`

#### Scenario: A range comment carries startLine and startSide
- **WHEN** the appended comment list contains a range comment with `start_line` and `start_side`
- **THEN** the mutation input also carries `startLine` equal to `start_line` and `startSide` equal to `start_side`

#### Scenario: Multiple appended comments are sent as multiple mutations
- **WHEN** the appended comment list contains more than one comment
- **THEN** the skill sends one `addPullRequestReviewThread` mutation per comment, in order, and treats each mutation's outcome independently

#### Scenario: The deprecated mutation is never used
- **WHEN** the skill is in append mode
- **THEN** it never sends an `addPullRequestReviewComment` mutation

### Requirement: Pre-mutation invariants

Before the first GraphQL mutation in append mode the skill MUST re-fetch the pull request and the target review and require all of:

- the PR's `head.sha` equals the recorded head SHA,
- the review's numeric id equals the recorded id,
- the review's `user.login` equals the authenticated login,
- the review's `state` equals `PENDING`,
- the review's `commit_id` equals the recorded head SHA,
- the review's canonical `pull_request_url` matches the resolved pull request,
- the review's `node_id` is present and well-formed.

If any check fails the skill MUST stop without mutation and report the actual state.

#### Scenario: A head SHA drift is refused before mutation
- **WHEN** the PR's head SHA has changed between the step-2 snapshot and the pre-mutation re-fetch
- **THEN** the skill stops without mutation and reports the recorded head SHA and the current head SHA

#### Scenario: A review whose state is no longer pending is refused before mutation
- **WHEN** the target review was `PENDING` at the step-2 snapshot but is submitted, dismissed, or deleted at the pre-mutation re-fetch
- **THEN** the skill stops without mutation and reports the current state

#### Scenario: A review owned by another user is refused before mutation
- **WHEN** the target review's `user.login` differs from the authenticated login at the pre-mutation re-fetch
- **THEN** the skill stops without mutation and reports the actual owner

### Requirement: Verification of appended and pre-existing comments

In append mode the skill MUST verify every requested appended comment against the live diff using the existing verifier, and MUST also verify that every pre-existing comment on the target review is unchanged from the snapshot taken before the first mutation. A pre-existing comment is unchanged when its `id`, `path`, `line`, `side`, `start_line`, `start_side`, and `body` all match the snapshot byte for byte.

#### Scenario: An appended comment that landed is reported as verified
- **WHEN** an `addPullRequestReviewThread` mutation returns a comment whose anchor and body match the request, and the live diff confirms the anchor
- **THEN** the skill reports that comment as appended and verified

#### Scenario: An appended comment that did not land is reported as unverified
- **WHEN** an `addPullRequestReviewThread` mutation returns a comment whose anchor or body differs from the request, or the live diff does not confirm the anchor
- **THEN** the skill stops and reports that comment as appended and unverified, naming the discrepancy

#### Scenario: A pre-existing comment that changed is reported as unexpected
- **WHEN** a pre-existing comment on the target review has a different id, path, line, side, start_line, start_side, or body from the pre-mutation snapshot
- **THEN** the skill stops and reports the changed comment by id, naming the field that changed

### Requirement: No recovery on a failed append

When verification fails in append mode the skill MUST stop, report what is verifiable, and MUST NOT attempt to delete the target review, delete any individual comment on it, retry the failed mutation, or recreate the review. The final response MUST name the appended comments that landed, the appended comments that did not, and the pre-existing comments that are unchanged or changed, so the user can decide whether to delete the review or revert comments in the GitHub UI.

#### Scenario: A failed append stops without further mutation
- **WHEN** any appended comment or any pre-existing comment fails verification
- **THEN** the skill makes no further API mutation and reports the actual remote state

#### Scenario: The target review is never deleted
- **WHEN** the skill is in append mode and verification fails
- **THEN** the skill never calls `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}`

#### Scenario: Individual comments are never deleted
- **WHEN** the skill is in append mode and verification fails
- **THEN** the skill never attempts to delete any individual comment, because no such API exists

### Requirement: Safety boundary preservation in append mode

The skill MUST continue to refuse to submit, approve, request changes, dismiss, or merge the target review in append mode. The skill MUST NOT modify the review's summary body, MUST NOT add replies to pre-existing comments, and MUST NOT touch reviews owned by other users.

#### Scenario: The review is never submitted
- **WHEN** the skill is in append mode
- **THEN** it never calls `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events`

#### Scenario: The review summary body is never updated
- **WHEN** the skill is in append mode
- **THEN** it never calls `PUT /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}`

#### Scenario: Pre-existing comments are not replied to
- **WHEN** the skill is in append mode and the user requests new comments
- **THEN** every appended comment has no `inReplyTo` parent and is a top-level thread on the target review
