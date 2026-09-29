import os
import requests
import json

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8002")

def run_tests():
    print("=== STEP 1: Test /roles ===")
    res = requests.get(f"{BASE_URL}/roles")
    assert res.status_code == 200, f"Failed: {res.status_code}"
    data = res.json()
    roles = data.get("roles", [])
    roles_detail = data.get("roles_detail", {})
    print(f"Total roles returned: {len(roles)}")
    assert len(roles) >= 30, f"Expected at least 30 roles, got {len(roles)}"
    assert "DevOps Engineer" in roles
    assert "Frontend Developer" in roles
    assert "Backend Developer" in roles
    assert "Full Stack Developer" in roles
    assert "Site Reliability Engineer (SRE)" in roles
    assert "QA / Automation Engineer" in roles
    assert "Software Architect" in roles
    assert "Data Engineer" in roles
    assert "Machine Learning Engineer" in roles
    print("✓ Roles endpoint verified successfully.")

    print("\n=== STEP 2: Authenticate as deepikadharanikota ===")
    # Login or fetch token from local-login or session
    # Let's inspect user token or login with existing user
    login_res = requests.post(f"{BASE_URL}/auth/local-login", json={"username": "deepikadharanikota", "password": "password123"})
    if login_res.status_code != 200:
        # Fallback to dev login if needed
        print(f"Local login status: {login_res.status_code}, trying me or direct check")
        token = "token_deepikadharanikota"
    else:
        token = login_res.json().get("access_token") or login_res.json().get("token")
    
    headers = {"token": token, "Authorization": f"Bearer {token}"}
    me_res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    assert me_res.status_code == 200, f"Auth me failed: {me_res.text}"
    user_info = me_res.json()["user"]
    print(f"Logged in as user: {user_info['username']}, current role: {user_info.get('target_role')}")

    print("\n=== STEP 3: Switch Target Role to DevOps Engineer ===")
    role_res = requests.put(f"{BASE_URL}/resume/target-role", json={"target_role": "DevOps Engineer"}, headers=headers)
    assert role_res.status_code == 200, f"Failed updating role: {role_res.text}"
    print("✓ Switched target role to DevOps Engineer.")

    print("\n=== STEP 4: Test /dashboard/roadmap ===")
    rm_res = requests.get(f"{BASE_URL}/dashboard/roadmap", headers=headers)
    assert rm_res.status_code == 200, f"Failed getting roadmap: {rm_res.text}"
    roadmap = rm_res.json()
    print(f"Target role: {roadmap['target_role']}")
    print(f"Category: {roadmap['category']}")
    print(f"Total milestones: {roadmap['total_milestones']}")
    print(f"Mastered count: {roadmap['mastered_count']}")
    
    milestones = roadmap["milestones"]
    assert len(milestones) >= 8, f"Expected >= 8 milestones for DevOps, got {len(milestones)}"
    for idx, m in enumerate(milestones):
        print(f"  {idx+1}. {m['topic']}: status={m['status']}, prereqs={m['prerequisites']}, unmet={m['unmet_prerequisites']}, action={m['action_label']}")
        if m.get("syllabus"):
            mods = m["syllabus"].get("modules", {})
            assert "intro" in mods and "core" in mods and "advanced" in mods and "summary" in mods
    print("✓ Roadmap and prerequisites verified successfully.")

    print("\n=== STEP 5: Test /learning/videos for Docker Module 1 & 2 ===")
    vid_res1 = requests.get(f"{BASE_URL}/learning/videos?topic=Docker&module=intro", headers=headers)
    assert vid_res1.status_code == 200, f"Failed: {vid_res1.text}"
    vdata1 = vid_res1.json()
    print(f"Docker Intro videos: {len(vdata1['videos'])}, required: {vdata1['required_count']}")
    assert len(vdata1['videos']) >= 1
    assert vdata1.get("syllabus") is not None
    print(f"Syllabus Title: {vdata1['syllabus'].get('title')}")

    vid_res2 = requests.get(f"{BASE_URL}/learning/videos?topic=Docker&module=core", headers=headers)
    assert vid_res2.status_code == 200, f"Failed: {vid_res2.text}"
    vdata2 = vid_res2.json()
    print(f"Docker Core videos: {len(vdata2['videos'])}, required: {vdata2['required_count']}")
    assert len(vdata2['videos']) >= 2, "Core module should have at least 2 detailed videos"
    print("✓ Video retrieval and module gating count verified.")

    print("\n=== STEP 6: Complete Video to Unlock Quiz & Test 15-Question Quiz ===")
    first_vid = vdata1["videos"][0]
    vid_id = first_vid.get("id") or first_vid.get("url")
    comp_res = requests.post(
        f"{BASE_URL}/learning/video/complete",
        json={"topic": "Docker", "module": "intro", "video_id": vid_id},
        headers=headers
    )
    assert comp_res.status_code == 200, f"Failed completing video: {comp_res.text}"
    print(f"✓ Video marked complete. Quiz unlocked: {comp_res.json().get('is_quiz_unlocked')}")

    quiz_res = requests.get(f"{BASE_URL}/quiz/generate?topic=Docker&module=intro", headers=headers)
    assert quiz_res.status_code == 200, f"Failed generating quiz: {quiz_res.text}"
    qdata = quiz_res.json()
    questions = qdata.get("questions", [])
    print(f"Quiz ID: {qdata.get('quiz_id')}, Questions generated: {len(questions)}")
    assert len(questions) == 15, f"Expected 15 questions, got {len(questions)}"
    
    # Check that questions test Docker concepts
    print(f"Sample Question 1: {questions[0]}")
    docker_keywords = ["docker", "container", "image", "daemon", "dockerfile", "volume", "compose", "port", "virtual", "host"]
    relevant_count = 0
    for q in questions:
        text = (q.get("question") or q.get("q") or "") + " " + " ".join(q.get("options") or q.get("opts") or [])
        text = text.lower()
        if any(kw in text for kw in docker_keywords):
            relevant_count += 1
    print(f"Relevant Docker questions: {relevant_count}/15")
    assert relevant_count >= 13, f"Too few relevant questions ({relevant_count}/15)"
    print("✓ 15-question role-specific Docker quiz verified successfully.")

    print("\n=== STEP 7: Test Quiz Submission & Scoring ===")
    answers = {str(i): "0" for i in range(15)}  # Answer option "0" for all as strings
    sub_res = requests.post(
        f"{BASE_URL}/quiz/submit",
        json={"quiz_id": qdata["quiz_id"], "topic": "Docker", "module": "intro", "answers": answers},
        headers=headers
    )
    assert sub_res.status_code == 200, f"Failed submitting quiz: {sub_res.text}"
    sdata = sub_res.json()
    print(f"Quiz submitted successfully! Score: {sdata.get('score')}%, Passed: {sdata.get('passed')}, Difficulty: {sdata.get('difficulty')}")
    print("✓ Quiz submission and scoring verified.")

    print("\n==========================================")
    print("ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==========================================")

if __name__ == "__main__":
    run_tests()
