from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from ..models.fix import Fix
from ..models.review import Review
from ..models.user import User


def get_stats(db: Session, user: User):
    reviews = db.query(Review).filter(Review.user_id == user.id).order_by(Review.created_at.desc()).all()
    fixes = db.query(Fix).filter(Fix.user_id == user.id).order_by(Fix.created_at.desc()).all()

    findings = 0
    severity = {"high": 0, "medium": 0, "low": 0}
    category = {"bug": 0, "security": 0, "bad_practice": 0}
    repo_findings = {}
    for review in reviews:
        for finding in review.findings:
            findings += 1
            severity[finding["severity"]] = severity.get(finding["severity"], 0) + 1
            category[finding["category"]] = category.get(finding["category"], 0) + 1
            repo_findings[review.repo] = repo_findings.get(review.repo, 0) + 1

    fix_status = {"pending": 0, "approved": 0, "rejected": 0}
    prs_opened = 0
    ci_passed = 0
    ci_failed = 0
    for fix in fixes:
        fix_status[fix.status] = fix_status.get(fix.status, 0) + 1
        if fix.pr_url:
            prs_opened += 1
        if fix.ci_status == "passed":
            ci_passed += 1
        if fix.ci_status == "failed":
            ci_failed += 1

    top_repos = sorted(repo_findings.items(), key=lambda item: item[1], reverse=True)[:5]

    reviewed_repos = set()
    for review in reviews:
        reviewed_repos.add(review.repo)

    return {
        "reviews": len(reviews),
        "repos": len(reviewed_repos),
        "findings": findings,
        "fixes": len(fixes),
        "prs_opened": prs_opened,
        "ci_passed": ci_passed,
        "ci_failed": ci_failed,
        "severity": severity,
        "category": category,
        "fix_status": fix_status,
        "top_repos": [{"repo": repo, "findings": count} for repo, count in top_repos],
        "last_14_days": count_days(reviews, fixes),
        "recent": recent_activity(reviews, fixes),
    }


def count_days(reviews: list[Review], fixes: list[Fix]):
    today = datetime.now(timezone.utc).date()
    days = []
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        days.append({
            "day": day.isoformat(),
            "reviews": sum(1 for r in reviews if r.created_at.astimezone(timezone.utc).date() == day),
            "fixes": sum(1 for f in fixes if f.created_at.astimezone(timezone.utc).date() == day),
        })
    return days


def recent_activity(reviews: list[Review], fixes: list[Fix]):
    items = []
    for review in reviews[:8]:
        items.append({
            "kind": "review",
            "repo": review.repo,
            "pr_number": review.pr_number,
            "title": review.pr_title,
            "status": f"{len(review.findings)} findings",
            "created_at": review.created_at,
        })
    for fix in fixes[:8]:
        items.append({
            "kind": "fix",
            "repo": fix.repo,
            "pr_number": fix.pr_number,
            "title": fix.title,
            "status": fix.ci_status or fix.status,
            "created_at": fix.created_at,
        })

    items.sort(key=lambda item: item["created_at"], reverse=True)
    return items[:8]
