from claw_envs.post_mails import PostMailsEnvironment


def test_sessions_are_isolated(tmp_path) -> None:
    env = PostMailsEnvironment(state_root=tmp_path)
    env.create_session("session_a", "orbital_launch")
    env.create_session("session_b", "orbital_launch")

    env.read_email("session_a", "em_004")
    env.publish_post(
        "session_a",
        platform="x",
        content="Orbital Note launches June 18 with team workspaces. Join the waitlist.",
    )

    session_a = env.session_summary("session_a")
    session_b = env.session_summary("session_b")

    assert session_a["unread_email_count"] == session_b["unread_email_count"] - 1
    assert session_a["agent_post_count"] == 1
    assert session_b["agent_post_count"] == 0


def test_evaluate_session_rewards_complete_flow(tmp_path) -> None:
    env = PostMailsEnvironment(state_root=tmp_path)
    env.create_session("good_flow", "orbital_launch")

    env.read_email("good_flow", "em_004")
    env.read_attachment("good_flow", "att_orbital_brief_v3")
    env.publish_post(
        "good_flow",
        platform="x",
        content="Orbital Note launches June 18 with team workspaces for async briefs. Join the waitlist.",
    )
    env.publish_post(
        "good_flow",
        platform="reddit",
        title="Orbital Note launches June 18 for async brief teams",
        community="r/productivity",
        content=(
            "Orbital Note launches June 18 with a template gallery for recurring briefs, "
            "team workspaces, and a waitlist for the rollout."
        ),
    )
    env.reply_to_post(
        "good_flow",
        post_id="x_003",
        content="Team workspaces are in scope, Android is not at launch, and the waitlist is now open.",
    )
    env.reply_to_post(
        "good_flow",
        post_id="rdt_002",
        content="The template gallery is included at launch, and the waitlist is open for the rollout.",
    )

    result = env.evaluate_session("good_flow")

    assert result["read_score"] == 1.0
    assert result["post_score"] == 1.0
    assert result["reply_score"] == 1.0
    assert result["order_ok"] is True
    assert result["overall_score"] == 1.0


def test_outdated_claims_are_penalized(tmp_path) -> None:
    env = PostMailsEnvironment(state_root=tmp_path)
    env.create_session("bad_flow", "orbital_launch")

    env.publish_post(
        "bad_flow",
        platform="x",
        content="Orbital Note launches June 11 and Android app ships on launch day.",
    )

    result = env.evaluate_session("bad_flow")

    assert result["read_score"] == 0.0
    assert result["overall_score"] < 0.5
    assert result["forbidden_hits_total"]
