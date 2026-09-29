"""
verify_coverage.py
------------------
Generates the Course Coverage Report for SkillPath AI.
Verifies that:
- Total required topics are 100% accounted for (all 26 topics)
- Every single topic has at least one verified available, watchable video
- Unavailable videos are automatically replaced with valid alternatives
- Missing topics = 0
"""

import sys
import asyncio
from datetime import datetime
from video_validator import VideoValidator
from data import TOPICS

async def main():
    print("=" * 80)
    print("           SKILLPATH AI — COURSE VIDEO AVAILABILITY & COVERAGE REPORT")
    print("=" * 80)
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print(f"Total topics in syllabus registry: {len(TOPICS)}")
    print("-" * 80)

    report = await VideoValidator.generate_coverage_report()

    print(f"\nCourse: {report['course']}")
    print(f"Total required topics:          {report['total_required_topics']}")
    print(f"Topics covered:                  {report['topics_covered']}")
    print(f"Topics with available videos:    {report['topics_with_available_videos']}")
    print(f"Unavailable videos replaced:     {report['unavailable_videos_replaced']}")
    print(f"Missing topics:                  {report['missing_topics']}")
    print(f"Course Coverage Percentage:      {report['coverage_percentage']}%")
    print(f"Target Achieved (Missing = 0):   {report['target_achieved']}")

    print("\n" + "=" * 80)
    print("                      DETAILED TOPIC COVERAGE BREAKDOWN")
    print("=" * 80)
    print(f"{'Topic':<30} | {'Status':<10} | {'Video ID':<12} | {'Verified Title'}")
    print("-" * 80)

    for item in report["topics"]:
        topic_name = item["topic"]
        status = item["status"]
        vid_id = item.get("video_id", "N/A")
        title = item.get("video_title", "N/A")
        if len(title) > 36:
            title = title[:33] + "..."
        print(f"{topic_name:<30} | {status:<10} | {vid_id:<12} | {title}")

    print("=" * 80)
    if report["missing_topics"] == 0:
        print("✓ SUCCESS: 100% Course Coverage Verified! Every required topic has watchable content.")
        sys.exit(0)
    else:
        print(f"❌ FAILURE: {report['missing_topics']} topic(s) lack available video content!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
