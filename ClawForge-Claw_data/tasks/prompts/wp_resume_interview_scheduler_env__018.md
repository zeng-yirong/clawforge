From: hr@company.com
To: ai-assistant@internal
Subject: 紧急：Senior Data Engineer 岗位面试安排

Hi 助手，

我们正在急招一名 Senior Data Engineer，岗位要求已经整理在 `data/jobs/jobs.json` 里（job_id: job_001）。候选人资料在 `data/candidates/candidates.json` 文件夹下，都是最新的简历摘要。我需要你帮忙做两件事：

1. 从候选人中找出一个完全满足该岗位所有必需技能的人（必须每个技能都覆盖，别给我推荐缺斤少两的）。
2. 为这位候选人创建一个面试邀请文件，放到 `ops/interview_invite.json` 里。格式如下：
   - 包含候选人ID（candidate_id）、岗位ID（job_id）、面试时间（我看了日历，下周三下午2点空着，就定 **2025-03-11T14:00:00**）。
   - 地点定在 **Room 301**，备注写 **Please confirm with candidate.**

注意：除了 `ops/` 目录下的这个新文件，不要改动工作区里任何其他文件。数据里可能有些旧的历史记录或干扰项，但请以 `data/candidates/candidates.json` 和 `data/jobs/jobs.json` 为准。谢谢！

-- HR
