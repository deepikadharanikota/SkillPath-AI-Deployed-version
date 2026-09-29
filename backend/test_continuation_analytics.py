import asyncio
import json
import httpx

BACKEND_URL = "http://localhost:8000"

async def main():
    from redis_client import redis_client as r
    keys = await r.keys("session:*")
    print(f"Active sessions in Redis: {keys}")
    if not keys:
        print("No active session found in Redis!")
        return
    token = keys[0].replace("session:", "")
    user_id = await r.get(keys[0])
    print(f"Using token: {token} for user_id: {user_id}")

    headers = {"token": token}

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Test 1: GET /learning/resume
        res_resume = await client.get(f"{BACKEND_URL}/learning/resume", headers=headers)
        print(f"GET /learning/resume status: {res_resume.status_code}")
        assert res_resume.status_code == 200, res_resume.text
        data_resume = res_resume.json()
        print("Resume response keys:", list(data_resume.keys()))
        print("Continue course:", data_resume.get("continue_course"))
        print("Next recommended course:", data_resume.get("next_course"))
        print("Learning path steps:", len(data_resume.get("learning_path", [])))
        print("All topics count:", len(data_resume.get("all_topics", [])))

        # Test 2: POST /learning/position
        pos_payload = {
            "topic": "Docker",
            "module": "intro",
            "video_id": "https://www.youtube.com/watch?v=fqMOX6JJhGo",
            "video_title": "Docker Fundamentals Introduction",
            "position_seconds": 165.5
        }
        res_pos = await client.post(f"{BACKEND_URL}/learning/position", headers=headers, json=pos_payload)
        print(f"POST /learning/position status: {res_pos.status_code}")
        assert res_pos.status_code == 200, res_pos.text
        data_pos = res_pos.json()
        print("Saved position response:", data_pos)
        assert data_pos["position_seconds"] == 165.5
        assert data_pos["video_id"] == "https://www.youtube.com/watch?v=fqMOX6JJhGo"

        # Test 3: Verify GET /learning/resume now returns the exact continuation!
        res_resume2 = await client.get(f"{BACKEND_URL}/learning/resume", headers=headers)
        data_resume2 = res_resume2.json()
        cont = data_resume2.get("continue_course")
        print("Updated continuation course:", cont)
        assert cont is not None, "continue_course should not be None after setting position"
        assert cont["topic"] == "Docker"
        assert cont["position_seconds"] == 165.5
        assert "fqMOX6JJhGo" in cont["action_url"]
        assert "t=165" in cont["action_url"]

        # Test 4: GET /dashboard/overview
        res_ov = await client.get(f"{BACKEND_URL}/dashboard/overview", headers=headers)
        assert res_ov.status_code == 200, res_ov.text
        data_ov = res_ov.json()
        print("Dashboard overview:", {
            "target_role": data_ov.get("target_role"),
            "role_readiness_pct": data_ov.get("role_readiness_pct"),
            "continue_course": data_ov.get("continue_course"),
            "overall_progress": data_ov.get("overall_progress")
        })
        assert "role_readiness_pct" in data_ov
        assert data_ov.get("continue_course") is not None

        # Test 5: GET /dashboard/skills
        res_sk = await client.get(f"{BACKEND_URL}/dashboard/skills", headers=headers)
        assert res_sk.status_code == 200, res_sk.text
        data_sk = res_sk.json()
        print("Dashboard skills summary:", data_sk.get("summary"))
        cat = data_sk.get("categorized", {})
        print("Known skills count:", len(cat.get("known", [])))
        print("Learning skills count:", len(cat.get("learning", [])))
        print("Needs improvement skills count:", len(cat.get("needs_improvement", [])))
        print("Missing skills count:", len(cat.get("missing", [])))
        if cat.get("known"):
            print("Sample Known skill:", cat["known"][0]["topic"], "| Evidence:", cat["known"][0]["evidence"])
        if cat.get("learning"):
            print("Sample Learning skill:", cat["learning"][0]["topic"], "| Evidence:", cat["learning"][0]["evidence"])
        if cat.get("missing"):
            print("Sample Missing skill:", cat["missing"][0]["topic"], "| Evidence:", cat["missing"][0]["evidence"])

        # Test 6: GET /dashboard/quiz-analysis
        res_qa = await client.get(f"{BACKEND_URL}/dashboard/quiz-analysis", headers=headers)
        assert res_qa.status_code == 200, res_qa.text
        data_qa = res_qa.json()
        print("Dashboard quiz analysis:", {
            "has_quiz_data": data_qa.get("has_quiz_data"),
            "total_quizzes_taken": data_qa.get("total_quizzes_taken"),
            "average_quiz_score": data_qa.get("average_quiz_score"),
            "strengths_count": len(data_qa.get("strengths", [])),
            "weaknesses_count": len(data_qa.get("weaknesses", []))
        })

        print("\nALL BACKEND TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
